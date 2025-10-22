#!/usr/bin/env python3
"""
Health check script for AgentCore deployment
"""

import boto3
import yaml
import json
import logging
from datetime import datetime
from config import AWS_REGION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_agent_health():
    """Comprehensive health check for the AgentCore deployment"""
    
    logger.info("Starting AgentCore health check...")
    
    # Load configuration
    try:
        with open('.bedrock_agentcore.yaml', 'r') as f:
            config = yaml.safe_load(f)
        logger.info("✓ Configuration loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load configuration: {e}")
        return False
    
    agent_config = config['agents']['uni_application_analyst']
    
    # Check 1: Agent Runtime Status
    try:
        client = boto3.client('bedrock-agentcore', region_name=agent_config['aws']['region'])
        
        # Simple ping test
        test_payload = json.dumps({
            "prompt": "Health check - please respond with a simple acknowledgment."
        })
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_config['bedrock_agentcore']['agent_arn'],
            payload=test_payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info("✓ Agent runtime is responsive")
        
    except Exception as e:
        logger.error(f"✗ Agent runtime check failed: {e}")
        return False
    
    # Check 2: Memory Service
    try:
        memory_arn = agent_config['memory']['memory_arn']
        logger.info(f"✓ Memory service configured: {memory_arn}")
    except Exception as e:
        logger.error(f"✗ Memory service check failed: {e}")
    
    # Check 3: ECR Repository
    try:
        ecr_client = boto3.client('ecr', region_name=agent_config['aws']['region'])
        repo_uri = agent_config['aws']['ecr_repository']
        repo_name = repo_uri.split('/')[-1]
        
        ecr_client.describe_repositories(repositoryNames=[repo_name])
        logger.info(f"✓ ECR repository accessible: {repo_name}")
        
    except Exception as e:
        logger.error(f"✗ ECR repository check failed: {e}")
    
    # Check 4: IAM Role
    try:
        iam_client = boto3.client('iam', region_name=agent_config['aws']['region'])
        role_arn = agent_config['aws']['execution_role']
        role_name = role_arn.split('/')[-1]
        
        iam_client.get_role(RoleName=role_name)
        logger.info(f"✓ IAM execution role exists: {role_name}")
        
    except Exception as e:
        logger.error(f"✗ IAM role check failed: {e}")
    
    # Check 5: Evaluation Framework
    try:
        from tools.eval_framework import AggregatedEvaluation
        logger.info("✓ Evaluation framework imported successfully")
    except Exception as e:
        logger.error(f"✗ Evaluation framework check failed: {e}")
    
    # Check 6: Prompts
    try:
        with open("prompts/program_details.txt", "r") as f:
            program_details = f.read()
        with open("prompts/evaluation_framework.txt", "r") as f:
            eval_framework = f.read()
        
        if len(program_details) > 0 and len(eval_framework) > 0:
            logger.info("✓ Prompt files loaded successfully")
        else:
            logger.warning("⚠ Prompt files are empty")
            
    except Exception as e:
        logger.error(f"✗ Prompt files check failed: {e}")
    
    logger.info("Health check completed")
    return True

def get_deployment_info():
    """Get deployment information"""
    
    try:
        with open('.bedrock_agentcore.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        agent_config = config['agents']['uni_application_analyst']
        
        info = {
            "agent_id": agent_config['bedrock_agentcore']['agent_id'],
            "agent_arn": agent_config['bedrock_agentcore']['agent_arn'],
            "memory_id": agent_config['memory']['memory_id'],
            "region": agent_config['aws']['region'],
            "account": agent_config['aws']['account'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Deployment Information:")
        for key, value in info.items():
            logger.info(f"  {key}: {value}")
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get deployment info: {e}")
        return None

if __name__ == "__main__":
    get_deployment_info()
    check_agent_health()
