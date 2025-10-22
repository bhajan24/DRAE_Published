#!/usr/bin/env python3
import boto3
import json
import time
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')

def parse_universities_from_response(response_text):
    """Dynamically parse university data from AgentCore response"""
    universities = []
    
    if not response_text or len(response_text) < 50:
        return universities
    
    # Split response into lines for processing
    lines = response_text.split('\n')
    current_university = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for university names in various formats
        # Pattern 1: "1. **University Name**" or "**University Name**"
        university_match = re.search(r'^\d*\.?\s*\*\*([^*]+)\*\*', line)
        if university_match:
            # Save previous university
            if current_university and current_university.get('name'):
                universities.append(current_university)
            
            # Extract university name
            name = university_match.group(1).strip()
            # Clean the name (remove rankings, locations in parentheses)
            name = re.sub(r'\s*-\s*#\d+.*', '', name)  # Remove "- #1 globally"
            name = re.sub(r'\s*\([^)]*\).*', '', name)  # Remove "(location)"
            
            current_university = {
                "id": len(universities) + 1,
                "name": name,
                "location": "USA",
                "ranking": len(universities) + 1,
                "programs": [],
                "acceptance_rate": "",
                "tuition": "",
                "deadline": "",
                "features": [],
                "matchScore": 90,
                "gpaRequirement": "",
                "greRequirement": "",
                "researchOpportunities": []
            }
        
        # Extract details for current university
        elif current_university and line:
            # Extract acceptance rate
            if 'acceptance rate' in line.lower():
                rate_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if rate_match:
                    current_university["acceptance_rate"] = f"{rate_match.group(1)}%"
            
            # Extract tuition/costs
            if any(word in line.lower() for word in ['tuition', 'cost', '$']):
                tuition_match = re.search(r'\$[\d,]+', line)
                if tuition_match:
                    current_university["tuition"] = tuition_match.group(0)
            
            # Extract GPA requirements
            if 'gpa' in line.lower():
                gpa_match = re.search(r'(\d\.\d+)', line)
                if gpa_match:
                    current_university["gpaRequirement"] = f"{gpa_match.group(1)}+"
            
            # Extract SAT scores (as additional info)
            if 'sat' in line.lower():
                sat_match = re.search(r'(\d{4})', line)
                if sat_match:
                    current_university["features"].append(f"SAT: {sat_match.group(1)}+")
            
            # Extract deadlines
            if any(word in line.lower() for word in ['deadline', 'january', 'november', 'december']):
                date_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d+', line, re.IGNORECASE)
                if date_match:
                    current_university["deadline"] = date_match.group(0)
            
            # Extract programs/specializations
            if any(word in line.lower() for word in ['computer science', 'engineering', 'ai', 'machine learning', 'cybersecurity']):
                if 'computer science' in line.lower() and 'Computer Science' not in current_university["programs"]:
                    current_university["programs"].append('Computer Science')
                if 'engineering' in line.lower() and 'Engineering' not in current_university["programs"]:
                    current_university["programs"].append('Engineering')
                if any(word in line.lower() for word in ['ai', 'artificial intelligence']) and 'AI/ML' not in current_university["programs"]:
                    current_university["programs"].append('AI/ML')
    
    # Add the last university
    if current_university and current_university.get('name'):
        universities.append(current_university)
    
    # Set default values for missing fields
    for uni in universities:
        if not uni["programs"]:
            uni["programs"] = ["Computer Science"]
        if not uni["acceptance_rate"]:
            uni["acceptance_rate"] = "Competitive"
        if not uni["tuition"]:
            uni["tuition"] = "Contact for details"
        if not uni["deadline"]:
            uni["deadline"] = "Check website"
        if not uni["gpaRequirement"]:
            uni["gpaRequirement"] = "3.0+"
        uni["greRequirement"] = "Check requirements"
        uni["researchOpportunities"] = ["Research programs available"]
        uni["features"] = uni["features"] or ["Top-ranked program"]
        uni["matchScore"] = max(95 - (uni["id"] * 5), 70)
    
    return universities

@app.route('/api/agentcore/search', methods=['POST'])
def search_universities():
    try:
        data = request.json
        
        # Use exact same structure as testing file
        payload = data  # Direct payload from React
        
        response = bedrock_agentcore.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:040504913362:runtime/university_discoverer_v6-0UljVlBJfV',
            runtimeSessionId='test_session_12345678901234567890123456789012345678901234567890',
            payload=json.dumps(payload),
            qualifier="DEFAULT"
        )
        
        # Use exact same response handling as testing file
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        return jsonify({
            'success': True,
            'agentcore_response': response_data,
            'runtime_arn': 'arn:aws:bedrock-agentcore:us-east-1:040504913362:runtime/university_discoverer_v6-0UljVlBJfV'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 AgentCore Proxy - WORKING with live runtime!")
    app.run(host='0.0.0.0', port=8081, debug=True)
