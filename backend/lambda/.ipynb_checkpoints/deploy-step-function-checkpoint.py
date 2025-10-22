#!/usr/bin/env python3
"""
Deploy optimized Step Function for parallel document processing
"""

import json
import boto3
from botocore.exceptions import ClientError

def deploy_step_function():
    """Deploy the optimized step function"""
    
    # Configuration - update these values
    LAMBDA_FUNCTION_ARN = "arn:aws:lambda:us-east-1:040504913362:function:your-lambda-function-name"
    STEP_FUNCTION_ROLE_ARN = "arn:aws:iam::040504913362:role/your-step-function-role"
    STEP_FUNCTION_NAME = "uni-application-processing-parallel"
    
    # Load step function definition
    with open('step-function-parallel.json', 'r') as f:
        definition = f.read()
    
    # Replace placeholder with actual Lambda ARN
    definition = definition.replace("${LambdaFunctionArn}", LAMBDA_FUNCTION_ARN)
    
    # Create Step Functions client
    stepfunctions = boto3.client('stepfunctions')
    
    try:
        # Create the state machine
        response = stepfunctions.create_state_machine(
            name=STEP_FUNCTION_NAME,
            definition=definition,
            roleArn=STEP_FUNCTION_ROLE_ARN,
            type='STANDARD'
        )
        
        print(f"✅ Step Function created successfully!")
        print(f"ARN: {response['stateMachineArn']}")
        print(f"Update your config.yaml with this ARN:")
        print(f"PROCESS:")
        print(f"  application_processing_sm: {response['stateMachineArn']}")
        
        return response['stateMachineArn']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'StateMachineAlreadyExists':
            print("⚠️  Step Function already exists. Updating...")
            
            # Get existing state machine ARN
            existing_machines = stepfunctions.list_state_machines()
            existing_arn = None
            
            for machine in existing_machines['stateMachines']:
                if machine['name'] == STEP_FUNCTION_NAME:
                    existing_arn = machine['stateMachineArn']
                    break
            
            if existing_arn:
                # Update the existing state machine
                stepfunctions.update_state_machine(
                    stateMachineArn=existing_arn,
                    definition=definition,
                    roleArn=STEP_FUNCTION_ROLE_ARN
                )
                print(f"✅ Step Function updated successfully!")
                print(f"ARN: {existing_arn}")
                return existing_arn
        else:
            print(f"❌ Error creating Step Function: {e}")
            return None

if __name__ == "__main__":
    print("🚀 Deploying optimized Step Function for parallel document processing...")
    deploy_step_function()
