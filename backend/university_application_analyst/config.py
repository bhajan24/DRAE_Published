"""
Centralized configuration for AgentCore deployment
"""

import os
from pathlib import Path

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', 'YOUR_AWS_ACCOUNT_ID')

# Bedrock Model Configuration
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# Agent Configuration
AGENT_NAME = "uni_application_analyst"
AGENT_ID = os.getenv('AGENT_ID', 'uni_application_analyst-YOUR_AGENT_ID')

# Memory Configuration
MEMORY_MODE = "STM_ONLY"
MEMORY_ID = os.getenv('MEMORY_ID', 'uni_application_analyst_mem-YOUR_MEMORY_ID')
MEMORY_NAME = "uni_application_analyst_mem"
MEMORY_EVENT_EXPIRY_DAYS = 30

# Platform Configuration
PLATFORM = "linux/arm64"
CONTAINER_RUNTIME = "docker"

# Network Configuration
NETWORK_MODE = "PUBLIC"
SERVER_PROTOCOL = "HTTP"
OBSERVABILITY_ENABLED = True

# IAM Role Configuration
EXECUTION_ROLE_NAME = "BedrockAgentCoreExecutionRole"
CODEBUILD_ROLE_NAME = "BedrockAgentCoreCodeBuildRole"

# ECR Configuration
ECR_REPOSITORY_NAME = f"bedrock-agentcore-{AGENT_NAME}"

# CodeBuild Configuration
CODEBUILD_PROJECT_NAME = f"bedrock-agentcore-{AGENT_NAME}-builder"
CODEBUILD_SOURCE_BUCKET = f"bedrock-agentcore-codebuild-sources-{AWS_ACCOUNT_ID}-{AWS_REGION}"

# Boto3 Configuration
BOTO_CONFIG = {
    "retries": {"max_attempts": 7, "mode": "standard"},
    "connect_timeout": 60,
    "read_timeout": 3600
}

# Logging Configuration
LOG_LEVEL = "INFO"

# Prompt Files
PROGRAM_DETAILS_FILE = "prompts/program_details.txt"
EVALUATION_FRAMEWORK_FILE = "prompts/evaluation_framework.txt"

# S3 Buckets (for IAM permissions)
S3_BUCKETS = [
    "your-data-bucket-1",
    "your-data-bucket-2"
]

# DynamoDB Tables (for IAM permissions)
DYNAMODB_TABLES = [
    "uni-applications",
    "uni-applications-evaluated", 
    "UA-applications"
]

def get_agent_arn():
    """Get the full agent ARN"""
    return f"arn:aws:bedrock-agentcore:{AWS_REGION}:{AWS_ACCOUNT_ID}:runtime/{AGENT_ID}"

def get_memory_arn():
    """Get the full memory ARN"""
    return f"arn:aws:bedrock-agentcore:{AWS_REGION}:{AWS_ACCOUNT_ID}:memory/{MEMORY_ID}"

def get_execution_role_arn():
    """Get the full execution role ARN"""
    return f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{EXECUTION_ROLE_NAME}"

def get_codebuild_role_arn():
    """Get the full CodeBuild role ARN"""
    return f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{CODEBUILD_ROLE_NAME}"

def get_ecr_repository_uri():
    """Get the full ECR repository URI"""
    return f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPOSITORY_NAME}"
