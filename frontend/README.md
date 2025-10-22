# DRAE - Discover, Recommend, Apply & Enroll

## 🎯 Overview
DRAE is an AI-powered platform that automates university applications for students and provides instant background verification for universities using AWS AI Agents.

## 🏗️ Architecture
Multi-agent system built on **AWS AgentCore** with three specialized AI agents powered by **Amazon Nova** models:
- **Student Assistant Agent**: Document processing & application generation
- **BGV Verification Agent**: Fraud detection & document verification  
- **University Matching Agent**: Intelligent university-student matching

## 🚀 Quick Start

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.9+
- Node.js 18+

### Installation
```bash
# Clone repository
git clone <repository-url>
cd DRAE_Published

# Install dependencies
npm install
pip install -r requirements.txt

# Configure AWS
aws configure

# Start development server
npm start
```

## 🎯 Features

### For Students
- **Discover**: AI-powered university search and matching
- **Recommend**: Personalized university recommendations based on profile
- **Apply**: Auto-filled applications with document processing
- **Enroll**: Real-time status tracking and enrollment management

### For Universities  
- **Background Verification**: AI-powered document fraud detection
- **Application Processing**: Automated review and scoring
- **Report Generation**: Detailed verification reports
- **Admin Dashboard**: Comprehensive application management

## 🛠️ Tech Stack
- **Frontend**: React.js, Material-UI
- **Backend**: Python Flask, AWS Lambda
- **AI/ML**: Amazon Bedrock, Nova Models, AgentCore
- **Storage**: Amazon S3, DynamoDB
- **Authentication**: AWS Cognito

## 📁 Project Structure
```
DRAE_Published/
├── src/
│   ├── components/          # React components
│   ├── services/           # API services
│   └── utils/              # Utility functions
├── working_proxy.py        # Backend proxy server
├── package.json           # Dependencies
└── README.md             # This file
```

## 🔧 Configuration
1. Set up AWS credentials
2. Configure Cognito Identity Pool
3. Deploy Lambda functions
4. Update API endpoints in services

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Support
For issues and questions, please create an issue in this repository.
