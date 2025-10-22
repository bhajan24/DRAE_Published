import json
import logging
import traceback
import boto3
from botocore.exceptions import ClientError

from config import config
from aws_utils import textractor_document_analysis

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def event_actions(record):
    """
    Handle S3 events by extracting text from uploaded documents and saving as .txt files.
    
    Args:
        record (dict): S3 event record
        
    Returns:
        tuple: (success: bool, result: dict or error_message: str)
    """
    try:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        
        logger.info(f"Processing S3 event for s3://{bucket_name}/{object_key}")
        
        # Skip if already a .txt file to avoid infinite loops
        # if object_key.lower().endswith('.txt'):
        #     logger.info(f"Skipping .txt file: {object_key}")
        #     return True, {"message": "Skipped .txt file", "object_key": object_key}
        
        # Extract text using Textractor
        logger.info(f"Starting text extraction for s3://{bucket_name}/{object_key}")
        status, extracted_text = textractor_document_analysis(bucket_name, object_key)
        
        if status != "SUCCEEDED":
            logger.error(f"Text extraction failed for {object_key}: {extracted_text}")
            return False, f"Text extraction failed: {extracted_text}"
        
        # Generate .txt file name (same name, .txt extension)
        file_name_without_ext = object_key.rsplit('.', 1)[0] if '.' in object_key else object_key
        txt_object_key = f"{file_name_without_ext}.txt"
        
        # Save extracted text to S3 as .txt file
        logger.info(f"Saving extracted text to s3://{bucket_name}/{txt_object_key}")
        
        s3_client = boto3.client('s3', region_name=config["AWS"]["region_name"])
        s3_client.put_object(
            Bucket=bucket_name,
            Key=txt_object_key,
            Body=extracted_text.encode('utf-8'),
            ContentType='text/plain'
        )
        
        logger.info(f"Successfully processed S3 event and saved text to {txt_object_key}")
        
        return True, {
            "message": "Text extraction completed successfully",
            "source_object": object_key,
            "output_object": txt_object_key,
            "text_length": len(extracted_text)
        }
        
    except KeyError as e:
        error_msg = f"Missing required field in S3 event: {e}"
        logger.error(error_msg)
        return False, error_msg
    except ClientError as e:
        error_msg = f"AWS error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error processing S3 event: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg
    