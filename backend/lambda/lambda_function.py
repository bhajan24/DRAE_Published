
"""
Lambda Function for University Application Processing System
Handles various student application operations including document extraction,
evaluation, report generation, and application management.
"""

import logging
import traceback

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

version = "0.2"

def lambda_handler(event, context):
    """
    Main Lambda handler for processing university application events.
    
    Args:
        event (dict): Lambda event containing Records with eventSource and action
        context: Lambda context object
        
    Returns:
        dict: Response with status code and result
    """
    try:
        logger.info(f"Lambda version: {version}")
        logger.info(f"Received event: {event}")
        
        # Validate event structure
        records = event.get("Records")
        if not records:
            logger.error("No records found in event")
            return return_output(400, "Malformed input: Missing Records", error_output=True)
        
        if not isinstance(records, list) or len(records) == 0:
            logger.error("Records is not a valid list or is empty")
            return return_output(400, "Malformed input: Invalid Records format", error_output=True)
        
        record = records[0]

        #----------------------------------------------------------------------------------------#
        # S3 event
        if record.get("eventSource") == "aws:s3":
            print("S3 Put event")
            from s3_event import event_actions
            status, output = event_actions(record)
    
            if not status:
                return return_output(400, output, error_output = True) 
    
            return return_output(200, output)

        
        # Validate record structure
        if not isinstance(record, dict):
            logger.error("Record is not a valid dictionary")
            return return_output(400, "Invalid record format", error_output=True)
        
        event_source = record.get("eventSource")
        if not event_source:
            logger.error("No eventSource found in record")
            return return_output(400, "Invalid event: Missing eventSource", error_output=True)
        
        # Process student application events
        if event_source == "student-application":
            logger.info(f"Processing {event_source} event")
            
            try:
                from student_application import student_actions
                status, output = student_actions(record)
                
                if not status:
                    logger.error(f"Student action failed: {output}")
                    return return_output(400, output, error_output=True)
                
                logger.info("Student action completed successfully")
                return return_output(200, output)
                
            except ImportError as e:
                logger.error(f"Failed to import student_application module: {e}")
                return return_output(500, "Internal error: Module import failed", error_output=True)
            except Exception as e:
                logger.error(f"Error in student_actions: {e}")
                logger.error(traceback.format_exc())
                return return_output(500, f"Internal error: {str(e)}", error_output=True)
        
        # Handle unknown event sources
        else:
            logger.warning(f"Unknown event source: {event_source}")
            return return_output(404, f"Unknown event source: {event_source}", error_output=True)
    
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}")
        logger.error(traceback.format_exc())
        return return_output(500, "Internal server error", error_output=True)



def return_output(status_code, response, error_output=False):
    """
    Standardized response formatter for Lambda function.
    
    Args:
        status_code (int): HTTP status code
        response: Response data (can be dict, string, etc.)
        error_output (bool): Whether this is an error response
        
    Returns:
        dict: Formatted response with status code, result, and version
    """
    try:
        # Handle response override for state machine compatibility
        if isinstance(response, dict) and "response_override" in response:
            output = response["response"]
        else:
            output = {
                "status_code": status_code,
                "result": response,
                "version": version
            }
        
        if error_output:
            logger.error(f"Error response: {output}")
        else:
            logger.info(f"Success response: {output}")
        
        return output
        
    except Exception as e:
        logger.error(f"Error in return_output: {e}")
        # Fallback response if formatting fails
        return {
            "status_code": 500,
            "result": "Response formatting error",
            "version": version
        }
