#!/usr/bin/env python3
"""
Setup script to configure the university application analyst agent
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment configuration"""
    
    print("🎓 University Application Analyst AgentCore Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get user inputs
    print("\n📝 Please provide your AWS configuration:")
    
    aws_region = input("AWS Region [us-east-1]: ").strip() or "us-east-1"
    aws_account_id = input("AWS Account ID: ").strip()
    
    if not aws_account_id:
        print("❌ AWS Account ID is required!")
        sys.exit(1)
    
    agent_id = input("Agent ID (leave empty to generate): ").strip()
    memory_id = input("Memory ID (leave empty to generate): ").strip()
    
    # Generate IDs if not provided
    if not agent_id:
        agent_id = f"uni_application_analyst-{generate_id()}"
    
    if not memory_id:
        memory_id = f"uni_application_analyst_mem-{generate_id()}"
    
    # Create .env file
    env_content = f"""# AWS Configuration
AWS_REGION={aws_region}
AWS_ACCOUNT_ID={aws_account_id}

# Agent Configuration  
AGENT_ID={agent_id}

# Memory Configuration
MEMORY_ID={memory_id}

# Optional: Override default values
# BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
# LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to .env")
    print(f"📋 Agent ID: {agent_id}")
    print(f"📋 Memory ID: {memory_id}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Run: python deploy.py")
    print(f"   2. Test: python test.py")

def generate_id():
    """Generate a random ID"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

if __name__ == "__main__":
    setup_environment()
