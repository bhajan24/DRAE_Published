#!/usr/bin/env python3
"""
Comprehensive test runner for AgentCore application
"""

import json
import logging
from pathlib import Path
from test import test_application_evaluation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_case(filename):
    """Load test case from file"""
    test_file = Path("test_case") / filename
    if test_file.exists():
        with open(test_file, 'r') as f:
            return json.load(f)
    return None

def format_application_prompt(test_data):
    """Format test data into evaluation prompt"""
    
    prompt = f"""
Please evaluate the following university application:

Student: {test_data['student_name']}
Application ID: {test_data['application_id']}
Program: Master of Agricultural Sciences
Specialization: {test_data['specialization']}

Academic Background:
- GPA: {test_data['academic_background']['gpa']} from {test_data['academic_background']['institution']}
- Degree: {test_data['academic_background']['degree']} ({test_data['academic_background']['graduation_date']})
- Rank: {test_data['academic_background']['rank']}
- Trend: {test_data['academic_background']['trend']}

Test Scores:
- GRE: Quantitative {test_data['test_scores']['gre_quantitative']}, Verbal {test_data['test_scores']['gre_verbal']}, AWA {test_data['test_scores']['gre_awa']}
- {test_data['test_scores']['english_test']}: {test_data['test_scores']['english_score']}

Research Experience:
- Projects: {test_data['research_experience']['count']}
- Main project: "{test_data['research_experience']['projects'][0]['title']}"
- Duration: {test_data['research_experience']['projects'][0]['duration']}
- Supervisor: {test_data['research_experience']['projects'][0]['supervisor']}
- Lab skills: {', '.join(test_data['research_experience']['lab_skills'])}
- Publications: {test_data['research_experience']['publications']}

Work Experience:
- Organization: {test_data['work_experience'][0]['organization']}
- Role: {test_data['work_experience'][0]['role']}
- Duration: {test_data['work_experience'][0]['duration']}

Program Alignment:
- Research Interest: {test_data['program_specific']['research_interest']}
- Career Goal: {test_data['program_specific']['career_goal']}

Documents: All required documents submitted and verified.

Please provide a complete 4-level evaluation following the established framework.
"""
    return prompt

def run_comprehensive_tests():
    """Run all available test cases"""
    
    logger.info("Starting comprehensive AgentCore tests...")
    
    # Test 1: Sample application
    logger.info("=== Test 1: Sample Application ===")
    test_data = load_test_case("sample_application.json")
    
    if test_data:
        prompt = format_application_prompt(test_data)
        result = test_application_evaluation_with_prompt(prompt)
        
        if result:
            logger.info("✓ Sample application test passed")
            validate_response_structure(result)
        else:
            logger.error("✗ Sample application test failed")
    else:
        logger.warning("Sample application test case not found")
    
    # Test 2: Basic functionality test
    logger.info("=== Test 2: Basic Functionality ===")
    basic_result = test_application_evaluation()
    
    if basic_result:
        logger.info("✓ Basic functionality test passed")
    else:
        logger.error("✗ Basic functionality test failed")

def test_application_evaluation_with_prompt(prompt):
    """Test with custom prompt"""
    import boto3
    from config import AWS_REGION, get_agent_arn
    
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    
    try:
        payload = json.dumps({"prompt": prompt})
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=get_agent_arn(),
            payload=payload,
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
        'application_id',
        'student_name', 
        'specialization',
        'level1_result',
        'level2_result',
        'level3_result',
        'level4_Result'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        logger.warning(f"Missing fields in response: {missing_fields}")
    else:
        logger.info("✓ Response structure validation passed")

if __name__ == "__main__":
    run_comprehensive_tests()
