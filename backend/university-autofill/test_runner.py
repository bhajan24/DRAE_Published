#!/usr/bin/env python3
"""
Comprehensive test runner for AgentCore application
"""

import json
import logging
from pathlib import Path
from test import test_application_autofill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_case(filename):
    """Load test case from file"""
    test_file = Path("test_case") / filename
    if test_file.exists():
        with open(test_file, 'r') as f:
            return json.load(f)
    return None

def run_comprehensive_tests():
    """Run all available test cases"""
    
    logger.info("Starting comprehensive AgentCore tests...")
    
    # Test 1: Basic functionality test
    logger.info("=== Test 1: Basic Functionality ===")
    basic_result = test_application_autofill()
    
    if basic_result:
        logger.info("✓ Basic functionality test passed")
        validate_response_structure(basic_result)
    else:
        logger.error("✗ Basic functionality test failed")
    
    # Test 2: Sample S3 locations
    logger.info("=== Test 2: Multiple S3 Locations ===")
    test_locations = [
        {
            "s3_bucket_name": "your-documents-bucket",
            "s3_key": "student-documents/test-student-1/"
        },
        {
            "s3_bucket_name": "your-documents-bucket", 
            "s3_key": "student-documents/test-student-2/"
        }
    ]
    
    for i, location in enumerate(test_locations, 1):
        logger.info(f"Testing location {i}: {location['s3_key']}")
        result = test_application_autofill_with_payload(location)
        
        if result:
            logger.info(f"✓ Location {i} test passed")
        else:
            logger.warning(f"⚠ Location {i} test failed (may not have documents)")

def test_application_autofill_with_payload(payload):
    """Test with custom S3 payload"""
    import boto3
    from config import AWS_REGION, get_agent_arn
    
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    
    try:
        payload_json = json.dumps(payload)
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=get_agent_arn(),
            payload=payload_json,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return None

def validate_response_structure(response):
    """Validate the response has expected structure"""
    
    required_fields = [
        'personal_information',
        'academic_background',
        'test_scores',
        'research_experience',
        'work_experience',
        'extracurricular',
        'program_specific',
        'profile_analysis'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        logger.warning(f"Missing fields in response: {missing_fields}")
    else:
        logger.info("✓ Response structure validation passed")
    
    # Check if documents section exists
    if 'documents' in response:
        logger.info("✓ Documents section found in response")
        doc_count = len(response['documents'])
        logger.info(f"  Found {doc_count} document references")
    else:
        logger.warning("⚠ Documents section missing from response")

if __name__ == "__main__":
    run_comprehensive_tests()
