import boto3
import time
from typing import Dict, List
from botocore.exceptions import ClientError

def read_text_files_from_s3(
    bucket_name: str,
    s3_key_prefix: str,
    file_names: List[str],
    max_wait_time: int = 20,
    check_interval: int = 5
) -> Dict[str, str]:
    """
    Read text files from S3 bucket with retry logic for files being processed.
    
    Args:
        bucket_name: Name of the S3 bucket
        s3_key_prefix: S3 key prefix/folder path (e.g., 'folder/subfolder')
        file_names: List of file names without extension
        max_wait_time: Maximum time to wait for files in seconds (default: 20)
        check_interval: Time interval between checks in seconds (default: 5)
    
    Returns:
        Dictionary with file names as keys and their content as values
    """
    s3_client = boto3.client('s3')
    
    # Initialize result dictionary with empty strings
    result = {file_name: "" for file_name in file_names}
    
    # Track which files are still pending
    pending_files = set(file_names)
    
    # Calculate number of retries
    num_retries = max_wait_time // check_interval
    
    # Ensure s3_key_prefix ends without trailing slash for consistent path building
    s3_key_prefix = s3_key_prefix.rstrip('/')
    
    for attempt in range(num_retries + 1):
        files_to_remove = set()
        
        for file_name in pending_files:
            # Construct the full S3 key
            s3_key = f"{s3_key_prefix}/{file_name}.txt"
            
            try:
                # Try to get the file from S3
                response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                
                # Read the content
                content = response['Body'].read().decode('utf-8')
                result[file_name] = content
                
                # Mark file as successfully read
                files_to_remove.add(file_name)
                print(f"Successfully read: {file_name}.txt")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                
                if error_code == 'NoSuchKey':
                    # File doesn't exist yet
                    if attempt < num_retries:
                        print(f"File not found: {file_name}.txt - Will retry (attempt {attempt + 1}/{num_retries + 1})")
                    else:
                        print(f"File not found: {file_name}.txt - Max retries reached, skipping")
                        files_to_remove.add(file_name)
                else:
                    # Other S3 errors
                    print(f"Error reading {file_name}.txt: {str(e)}")
                    files_to_remove.add(file_name)
                    
            except Exception as e:
                # Handle other exceptions (encoding errors, etc.)
                print(f"Unexpected error reading {file_name}.txt: {str(e)}")
                files_to_remove.add(file_name)
        
        # Remove successfully read files and files with errors from pending list
        pending_files -= files_to_remove
        
        # If all files are processed, break early
        if not pending_files:
            print("All files processed successfully")
            break
        
        # Wait before next retry (but not after the last attempt)
        if pending_files and attempt < num_retries:
            print(f"Waiting {check_interval} seconds before next retry...")
            time.sleep(check_interval)
    
    return result