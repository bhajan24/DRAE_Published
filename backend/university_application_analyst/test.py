
import boto3
import json
from config import AWS_REGION, get_agent_arn

client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)

def test_application_evaluation():
    """Test the university application evaluation agent"""
    
    # Sample application data for testing
    test_prompt = """
    Please evaluate the following university application:
    
    Student: John Doe
    Application ID: AGR-2025-TEST
    Program: Master of Agricultural Sciences
    Specialization: Crop Sciences
    
    Academic Background:
    - GPA: 8.2/10.0 from University of Agriculture
    - Degree: B.Sc. Agriculture (2024)
    - Rank: Top 20%
    
    Test Scores:
    - GRE: Quantitative 160, Verbal 155, AWA 4.0
    - IELTS: 7.5 overall
    
    Research Experience:
    - 8-month thesis project on "Sustainable Crop Production"
    - Supervisor: Dr. Smith
    - Lab skills: Soil analysis, Plant breeding techniques
    
    Work Experience:
    - 6-month internship at AgriCorp as Research Assistant
    
    Documents: All required documents submitted and verified.
    
    Please provide a complete 4-level evaluation.
    """
    
    payload = json.dumps({"prompt": test_prompt})
    
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=get_agent_arn(),
            payload=payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        print("=== Agent Response ===")
        print(json.dumps(response_data, indent=2))
        
        return response_data
        
    except Exception as e:
        print(f"Error testing agent: {e}")
        return None

if __name__ == "__main__":
    test_application_evaluation()