
import boto3
import json
from config import AWS_REGION, get_agent_arn

client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)

def test_application_autofill():
    """Test the university application autofill agent"""
    
    # Sample S3 payload for testing
    test_payload = {
        "s3_bucket_name": "your-documents-bucket",
        "s3_key": "student-documents/john-doe/"
    }
    
    payload = json.dumps(test_payload)
    
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
        
        # Validate response structure
        expected_keys = [
            'personal_information', 'academic_background', 
            'test_scores', 'research_experience', 'work_experience',
            'extracurricular', 'program_specific', 'profile_analysis'
        ]
        
        for key in expected_keys:
            if key in response_data:
                print(f"✓ {key} found in response")
            else:
                print(f"✗ {key} missing from response")
        
        return response_data
        
    except Exception as e:
        print(f"Error testing agent: {e}")
        return None

if __name__ == "__main__":
    test_application_autofill()