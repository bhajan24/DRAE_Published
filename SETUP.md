# Setup Instructions

## Before Using This Repository

This repository has been sanitized for public use. You need to configure your AWS resources and update configuration files with your specific values.

### Required Replacements

1. **AWS Account ID**: Replace `YOUR_AWS_ACCOUNT_ID` with your actual AWS account ID
2. **Company Name**: Replace `YOUR_COMPANY` with your organization name
3. **S3 Bucket**: Replace `your-s3-bucket-name` with your actual S3 bucket name
4. **Agent IDs**: Replace `YOUR_AGENT_ID` with your actual Bedrock AgentCore agent ID
5. **Memory IDs**: Replace `YOUR_MEMORY_ID` with your actual memory ID

### Configuration Files to Update

- `backend/lambda/config.yaml`


### AWS Resources Required

- Bedrock AgentCore agents
- IAM roles with appropriate permissions
- S3 buckets for document storage
- DynamoDB tables
- Step Functions state machines

Refer to individual component README files for detailed setup instructions.
