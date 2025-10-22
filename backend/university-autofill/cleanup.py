#!/usr/bin/env python3
"""
Cleanup script for AgentCore resources
"""

import boto3
import yaml
import logging
from config import (
    AWS_REGION, AGENT_NAME, get_agent_arn, get_memory_arn,
    CODEBUILD_PROJECT_NAME, ECR_REPOSITORY_NAME
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_resources():
    """Clean up AgentCore resources"""
    
    # Initialize clients using config
    agentcore_client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    ecr_client = boto3.client('ecr', region_name=AWS_REGION)
    codebuild_client = boto3.client('codebuild', region_name=AWS_REGION)
    
    try:
        # Delete agent using config
        agent_arn = get_agent_arn()
        logger.info(f"Deleting agent: {agent_arn}")
        try:
            agentcore_client.delete_agent_runtime(agentRuntimeArn=agent_arn)
            logger.info("✓ Agent deleted successfully")
        except Exception as e:
            logger.warning(f"Agent deletion failed (may not exist): {e}")
        
        # Delete memory using config
        memory_arn = get_memory_arn()
        logger.info(f"Deleting memory: {memory_arn}")
        try:
            agentcore_client.delete_memory(memoryArn=memory_arn)
            logger.info("✓ Memory deleted successfully")
        except Exception as e:
            logger.warning(f"Memory deletion failed (may not exist): {e}")
        
        # Delete CodeBuild project using config
        logger.info(f"Deleting CodeBuild project: {CODEBUILD_PROJECT_NAME}")
        try:
            codebuild_client.delete_project(name=CODEBUILD_PROJECT_NAME)
            logger.info("✓ CodeBuild project deleted successfully")
        except Exception as e:
            logger.warning(f"CodeBuild project deletion failed (may not exist): {e}")
        
        # Optional: Delete ECR repository
        logger.info(f"Deleting ECR repository: {ECR_REPOSITORY_NAME}")
        try:
            ecr_client.delete_repository(
                repositoryName=ECR_REPOSITORY_NAME,
                force=True
            )
            logger.info("✓ ECR repository deleted successfully")
        except Exception as e:
            logger.warning(f"ECR repository deletion failed (may not exist): {e}")
        
        logger.info("🎉 Cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_resources()
