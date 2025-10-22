"""
Student Application Processing Module
Handles various student application operations including document extraction,
evaluation, report generation, and application management.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

from aws_utils import (
    textractor_document_analysis, 
    dynamodb_put_item, 
    dynamodb_get_item, 
    invoke_agentcore_runtime, 
    dynamodb_get_all_items, 
    start_state_machine
)
from report_generation import ProfessionalAdmissionsReportGenerator
from wishlist_report_generation import StudentFeedbackReportGenerator
from config import config

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def student_actions(record: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Route student application actions to appropriate handlers.
    
    Args:
        record (dict): Event record containing action and input data
        
    Returns:
        tuple: (success: bool, result: Any)
    """
    try:
        action = record.get("action")
        if not action:
            logger.error("No action specified in record")
            return False, "Missing action parameter"
        
        logger.info(f"Processing student action: {action}")
        
        # Route to appropriate handler
        action_handlers = {
            "document_extraction": document_extraction_flow,
            "document_extraction_lite": document_extraction_lite_flow,
            "prepare_document_list": prepare_document_list_flow,
            "extract_single_document": extract_single_document_flow,
            "consolidate_extraction_results": consolidate_extraction_results_flow,
            "evaluate_application": evaluate_application_flow,
            "generate_report": generate_report_flow,
            "generate_student_feedback": generate_student_feedback_flow,
            "generate_wishlist_report": generate_wishlist_report_flow,
            "list_applicants": list_applicants_flow,
            "list_applicants_v2": list_applicants_v2_flow,
            "list_evaluations": list_evaluations_flow,
            "process_application": process_application_flow,
            "get_application": get_application_flow,
            "get_evaluation": get_evaluation_flow,
            "submit_application": submit_application_flow,
            "update_wishlist": update_wishlist_flow,
            "list_wishlist": list_wishlist_flow
        }
        
        handler = action_handlers.get(action)
        if not handler:
            logger.error(f"Unknown action: {action}")
            return False, f"Unknown action: {action}"
        
        # Execute handler with input data
        input_data = record.get("input", {})
        return handler(input_data)
        
    except Exception as e:
        logger.error(f"Error in student_actions: {e}")
        logger.error(traceback.format_exc())
        return False, f"Internal error: {str(e)}"



def get_evaluation_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Retrieve evaluation details for a specific application.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, evaluation_data: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in get_evaluation_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Retrieving evaluation for application: {application_id}")
        
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not student:
            logger.warning(f"No evaluation found for application: {application_id}")
            return False, f"No evaluation found for application: {application_id}"
        
        logger.info(f"Successfully retrieved evaluation for: {application_id}")
        return True, student
        
    except Exception as e:
        logger.error(f"Error in get_evaluation_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to retrieve evaluation: {str(e)}"


def submit_application_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Submit a new application to the applications table.
    
    Args:
        data (dict): Input data containing application_id and application_form
        
    Returns:
        tuple: (success: bool, result_message: str)
    """
    try:
        application_id = data.get("application_id")
        application_form = data.get("application_form")
        
        if not application_id:
            logger.error("Missing application_id in submit_application_flow")
            return False, "Missing application_id parameter"
        
        if not application_form:
            logger.error("Missing application_form in submit_application_flow")
            return False, "Missing application_form parameter"
        
        if not isinstance(application_form, dict):
            logger.error("application_form must be a valid JSON object")
            return False, "application_form must be a valid JSON object"
        
        logger.info(f"Submitting application for: {application_id}")
        
        # Create a copy to avoid modifying the original
        application_data = application_form.copy()
        
        # Add application_id if not present
        if "application_id" not in application_data:
            application_data["application_id"] = application_id
        
        # Add application_status
        application_data["application_status"] = "New"
        
        # Save to DynamoDB
        dynamodb_put_item(application_data, config["DYNAMO_DB"]["application_table_name"])
        
        logger.info(f"Successfully submitted application for: {application_id}")
        return True, f"Application {application_id} submitted successfully"
        
    except Exception as e:
        logger.error(f"Error in submit_application_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to submit application: {str(e)}"


def update_wishlist_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Update wishlist table with provided JSON data.
    
    Args:
        data (dict): Input data containing wishlist_data as JSON
        
    Returns:
        tuple: (success: bool, result_message: str)
    """
    try:
        wishlist_data = data.get("wishlist_data")
        
        if not wishlist_data:
            logger.error("Missing wishlist_data in update_wishlist_flow")
            return False, "Missing wishlist_data parameter"
        
        if not isinstance(wishlist_data, dict):
            logger.error("wishlist_data must be a valid JSON object")
            return False, "wishlist_data must be a valid JSON object"
        
        logger.info("Updating wishlist table")
        
        # Save to DynamoDB wishlist table
        dynamodb_put_item(wishlist_data, config["DYNAMO_DB"]["wishlist_table_name"])
        
        logger.info("Successfully updated wishlist")
        return True, "Wishlist updated successfully"
        
    except Exception as e:
        logger.error(f"Error in update_wishlist_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to update wishlist: {str(e)}"


def list_wishlist_flow(data: Dict[str, Any] = None) -> Tuple[bool, Any]:
    """
    Retrieve all items from the wishlist table.
    
    Args:
        data (dict, optional): Input data (currently unused, for consistency)
    
    Returns:
        tuple: (success: bool, wishlist_items: list)
    """
    try:
        logger.info("Retrieving all wishlist items")
        
        status, all_items = dynamodb_get_all_items(
            config["DYNAMO_DB"]["wishlist_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve wishlist items: {all_items}")
            return False, "Failed to retrieve wishlist items"
        
        logger.info(f"Successfully retrieved {len(all_items)} wishlist items")
        return True, all_items
        
    except Exception as e:
        logger.error(f"Error in list_wishlist_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to list wishlist items: {str(e)}"


def get_application_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Retrieve application details for a specific application.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, application_data: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in get_application_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Retrieving application details for: {application_id}")
        
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.warning(f"No application found for: {application_id}")
            return False, f"No application found for application: {application_id}"
        
        logger.info(f"Successfully retrieved application for: {application_id}")
        return True, student
        
    except Exception as e:
        logger.error(f"Error in get_application_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to retrieve application: {str(e)}"


def process_application_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Initiate complete application processing workflow.
    Starts state machine for document extraction -> evaluation -> report generation.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, result_message: str)
    """
    try:
        logger.info("Initiating application processing workflow")
        
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in process_application_flow")
            return False, "Missing application_id parameter"
        
        # Prepare input for state machine
        try:
            input_data = json.dumps({"application_id": application_id})
        except Exception as e:
            logger.error(f"Failed to serialize input data: {e}")
            return False, "Invalid application data format"
        
        # Get current application record
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.error(f"Application not found: {application_id}")
            return False, f"Application not found: {application_id}"
        
        # Start state machine execution (use parallel version if available)
        step_function_arn = config["PROCESS"].get(
            "application_processing_parallel_sm", 
            config["PROCESS"]["application_processing_sm"]
        )
        
        status, output = start_state_machine(step_function_arn, input_data)
        
        if not status:
            logger.error(f"Failed to start state machine: {output}")
            # Update application status to on-hold
            student["application_status"] = "On-hold"
            dynamodb_put_item(student, config["DYNAMO_DB"]["application_table_name"])
            return False, f"Failed to start processing: {output}"
        
        # Update application status to processing
        student["application_status"] = "Application processing"
        dynamodb_put_item(student, config["DYNAMO_DB"]["application_table_name"])
        
        logger.info(f"Successfully started processing for application: {application_id}")
        return True, "Application processing initiated successfully"
        
    except Exception as e:
        logger.error(f"Error in process_application_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to process application: {str(e)}"
    


def list_evaluations_flow(data: Dict[str, Any] = None) -> Tuple[bool, Any]:
    """
    Retrieve all evaluation records from the database.
    
    Args:
        data (dict, optional): Input data (currently unused, for consistency)
    
    Returns:
        tuple: (success: bool, evaluations_list: list)
    """
    try:
        logger.info("Retrieving all evaluation records")
        
        status, all_students = dynamodb_get_all_items(
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve evaluations: {all_students}")
            return False, "Failed to retrieve evaluation records"
        
        logger.info(f"Successfully retrieved {len(all_students)} evaluation records")
        return True, all_students
        
    except Exception as e:
        logger.error(f"Error in list_evaluations_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to list evaluations: {str(e)}"


def list_applicants_flow(data: Dict[str, Any] = None) -> Tuple[bool, Any]:
    """
    Retrieve all application records from the database.
    
    Args:
        data (dict, optional): Input data (currently unused, for consistency)
    
    Returns:
        tuple: (success: bool, applications_list: list)
    """
    try:
        logger.info("Retrieving all application records")
        
        status, all_students = dynamodb_get_all_items(
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve applications: {all_students}")
            return False, "Failed to retrieve application records"
        
        logger.info(f"Successfully retrieved {len(all_students)} application records")
        return True, all_students
        
    except Exception as e:
        logger.error(f"Error in list_applicants_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to list applicants: {str(e)}"


def list_applicants_v2_flow(data: Dict[str, Any] = None) -> Tuple[bool, Any]:
    """
    Retrieve combined application and evaluation data with configurable fields.
    
    Args:
        data (dict, optional): Input data containing optional field configurations
        
    Returns:
        tuple: (success: bool, combined_applicants_list: list)
    """
    try:
        logger.info("Retrieving combined application and evaluation records")
        
        # Default fields to extract with correct nested paths
        default_app_fields = {
            "application_id": "application_id",
            "documents": "documents", 
            "full_name": "personal_information.full_name",
            "specialization": "program_specific.specialization",
            "application_status": "application_status",
            "submitted_date": "submitted_date"
        }
        
        default_eval_fields = {
            "composite_score": "level4_Result.composite_score",
            "confidence_level": "level4_Result.confidence_level", 
            "final_decision": "level4_Result.final_decision",
            "report": "report"
        }
        
        # Get configurable fields from input data
        input_data = data or {}
        app_fields = input_data.get("application_fields", default_app_fields)
        eval_fields = input_data.get("evaluation_fields", default_eval_fields)
        
        # Get all applications
        status, applications = dynamodb_get_all_items(
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve applications: {applications}")
            return False, "Failed to retrieve application records"
        
        # Get all evaluations
        status, evaluations = dynamodb_get_all_items(
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve evaluations: {evaluations}")
            return False, "Failed to retrieve evaluation records"
        
        # Create evaluation lookup by application_id
        eval_lookup = {eval_record.get("application_id"): eval_record for eval_record in evaluations}
        
        # Helper function to get nested field value
        def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
            """Get value from nested dictionary using dot notation path"""
            try:
                keys = path.split('.')
                current = obj
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                return current
            except Exception:
                return None
        
        # Combine data
        combined_records = []
        for app in applications:
            app_id = app.get("application_id")
            combined_record = {}
            
            # Extract application fields (handle both string paths and direct field names)
            if isinstance(app_fields, dict):
                for field_name, field_path in app_fields.items():
                    combined_record[field_name] = get_nested_value(app, field_path)
            else:
                # Backward compatibility - if list provided, use default mapping
                for field in app_fields:
                    if field in default_app_fields:
                        combined_record[field] = get_nested_value(app, default_app_fields[field])
                    else:
                        combined_record[field] = app.get(field)
            
            # Extract evaluation fields (blank if not available)
            eval_record = eval_lookup.get(app_id, {})
            if isinstance(eval_fields, dict):
                for field_name, field_path in eval_fields.items():
                    combined_record[field_name] = get_nested_value(eval_record, field_path)
            else:
                # Backward compatibility - if list provided, use default mapping
                for field in eval_fields:
                    if field in default_eval_fields:
                        combined_record[field] = get_nested_value(eval_record, default_eval_fields[field])
                    else:
                        combined_record[field] = eval_record.get(field)
            
            combined_records.append(combined_record)
        
        logger.info(f"Successfully combined {len(combined_records)} application records with evaluation data")
        return True, combined_records
        
    except Exception as e:
        logger.error(f"Error in list_applicants_v2_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to list combined applicants: {str(e)}"


def generate_report_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Generate comprehensive admissions report for evaluated application.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, report_info: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in generate_report_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Starting report generation for application: {application_id}")
        
        # Get evaluation data
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not student:
            logger.error(f"No evaluation found for application: {application_id}")
            return False, f"No evaluation data found for application: {application_id}"
        
        # Get original application data for enhanced context
        app_data = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        # Merge application context into evaluation data
        if app_data:
            student["application_context"] = {
                "documents": {k: v for k, v in app_data.items() if k.endswith('_content')},
                "metadata": {k: v for k, v in app_data.items() if k in ['submission_date', 'last_updated', 'document_count']}
            }
        
        # Get all evaluations for cohort comparison
        status, all_students = dynamodb_get_all_items(
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not status:
            logger.error(f"Failed to retrieve cohort data: {all_students}")
            return False, "Failed to retrieve cohort data for comparison"
        
        # Get S3 configuration
        s3_bucket = config["REPORTS"]["save_bucket"]
        s3_prefix = config["REPORTS"]["save_key"]
        
        # Initialize report generator
        generator = ProfessionalAdmissionsReportGenerator(
            student_data=student,
            all_applicants=all_students,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix
        )
        
        logger.info("Generating HTML report")
        
        # Generate and upload report
        s3_key = f"{s3_prefix}/{application_id}/report.html"
        result = generator.generate_html_report(s3_key=s3_key)
        
        if not result.get('upload', {}).get('success', False):
            logger.error(f"Report upload failed: {result}")
            return False, f"Failed to upload report: {result.get('upload', {}).get('message', 'Unknown error')}"

        # Update evaluation record with report location
        report_url = f"s3://{s3_bucket}/{s3_key}"
        student["report"] = report_url
        dynamodb_put_item(student, config["DYNAMO_DB"]["evaluations_table_name"])
        
        # Update application status
        app_student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if app_student:
            app_student["application_status"] = "Processing complete"
            dynamodb_put_item(app_student, config["DYNAMO_DB"]["application_table_name"])
        
        logger.info(f"Report generation completed successfully for: {application_id}")
        
        return True, {
            "application_id": application_id,
            "report": report_url,
            "upload_details": result.get('upload', {})
        }
        
    except Exception as e:
        logger.error(f"Error in generate_report_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to generate report: {str(e)}"


def generate_student_feedback_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Generate student feedback report for evaluated application.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, feedback_report_info: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in generate_student_feedback_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Starting student feedback report generation for application: {application_id}")
        
        # Get evaluation data
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not student:
            logger.error(f"No evaluation found for application: {application_id}")
            return False, f"No evaluation data found for application: {application_id}"
        
        # Get S3 configuration
        s3_bucket = config["REPORTS"]["save_bucket"]
        s3_prefix = config["REPORTS"]["save_key"]
        
        # Initialize student feedback report generator
        generator = StudentFeedbackReportGenerator(
            student_data=student,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix
        )
        
        logger.info("Generating student feedback HTML report")
        
        # Generate and upload feedback report
        feedback_s3_key = f"{s3_prefix}/{application_id}/student_feedback.html"
        result = generator.generate_html_report(s3_key=feedback_s3_key)
        
        if not result.get('upload', {}).get('success', False):
            logger.error(f"Student feedback report upload failed: {result}")
            return False, f"Failed to upload student feedback report: {result.get('upload', {}).get('message', 'Unknown error')}"
        
        # Update wishlist table with feedback report location and status
        feedback_report_url = f"s3://{s3_bucket}/{feedback_s3_key}"
        w_student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["wishlist_table_name"]
        )
        
        if w_student:
            w_student["feedback_report"] = feedback_report_url
            w_student["status"] = student.get("level4_Result", {}).get("final_decision", "PENDING")
            dynamodb_put_item(w_student, config["DYNAMO_DB"]["wishlist_table_name"])
            logger.info(f"Updated wishlist record with feedback report for: {application_id}")
        else:
            logger.warning(f"No wishlist record found for application: {application_id}")
        
        logger.info(f"Student feedback report generation completed successfully for: {application_id}")
        
        return True, {
            "application_id": application_id,
            "feedback_report": feedback_report_url,
            "upload_details": result.get('upload', {})
        }
        
    except Exception as e:
        logger.error(f"Error in generate_student_feedback_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to generate student feedback report: {str(e)}"


def generate_wishlist_report_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Generate wishlist report for a specific evaluated application.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, wishlist_report_info: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in generate_wishlist_report_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Starting wishlist report generation for application: {application_id}")
        
        # Get evaluation data
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["evaluations_table_name"]
        )
        
        if not student:
            logger.error(f"No evaluation found for application: {application_id}")
            return False, f"No evaluation data found for application: {application_id}"
        
        # Get original application data for enhanced context
        app_data = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        # Merge application context into evaluation data
        if app_data:
            student["application_context"] = {
                "documents": {k: v for k, v in app_data.items() if k.endswith('_content')},
                "metadata": {k: v for k, v in app_data.items() if k in ['submission_date', 'last_updated', 'document_count']}
            }
        
        # Get S3 configuration
        s3_bucket = config["REPORTS"]["save_bucket"]
        s3_prefix = config["REPORTS"]["save_key"]
        
        # Initialize wishlist report generator with evaluation data
        generator = StudentFeedbackReportGenerator(
            student_data=student,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix
        )
        
        logger.info("Generating wishlist HTML report")
        
        # Generate and upload wishlist report
        s3_key = f"{s3_prefix}/{application_id}/wishlist_report.html"
        result = generator.generate_html_report(s3_key=s3_key)
        
        if not result.get('upload', {}).get('success', False):
            logger.error(f"Wishlist report upload failed: {result}")
            return False, f"Failed to upload wishlist report: {result.get('upload', {}).get('message', 'Unknown error')}"
        
        # Update wishlist table with report location
        wishlist_report_url = f"s3://{s3_bucket}/{s3_key}"
        w_student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["wishlist_table_name"]
        )
        
        if w_student:
            w_student["report"] = wishlist_report_url
            w_student["status"] = student.get("level4_Result", {}).get("final_decision", "PENDING")
            dynamodb_put_item(w_student, config["DYNAMO_DB"]["wishlist_table_name"])
        
        logger.info(f"Wishlist report generation completed successfully for: {application_id}")
        
        return True, {
            "application_id": application_id,
            "wishlist_report": wishlist_report_url,
            "upload_details": result.get('upload', {})
        }
        
    except Exception as e:
        logger.error(f"Error in generate_wishlist_report_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to generate wishlist report: {str(e)}"
    

def evaluate_application_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Evaluate application using AI agent for comprehensive analysis.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, evaluation_result: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in evaluate_application_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Starting application evaluation for: {application_id}")
        
        # Get application data
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.error(f"Application not found: {application_id}")
            return False, f"Application not found: {application_id}"
        
        # Prepare data for evaluation (remove status to avoid bias)
        eval_data = student.copy()
        eval_data.pop("application_status", None)
        
        # Create evaluation prompt
        prompt = f"""Perform level 1-4 analysis and scoring for the following application details and provide the aggregated evaluation result:
{eval_data}

Note: If the content is blank for any field it means the document was not provided.
Ensure you do not fabricate any values or hallucinate.
Skip the preamble."""
        
        logger.info("Invoking AI agent for evaluation")
        
        # Invoke AI agent for evaluation
        status, response = invoke_agentcore_runtime(prompt)
        
        if not status:
            logger.error(f"AI agent evaluation failed: {response}")
            return False, f"Evaluation service failed: {response}"
        
        if not response or not isinstance(response, dict):
            logger.error("Invalid response from AI agent")
            return False, "Invalid evaluation response from AI service"
        
        # Add application_id to response
        response["application_id"] = application_id
        
        logger.info(f"Evaluation completed successfully for: {application_id}")
        
        # Update application status
        student["application_status"] = "Generating report"
        dynamodb_put_item(student, config["DYNAMO_DB"]["application_table_name"])
        
        # Save evaluation results
        dynamodb_put_item(response, config["DYNAMO_DB"]["evaluations_table_name"])
        
        return True, {"application_id": application_id}
        
    except Exception as e:
        logger.error(f"Error in evaluate_application_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to evaluate application: {str(e)}"
    

def parse_s3_uri(s3_uri: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse S3 URI to extract bucket and key components.
    
    Args:
        s3_uri (str): S3 URI in format s3://bucket-name/key/path
    
    Returns:
        tuple: (bucket_name: str|None, key: str|None)
    """
    try:
        if not s3_uri or not isinstance(s3_uri, str) or not s3_uri.startswith("s3://"):
            return None, None
        
        # Remove s3:// prefix
        path = s3_uri[5:]
        
        if not path:
            return None, None
        
        # Split bucket and key
        parts = path.split('/', 1)
        bucket = parts[0] if parts[0] else None
        key = parts[1] if len(parts) > 1 and parts[1] else ""
        
        return bucket, key
        
    except Exception as e:
        logger.error(f"Error parsing S3 URI '{s3_uri}': {e}")
        return None, None


def document_extraction_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Extract text content from all documents in the application.
    Documents are stored as S3 URIs in format: s3://bucket-name/path/to/file.pdf
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, extraction_results: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in document_extraction_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Starting document extraction for application: {application_id}")
        
        # Load application
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.error(f"Application not found: {application_id}")
            return False, f"Application not found: {application_id}"
        
        # Track extraction status
        extraction_results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
        
        def extract_document(s3_uri: str, field_name: str) -> Optional[str]:
            """Helper function to extract text from document using S3 URI"""
            try:
                if not s3_uri or s3_uri == "":
                    logger.info(f"Skipping empty path: {field_name}")
                    extraction_results["skipped"].append(field_name)
                    return None
                
                # Parse S3 URI
                bucket_name, s3_key = parse_s3_uri(s3_uri)
                
                if not bucket_name or not s3_key:
                    logger.error(f"Invalid S3 URI for {field_name}: {s3_uri}")
                    extraction_results["failed"].append(field_name)
                    return ""
                
                logger.info(f"Extracting: {field_name} from s3://{bucket_name}/{s3_key}")
                
                # Perform extraction
                status, result = textractor_document_analysis(bucket_name, s3_key)
                
                if status == "SUCCEEDED":
                    extraction_results["successful"].append(field_name)
                    logger.info(f"Successfully extracted: {field_name}")
                    return result
                else:
                    extraction_results["failed"].append(field_name)
                    logger.error(f"Failed to extract {field_name}: {result}")
                    return ""
                    
            except Exception as e:
                logger.error(f"Error extracting {field_name}: {e}")
                extraction_results["failed"].append(field_name)
                return ""
        
        # Process main documents section
        if "documents" in student:
            _extract_main_documents(student, extract_document)
        
        # Process nested documents in other sections
        _extract_nested_documents(student, extract_document)
        
        # Update application status
        student["application_status"] = "Evaluation in-progress"
        
        # Save updated student record to DynamoDB
        try:
            dynamodb_put_item(student, config["DYNAMO_DB"]["application_table_name"])
            logger.info(f"Saved updated record to DynamoDB for: {application_id}")
        except Exception as e:
            logger.error(f"Failed to save to DynamoDB: {e}")
            return False, f"Failed to save extracted content: {str(e)}"
        
        # Log summary
        logger.info(f"Document extraction completed - Success: {len(extraction_results['successful'])}, "
                   f"Failed: {len(extraction_results['failed'])}, Skipped: {len(extraction_results['skipped'])}")
        
        return True, {
            "application_id": application_id,
            "result": extraction_results,
            "summary": {
                "successful": len(extraction_results['successful']),
                "failed": len(extraction_results['failed']),
                "skipped": len(extraction_results['skipped'])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in document_extraction_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to extract documents: {str(e)}"


def document_extraction_lite_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Extract text content from a single S3 document without application context.
    
    Args:
        data (dict): Input data containing s3_bucket and s3_key
        
    Returns:
        tuple: (success: bool, extracted_text: str or error_message: str)
    """
    try:
        s3_bucket = data.get("s3_bucket")
        s3_key = data.get("s3_key")
        
        if not s3_bucket:
            logger.error("Missing s3_bucket in document_extraction_lite_flow")
            return False, "Missing s3_bucket parameter"
        
        if not s3_key:
            logger.error("Missing s3_key in document_extraction_lite_flow")
            return False, "Missing s3_key parameter"
        
        logger.info(f"Starting lite document extraction for s3://{s3_bucket}/{s3_key}")
        
        # Perform text extraction using existing methodology
        status, result = textractor_document_analysis(s3_bucket, s3_key)
        
        if status == "SUCCEEDED":
            logger.info(f"Successfully extracted text from s3://{s3_bucket}/{s3_key}")
            return True, result
        else:
            logger.error(f"Failed to extract text from s3://{s3_bucket}/{s3_key}: {result}")
            return False, f"Text extraction failed: {result}"
            
    except Exception as e:
        logger.error(f"Error in document_extraction_lite_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to extract document: {str(e)}"

        
def _extract_main_documents(student: Dict[str, Any], extract_document) -> None:
    """
    Extract content from main documents section.
    
    Args:
        student (dict): Student application data
        extract_document: Function to extract document content
    """
    try:
        docs = student.get("documents", {})
        if not docs:
            logger.info("No documents section found")
            return
        
        # Document mapping for main documents
        document_mapping = {
            "transcript": "transcript_content",
            "sop": "sop_content", 
            "resume": "resume_content",
            "lor_academic": "lor_academic_content",
            "lor_research": "lor_research_content",
            "lor_professional": "lor_professional_content",
            "passport": "passport_content",
            "gre_report": "gre_report_content",
            "english_report": "english_report_content",
            "degree_certificate": "degree_certificate_content",
            "bank_statement": "bank_statement_content",
            "affidavit": "affidavit_content",
            "fee_receipt": "fee_receipt_content",
            "writing_sample": "writing_sample_content",
            "portfolio": "portfolio_content",
            "research_proposal": "research_proposal_content",
            "publication_certificate": "publication_certificate_content",
            "internship_certificate": "internship_certificate_content",
            "work_certificate": "work_certificate_content",
            "recommendation_letter_additional": "recommendation_letter_additional_content"
        }
        
        # Process all documents
        for doc_key, content_key in document_mapping.items():
            if doc_key in docs:
                s3_uri = docs[doc_key]
                extracted_content = extract_document(s3_uri, doc_key)
                
                # Store extracted content in the student object
                if extracted_content is not None:
                    student[content_key] = extracted_content
                    
    except Exception as e:
        logger.error(f"Error extracting main documents: {e}")


def prepare_document_list_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Prepare list of documents for parallel processing.
    
    Args:
        data (dict): Input data containing application_id
        
    Returns:
        tuple: (success: bool, document_list: dict)
    """
    try:
        application_id = data.get("application_id")
        if not application_id:
            logger.error("Missing application_id in prepare_document_list_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Preparing document list for application: {application_id}")
        
        # Load application
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.error(f"Application not found: {application_id}")
            return False, f"Application not found: {application_id}"
        
        documents = []
        
        # Main documents
        if "documents" in student:
            docs = student["documents"]
            document_mapping = {
                "transcript": "transcript_content",
                "sop": "sop_content",
                "resume": "resume_content",
                "lor_academic": "lor_academic_content",
                "lor_research": "lor_research_content",
                "lor_professional": "lor_professional_content",
                "passport": "passport_content",
                "gre_report": "gre_report_content",
                "english_report": "english_report_content",
                "degree_certificate": "degree_certificate_content",
                "bank_statement": "bank_statement_content",
                "affidavit": "affidavit_content",
                "fee_receipt": "fee_receipt_content",
                "writing_sample": "writing_sample_content",
                "portfolio": "portfolio_content",
                "research_proposal": "research_proposal_content",
                "publication_certificate": "publication_certificate_content",
                "internship_certificate": "internship_certificate_content",
                "work_certificate": "work_certificate_content",
                "recommendation_letter_additional": "recommendation_letter_additional_content"
            }
            
            for doc_key, content_key in document_mapping.items():
                if doc_key in docs and docs[doc_key]:
                    documents.append({
                        "application_id": application_id,
                        "document_type": "main",
                        "document_key": doc_key,
                        "content_key": content_key,
                        "s3_uri": docs[doc_key]
                    })
        
        # Nested documents
        if "personal_information" in student:
            personal_info = student["personal_information"]
            if "government_id_document" in personal_info and personal_info["government_id_document"]:
                documents.append({
                    "application_id": application_id,
                    "document_type": "nested",
                    "document_key": "personal_information.government_id_document",
                    "content_key": "government_id_content",
                    "s3_uri": personal_info["government_id_document"],
                    "parent_path": "personal_information"
                })
        
        # Research documents
        if "research_experience" in student:
            research_exp = student["research_experience"]
            projects = research_exp.get("projects", [])
            
            for idx, project in enumerate(projects):
                if "publication_document" in project and project["publication_document"]:
                    documents.append({
                        "application_id": application_id,
                        "document_type": "nested",
                        "document_key": f"research_experience.projects[{idx}].publication_document",
                        "content_key": "publication_content",
                        "s3_uri": project["publication_document"],
                        "parent_path": f"research_experience.projects.{idx}"
                    })
                
                if "report_document" in project and project["report_document"]:
                    documents.append({
                        "application_id": application_id,
                        "document_type": "nested",
                        "document_key": f"research_experience.projects[{idx}].report_document",
                        "content_key": "report_content",
                        "s3_uri": project["report_document"],
                        "parent_path": f"research_experience.projects.{idx}"
                    })
        
        # Work experience documents
        if "work_experience" in student:
            work_experiences = student["work_experience"]
            
            for idx, work in enumerate(work_experiences):
                if "certificate_document" in work and work["certificate_document"]:
                    documents.append({
                        "application_id": application_id,
                        "document_type": "nested",
                        "document_key": f"work_experience[{idx}].certificate_document",
                        "content_key": "certificate_content",
                        "s3_uri": work["certificate_document"],
                        "parent_path": f"work_experience.{idx}"
                    })
                
                if "recommendation_document" in work and work["recommendation_document"]:
                    documents.append({
                        "application_id": application_id,
                        "document_type": "nested",
                        "document_key": f"work_experience[{idx}].recommendation_document",
                        "content_key": "recommendation_content",
                        "s3_uri": work["recommendation_document"],
                        "parent_path": f"work_experience.{idx}"
                    })
        
        logger.info(f"Prepared {len(documents)} documents for parallel processing")
        
        return True, {
            "application_id": application_id,
            "documents": documents,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error in prepare_document_list_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to prepare document list: {str(e)}"


def extract_single_document_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Extract content from a single document.
    
    Args:
        data (dict): Input data containing application_id and document info
        
    Returns:
        tuple: (success: bool, extraction_result: dict)
    """
    try:
        application_id = data.get("application_id")
        document = data.get("document")
        
        if not application_id or not document:
            logger.error("Missing application_id or document in extract_single_document_flow")
            return False, "Missing required parameters"
        
        s3_uri = document.get("s3_uri")
        document_key = document.get("document_key")
        
        logger.info(f"Extracting single document: {document_key} for application: {application_id}")
        
        # Parse S3 URI
        bucket_name, s3_key = parse_s3_uri(s3_uri)
        
        if not bucket_name or not s3_key:
            logger.error(f"Invalid S3 URI for {document_key}: {s3_uri}")
            return True, {
                "application_id": application_id,
                "document": document,
                "status": "failed",
                "error": "Invalid S3 URI",
                "content": ""
            }
        
        # Perform extraction
        status, result = textractor_document_analysis(bucket_name, s3_key)
        
        if status == "SUCCEEDED":
            logger.info(f"Successfully extracted: {document_key}")
            return True, {
                "application_id": application_id,
                "document": document,
                "status": "success",
                "content": result
            }
        else:
            logger.error(f"Failed to extract {document_key}: {result}")
            return True, {
                "application_id": application_id,
                "document": document,
                "status": "failed",
                "error": str(result),
                "content": ""
            }
            
    except Exception as e:
        logger.error(f"Error in extract_single_document_flow: {e}")
        logger.error(traceback.format_exc())
        return True, {
            "application_id": data.get("application_id"),
            "document": data.get("document", {}),
            "status": "failed",
            "error": str(e),
            "content": ""
        }


def consolidate_extraction_results_flow(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Consolidate parallel extraction results and update application.
    
    Args:
        data (dict): Input data containing application_id and extraction_results
        
    Returns:
        tuple: (success: bool, consolidation_result: dict)
    """
    try:
        application_id = data.get("application_id")
        extraction_results = data.get("extraction_results", [])
        
        if not application_id:
            logger.error("Missing application_id in consolidate_extraction_results_flow")
            return False, "Missing application_id parameter"
        
        logger.info(f"Consolidating extraction results for application: {application_id}")
        
        # Load application
        student = dynamodb_get_item(
            "application_id",
            application_id,
            config["DYNAMO_DB"]["application_table_name"]
        )
        
        if not student:
            logger.error(f"Application not found: {application_id}")
            return False, f"Application not found: {application_id}"
        
        # Track results
        successful = 0
        failed = 0
        skipped = 0
        
        # Process each extraction result
        for result_wrapper in extraction_results:
            result = result_wrapper.get("Payload", {}).get("result", {})
            
            if result.get("status") == "success":
                successful += 1
                document = result.get("document", {})
                content = result.get("content", "")
                
                # Store content based on document type
                if document.get("document_type") == "main":
                    content_key = document.get("content_key")
                    if content_key:
                        student[content_key] = content
                
                elif document.get("document_type") == "nested":
                    parent_path = document.get("parent_path", "")
                    content_key = document.get("content_key")
                    
                    if "personal_information" in parent_path:
                        if "personal_information" not in student:
                            student["personal_information"] = {}
                        student["personal_information"][content_key] = content
                    
                    elif "research_experience.projects" in parent_path:
                        path_parts = parent_path.split(".")
                        if len(path_parts) >= 3:
                            idx = int(path_parts[2])
                            if "research_experience" in student and "projects" in student["research_experience"]:
                                if idx < len(student["research_experience"]["projects"]):
                                    student["research_experience"]["projects"][idx][content_key] = content
                    
                    elif "work_experience" in parent_path:
                        path_parts = parent_path.split(".")
                        if len(path_parts) >= 2:
                            idx = int(path_parts[1])
                            if "work_experience" in student:
                                if idx < len(student["work_experience"]):
                                    student["work_experience"][idx][content_key] = content
            
            elif result.get("status") == "failed":
                failed += 1
            else:
                skipped += 1
        
        # Update application status
        student["application_status"] = "Evaluation in-progress"
        
        # Save updated student record
        dynamodb_put_item(student, config["DYNAMO_DB"]["application_table_name"])
        
        logger.info(f"Consolidation completed - Success: {successful}, Failed: {failed}, Skipped: {skipped}")
        
        return True, {
            "application_id": application_id,
            "summary": {
                "successful": successful,
                "failed": failed,
                "skipped": skipped,
                "total": len(extraction_results)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in consolidate_extraction_results_flow: {e}")
        logger.error(traceback.format_exc())
        return False, f"Failed to consolidate results: {str(e)}"


def _extract_nested_documents(student: Dict[str, Any], extract_document) -> None:
    """
    Extract content from nested documents in other sections.
    
    Args:
        student (dict): Student application data
        extract_document: Function to extract document content
    """
    try:
        # Personal Information - Government ID
        personal_info = student.get("personal_information", {})
        if "government_id_document" in personal_info:
            s3_uri = personal_info["government_id_document"]
            content = extract_document(s3_uri, "personal_information.government_id")
            if content is not None:
                personal_info["government_id_content"] = content
        
        # Research Experience - Publications and Reports
        research_exp = student.get("research_experience", {})
        projects = research_exp.get("projects", [])
        
        for idx, project in enumerate(projects):
            # Publication document
            if "publication_document" in project:
                s3_uri = project["publication_document"]
                content = extract_document(
                    s3_uri,
                    f"research_experience.projects[{idx}].publication"
                )
                if content is not None:
                    project["publication_content"] = content
            
            # Report document
            if "report_document" in project:
                s3_uri = project["report_document"]
                content = extract_document(
                    s3_uri,
                    f"research_experience.projects[{idx}].report"
                )
                if content is not None:
                    project["report_content"] = content
        
        # Work Experience - Certificates and Recommendations
        work_experiences = student.get("work_experience", [])
        
        for idx, work in enumerate(work_experiences):
            # Certificate
            if "certificate_document" in work:
                s3_uri = work["certificate_document"]
                content = extract_document(
                    s3_uri,
                    f"work_experience[{idx}].certificate"
                )
                if content is not None:
                    work["certificate_content"] = content
            
            # Recommendation
            if "recommendation_document" in work:
                s3_uri = work["recommendation_document"]
                content = extract_document(
                    s3_uri,
                    f"work_experience[{idx}].recommendation"
                )
                if content is not None:
                    work["recommendation_content"] = content
                    
    except Exception as e:
        logger.error(f"Error extracting nested documents: {e}")