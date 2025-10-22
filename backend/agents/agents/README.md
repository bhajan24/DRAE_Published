# DRAE AI Agents

## Overview
This directory contains the AI agents for the DRAE platform, built using AWS Bedrock and AgentCore.

## Agents

### Discovery Agent
- **Location**: `Discovery-Agent/`
- **Purpose**: AgentCore deployment for university discovery
- **Features**: JSON payload handling, CS/ML requirements processing
- **Model**: Uses AWS Bedrock with Nova models

### Search Engine Agent  
- **Location**: `Search-Engine/`
- **Purpose**: AI-powered university search using LLM
- **Features**: Text cleaning, streaming responses, intelligent matching
- **Model**: Anthropic Claude 3.5 Sonnet via Bedrock

## Setup

1. **Install Dependencies**:
   ```bash
   cd Discovery-Agent && pip install -r requirements.txt
   cd ../Search-Engine && pip install -r requirements.txt
   ```

2. **Configure AWS**:
   ```bash
   export AWS_REGION=us-east-1
   aws configure
   ```

3. **Deploy Agents**:
   ```bash
   python university_discoverer.py
   python university_search.py
   ```

## Configuration
- Set `AWS_REGION` environment variable
- Ensure AWS credentials are configured
- Update model IDs as needed for your deployment
