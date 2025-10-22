#!/usr/bin/env python3
"""
Health check script for AgentCore deployment
"""

import boto3
import yaml
import json
import logging
from datetime import datetime
from config import AWS_REGION, get_agent_arn, AGENT_NAME

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
    
    agent_config = config['agents'][AGENT_NAME]
    
    # Check 1: Agent Runtime Status
    try:
        client = boto3.client('bedrock-agentcore', region_name=agent_config['aws']['region'])
        
        # Simple test with minimal S3 payload
        test_payload = json.dumps({
            "s3_bucket_name": "test-bucket",
            "s3_key": "test-documents/"
        })
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=get_agent_arn(),
            payload=test_payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info("✓ Agent runtime is responsive")
        
        # Check if response has expected structure (even if empty due to no documents)
        if isinstance(response_data, dict):
            logger.info("✓ Agent returns structured response")
        else:
            logger.warning("⚠ Agent response format unexpected")
            
    except Exception as e:
        logger.error(f"✗ Agent runtime check failed: {e}")
        return False
    
    # Check 2: Memory Store Status
    try:
        memory_arn = agent_config['bedrock_agentcore']['memory_arn']
        
        # Check if memory exists
        memory_response = client.get_memory(memoryArn=memory_arn)
        logger.info("✓ Memory store is accessible")
        
    except Exception as e:
        logger.warning(f"⚠ Memory store check failed: {e}")
    
    # Check 3: Model Access
    try:
        bedrock_client = boto3.client('bedrock', region_name=AWS_REGION)
        
        model_id = agent_config['bedrock_agentcore']['model_id']
        
        # List available models to verify access
        models = bedrock_client.list_foundation_models()
        model_ids = [model['modelId'] for model in models['modelSummaries']]
        
        if model_id in model_ids:
            logger.info(f"✓ Model {model_id} is accessible")
        else:
            logger.warning(f"⚠ Model {model_id} not found in available models")
            
    except Exception as e:
        logger.warning(f"⚠ Model access check failed: {e}")
    
    # Check 4: IAM Permissions
    try:
        sts_client = boto3.client('sts', region_name=AWS_REGION)
        identity = sts_client.get_caller_identity()
        logger.info(f"✓ Running as: {identity.get('Arn', 'Unknown')}")
        
    except Exception as e:
        logger.warning(f"⚠ IAM identity check failed: {e}")
    
    # Check 5: S3 Access (test buckets from config)
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        from config import S3_BUCKETS
        accessible_buckets = []
        
        for bucket in S3_BUCKETS:
            try:
                s3_client.head_bucket(Bucket=bucket)
                accessible_buckets.append(bucket)
            except:
                pass
        
        if accessible_buckets:
            logger.info(f"✓ S3 access verified for buckets: {accessible_buckets}")
        else:
            logger.warning("⚠ No S3 buckets accessible")
            
    except Exception as e:
        logger.warning(f"⚠ S3 access check failed: {e}")
    
    # Summary
    logger.info("=== Health Check Summary ===")
    logger.info(f"Agent: {AGENT_NAME}")
    logger.info(f"Region: {AWS_REGION}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("Health check completed")
    
    return True

def check_deployment_status():
    """Check if all components are properly deployed"""
    
    logger.info("Checking deployment status...")
    
    try:
        # Check if agent ARN file exists
        with open('.agent_arn', 'r') as f:
            agent_arn = f.read().strip()
        logger.info(f"✓ Agent ARN found: {agent_arn}")
        
        # Verify agent exists
        client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
        
        # Try to get agent details
        agent_response = client.get_agent_runtime(agentRuntimeArn=agent_arn)
        logger.info("✓ Agent deployment verified")
        
        return True
        
    except FileNotFoundError:
        logger.error("✗ Agent ARN file not found - agent may not be deployed")
        return False
    except Exception as e:
        logger.error(f"✗ Deployment verification failed: {e}")
        return False

if __name__ == "__main__":
    deployment_ok = check_deployment_status()
    if deployment_ok:
        health_ok = check_agent_health()
        if health_ok:
            logger.info("🎉 All checks passed!")
        else:
            logger.error("❌ Health check failed")
    else:
        logger.error("❌ Deployment check failed")
