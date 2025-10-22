"""
AWS Utilities Module
Provides functions for interacting with AWS services including DynamoDB,
Step Functions, Bedrock Agent Runtime, and Textractor.
"""

import json
import logging
import traceback
from typing import Any, Dict, Tuple, List, Optional
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from config import config
from utils import DecimalEncoder

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# AWS region configuration
region_name = config["AWS"]["region_name"]


def start_state_machine(state_machine_arn: str, run_input: str) -> Tuple[bool, str]:
    """
    Start AWS Step Functions state machine execution.
    
    Args:
        state_machine_arn (str): ARN of the state machine to execute
        run_input (str): JSON string input for the state machine
        
    Returns:
        tuple: (success: bool, execution_arn_or_error: str)
    """
    try:
        if not state_machine_arn:
            logger.error("State machine ARN is required")
            return False, "State machine ARN is required"
        
        if not run_input:
            logger.error("Input data is required for state machine")
            return False, "Input data is required"
        
        logger.info(f"Starting state machine: {state_machine_arn}")
        
        stepfunctions_client = boto3.client("stepfunctions", region_name=region_name)
        response = stepfunctions_client.start_execution(
            stateMachineArn=state_machine_arn, 
            input=run_input
        )
        
        execution_arn = response["executionArn"]
        logger.info(f"State machine started successfully: {execution_arn}")
        return True, execution_arn
        
    except ClientError as err:
        error_msg = f"AWS error starting state machine: {err.response['Error']['Code']} - {err.response['Error']['Message']}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error starting state machine: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg


def dynamodb_get_all_items(table_name: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Retrieve all items from a DynamoDB table using scan operation.
    
    Args:
        table_name (str): Name of the DynamoDB table
        
    Returns:
        tuple: (success: bool, items: list or error_message: str)
    """
    try:
        if not table_name:
            logger.error("Table name is required")
            return False, "Table name is required"
        
        logger.info(f"Scanning all items from table: {table_name}")
        
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        table = dynamodb.Table(table_name)
        
        items = []
        response = table.scan()
        items.extend(response.get('Items', []))

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
    
        logger.info(f"Successfully retrieved {len(items)} items from {table_name}")
        return True, items
        
    except ClientError as e:
        error_message = f"DynamoDB error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(f"Error retrieving all items from {table_name}: {error_message}")
        return False, error_message
    except Exception as e:
        error_message = f"Unexpected error retrieving items: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        return False, error_message


def convert_floats_to_decimal(obj: Any) -> Any:
    """
    Recursively convert all float values to Decimal for DynamoDB compatibility.
    
    Args:
        obj: Any Python object (dict, list, float, etc.)
    
    Returns:
        Object with floats converted to Decimal
    """
    try:
        if isinstance(obj, list):
            return [convert_floats_to_decimal(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
        elif isinstance(obj, float):
            # Convert float to Decimal
            return Decimal(str(obj))
        else:
            return obj
    except Exception as e:
        logger.error(f"Error converting floats to decimal: {e}")
        return obj


def dynamodb_put_item(item: Dict[str, Any], table_name: str) -> bool:
    """
    Save item to DynamoDB with automatic float to Decimal conversion.
    
    Args:
        item (dict): Item to save to DynamoDB
        table_name (str): Name of the DynamoDB table
        
    Returns:
        bool: True if successful, raises exception if failed
    """
    try:
        if not item:
            logger.error("Item data is required")
            raise ValueError("Item data is required")
        
        if not table_name:
            logger.error("Table name is required")
            raise ValueError("Table name is required")
        
        logger.info(f"Saving item to table: {table_name}")
        
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        dynamo_metadata_table = dynamodb.Table(table_name)
        
        # Convert floats to Decimal
        converted_item = convert_floats_to_decimal(item)
        
        dynamo_metadata_table.put_item(Item=converted_item)
        logger.info(f"Successfully saved item to {table_name}")
        return True
        
    except ClientError as e:
        error_msg = f"DynamoDB error saving item: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error saving item to DynamoDB: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise Exception(error_msg)
    


def invoke_agentcore_runtime(prompt: str, 
                             agentcore_runtimearn: str = None, 
                             qualifier: str = None) -> Tuple[bool, Any]:
    """
    Invoke Bedrock Agent Runtime for AI-powered analysis.
    
    Args:
        prompt (str): The prompt to send to the agent
        agentcore_runtimearn (str, optional): Agent runtime ARN (uses config default if None)
        qualifier (str, optional): Agent qualifier (uses config default if None)
        
    Returns:
        tuple: (success: bool, response_data: dict or error_message: str)
    """
    try:
        if not prompt:
            logger.error("Prompt is required for agent invocation")
            return False, "Prompt is required"
        
        # Use config defaults if not provided
        if not agentcore_runtimearn:
            agentcore_runtimearn = config["AGENTS"]["uni_application_analyst"]["agentcore_arn"]
        if not qualifier:
            qualifier = config["AGENTS"]["uni_application_analyst"]["qualifier"]
        
        logger.info(f"Invoking Bedrock agent: {agentcore_runtimearn}")
        
        client = boto3.client('bedrock-agentcore', region_name=region_name)
        payload = json.dumps({"prompt": prompt})
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agentcore_runtimearn,
            payload=payload,
            qualifier=qualifier
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info("Successfully invoked Bedrock agent")
        return True, response_data
        
    except ClientError as e:
        error_msg = f"Bedrock agent error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        return False, error_msg
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON response from agent: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error invoking Bedrock agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg
    

def textractor_document_analysis(bucket_name: str, s3_object_key: str) -> Tuple[str, str]:
    """
    Extract text from documents using AWS Textractor service.
    
    Args:
        bucket_name (str): S3 bucket name containing the document
        s3_object_key (str): S3 object key/path to the document
        
    Returns:
        tuple: (status: str, extracted_text: str or error_message: str)
    """
    try:
        if not bucket_name:
            logger.error("S3 bucket name is required")
            return "FAILED", "S3 bucket name is required"
        
        if not s3_object_key:
            logger.error("S3 object key is required")
            return "FAILED", "S3 object key is required"
        
        logger.info(f"Starting document analysis for s3://{bucket_name}/{s3_object_key}")
        
        from textractor import Textractor
        from textractor.data.constants import TextractFeatures
        from textractor.data.text_linearization_config import TextLinearizationConfig
        
        extractor = Textractor(region_name=region_name)
        config_obj = TextLinearizationConfig(
            table_linearization_format="markdown",
            selection_element_selected="[X]",
            selection_element_not_selected="[]",
            signature_token="[SIGNATURE]"
        )

        document = extractor.start_document_analysis(
            file_source=f"s3://{bucket_name}/{s3_object_key}",
            features=[
                TextractFeatures.LAYOUT, 
                TextractFeatures.TABLES, 
                TextractFeatures.FORMS, 
                TextractFeatures.SIGNATURES
            ],
            save_image=False
        )
        
        extracted_text = document.get_text(config_obj)
        logger.info(f"Successfully extracted text from document (length: {len(extracted_text)})")
        return "SUCCEEDED", extracted_text
    
    except ImportError as e:
        error_msg = f"Textractor library not available: {str(e)}"
        logger.error(error_msg)
        return "FAILED", error_msg
    except ClientError as e:
        error_msg = f"AWS error during text extraction: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        return "FAILED", error_msg
    except Exception as e:
        error_msg = f"Error during text extraction: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return "FAILED", error_msg


def dynamodb_get_item(id_key: str, id_value: str, table_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an item from DynamoDB by its ID and return it as a JSON-compatible object.
    
    Args:
        id_key (str): The key name for the item ID
        id_value (str): The value of the item ID
        table_name (str): Name of the DynamoDB table
        
    Returns:
        dict or None: The item data if found, None if not found
        
    Raises:
        Exception: If there's an error accessing DynamoDB
    """
    try:
        if not id_key:
            logger.error("ID key is required")
            raise ValueError("ID key is required")
        
        if not id_value:
            logger.error("ID value is required")
            raise ValueError("ID value is required")
        
        if not table_name:
            logger.error("Table name is required")
            raise ValueError("Table name is required")
        
        logger.info(f"Retrieving item from {table_name} where {id_key}={id_value}")
        
        # Prepare the key
        key = {id_key: id_value}

        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        dynamo_metadata_table = dynamodb.Table(table_name)
        
        # Get the item
        response = dynamo_metadata_table.get_item(Key=key)

        # Check if the item exists
        if 'Item' not in response:
            logger.info(f"No item found with {id_key}={id_value}")
            return None

        # Convert DynamoDB item to standard Python dict
        item = response['Item']
        json_str = json.dumps(item, cls=DecimalEncoder)
        result = json.loads(json_str)
        
        logger.info(f"Successfully retrieved item from {table_name}")
        return result

    except ClientError as e:
        error_message = f"DynamoDB error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(f"Error retrieving {id_value} from {table_name}: {error_message}")
        raise Exception(error_message)
    except Exception as e:
        error_message = f"Error retrieving item: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        raise Exception(error_message)
