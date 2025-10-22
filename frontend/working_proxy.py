#!/usr/bin/env python3
import boto3
import json
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['*'], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'])

@app.route('/api/format-response', methods=['POST', 'OPTIONS'])
def format_response():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        agent_response = data.get('response', '')
        
        # Use Bedrock to format the response
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        format_prompt = f"""
        Extract university information from this text and return ONLY a JSON array. 
        Look for university names, rankings, locations, tuition, GPA requirements, acceptance rates, and deadlines.
        
        Text: {agent_response[:1000]}
        
        Return exactly this format:
        [
          {{
            "id": 1,
            "name": "University Name",
            "location": "City, State", 
            "ranking": "#X nationally",
            "tuition": "$XX,XXX/year",
            "acceptance_rate": "XX%",
            "gpa_requirement": "X.X",
            "deadline": "Month Day, Year",
            "programs": ["Computer Science"],
            "description": "Brief description",
            "researchOpportunities": [],
            "features": []
          }}
        ]
        """
        
        try:
            response = bedrock.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                body=json.dumps({
                    'messages': [{'role': 'user', 'content': format_prompt}],
                    'max_tokens': 1500,
                    'temperature': 0.1
                })
            )
            
            response_body = json.loads(response['body'].read())
            formatted_text = response_body['content'][0]['text']
            
            # Extract JSON from the response
            start = formatted_text.find('[')
            end = formatted_text.rfind(']') + 1
            if start != -1 and end != 0:
                universities_json = formatted_text[start:end]
                universities = json.loads(universities_json)
                
                # Ensure each university has required fields
                for i, uni in enumerate(universities):
                    uni['id'] = i + 1
                    uni.setdefault('researchOpportunities', [])
                    uni.setdefault('features', [])
                    uni.setdefault('programs', ['Computer Science'])
                    
                return jsonify({
                    'success': True,
                    'universities': universities,
                    'session_id': 'format-' + str(hash(agent_response[:100]) % 10000000000000),
                    'search_metadata': {'universitiesFound': len(universities)}
                })
        except Exception as e:
            print(f"LLM formatting failed: {e}")
        
        # Fallback: Create structured response from raw text
        universities = [{
            "id": 1,
            "name": "University Search Results",
            "location": "Multiple Locations",
            "ranking": "See Details",
            "tuition": "Varies",
            "acceptance_rate": "Contact Universities", 
            "gpa_requirement": "As Specified",
            "deadline": "Various Deadlines",
            "programs": ["Computer Science"],
            "description": agent_response[:500] + "..." if len(agent_response) > 500 else agent_response,
            "researchOpportunities": [],
            "features": []
        }]
        
        return jsonify({
            'success': True,
            'universities': universities,
            'session_id': 'fallback-' + str(hash(agent_response[:100]) % 10000000000000),
            'search_metadata': {'universitiesFound': 1}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'universities': []
        }), 500

@app.route('/api/agentcore/search', methods=['POST', 'OPTIONS'])
def search_universities():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        data = request.json
        payload = data
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:040504913362:runtime/university_discoverer_v7-kLLELuFDRR',
            runtimeSessionId='test_session_12345678901234567890123456789012345678901234567890',
            payload=json.dumps(payload),
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        universities = []
        if 'data' in response_data and 'universities' in response_data['data']:
            raw_universities = response_data['data']['universities']
            for i, uni in enumerate(raw_universities):
                universities.append({
                    'id': i + 1,
                    'name': uni.get('name', 'Unknown University'),
                    'location': uni.get('location', 'Unknown Location'),
                    'ranking': uni.get('ranking', 'Not Ranked'),
                    'tuition': uni.get('tuition', 'Contact University'),
                    'acceptance_rate': 'Contact University',
                    'gpa_requirement': '3.0+',
                    'deadline': 'Various Deadlines',
                    'programs': uni.get('programs', ['Computer Science']),
                    'description': uni.get('description', '')[:200] + '...' if len(uni.get('description', '')) > 200 else uni.get('description', ''),
                    'researchOpportunities': [],
                    'features': []
                })
        
        return jsonify({
            'success': True,
            'universities': universities,
            'agentcore_response': response_data,
            'session_id': 'search-' + str(hash(str(payload)) % 10000000000000),
            'search_metadata': {'universitiesFound': len(universities)}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST', 'OPTIONS'])
def upload_document():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        print(f"📄 Upload request received")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        # Handle file upload
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        document_type = request.form.get('document_type', 'transcript')
        student_name = request.form.get('student_name', 'Student')
        
        print(f"✅ Processing file: {file.filename}, type: {document_type}")
        
        # Simulate processing time
        time.sleep(1)
        
        # Mock response
        document_id = f"doc-{int(time.time())}"
        
        response_data = {
            'status': 'success',
            'document_id': document_id,
            's3_url': f'https://example-bucket.s3.amazonaws.com/documents/{document_id}.pdf',
            'extracted_data': {
                'gpa': '3.8',
                'courses': ['Computer Science', 'Mathematics'],
                'graduation_year': '2024',
                'student_name': student_name
            },
            'confidence_scores': {
                'gpa': 0.95,
                'courses': 0.88,
                'graduation_year': 0.92
            }
        }
        
        print(f"✅ Upload successful: {document_id}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/university-insights', methods=['POST', 'OPTIONS'])
def university_insights():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        university_name = data.get('university_name', 'University')
        student_profile = data.get('student_profile', {})
        
        # Simulate processing time
        time.sleep(2)
        
        # Mock detailed insights response
        return jsonify({
            'status': 'success',
            'university': {
                'name': university_name,
                'detailed_info': {
                    'admission_requirements': {
                        'gpa_minimum': '3.5/4.0',
                        'entrance_exam': 'GRE General Test',
                        'english_requirement': 'TOEFL 90+ or IELTS 6.5+',
                        'documents_needed': [
                            'Academic transcripts',
                            'Statement of Purpose',
                            'Letters of Recommendation (3)',
                            'Resume/CV',
                            'Research proposal (for research programs)'
                        ]
                    },
                    'application_process': {
                        'application_portal': 'University admissions website',
                        'application_fee': '$75-$125',
                        'steps': [
                            'Online application submission',
                            'Document upload',
                            'Standardized test scores',
                            'Interview (if required)',
                            'Final admission decision'
                        ]
                    },
                    'deadlines': {
                        'application_deadline': 'December 15, 2024',
                        'test_score_deadline': 'December 31, 2024',
                        'interview_period': 'February 1-28, 2025',
                        'admission_result': 'March 15, 2025',
                        'enrollment_deadline': 'April 30, 2025'
                    },
                    'scholarships': [
                        {
                            'name': 'Merit Scholarship',
                            'amount': '$10,000-$25,000/year',
                            'eligibility': 'Top 20% of applicants'
                        },
                        {
                            'name': 'Research Assistantship',
                            'amount': '$20,000-$30,000/year',
                            'eligibility': 'Graduate students in research programs'
                        }
                    ],
                    'placement_statistics': {
                        'average_package': '$95,000/year',
                        'highest_package': '$180,000/year',
                        'placement_rate': '92%',
                        'top_recruiters': ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta'],
                        'popular_roles': ['Software Engineer', 'Data Scientist', 'Product Manager']
                    }
                },
                'match_analysis': {
                    'admission_probability': 'Good (75%)',
                    'strengths': ['Strong academic background', 'Relevant experience'],
                    'recommendations': [
                        'Strengthen statement of purpose',
                        'Highlight relevant projects and research',
                        'Secure strong recommendation letters'
                    ]
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/autofill', methods=['POST', 'OPTIONS'])
def autofill_form():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        documents = data.get('documents', [])
        form_fields = data.get('form_fields', [])
        
        # Mock autofill response
        return jsonify({
            'autofill_data': {
                'name': 'Alex Johnson',
                'email': 'student@example.com',
                'gpa': '3.8',
                'major': 'Computer Science',
                'skills': ['Python', 'Machine Learning', 'Data Analysis']
            },
            'confidence_scores': {
                'name': 0.98,
                'email': 0.95,
                'gpa': 0.92,
                'major': 0.89,
                'skills': 0.85
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-url', methods=['POST'])
def get_upload_url():
    """Generate presigned URL for S3 upload"""
    try:
        data = request.json
        file_name = data.get('fileName', f'document_{uuid.uuid4().hex}')
        file_type = data.get('fileType', 'application/pdf')
        
        # Remove spaces and special characters from file name
        safe_file_name = file_name.replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '')
        
        # S3 configuration
        bucket_name = 'university-documents-bucket'
        s3_key = f'uploads/{uuid.uuid4().hex}_{safe_file_name}'
        
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key,
                'ContentType': file_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return jsonify({
            'success': True,
            'uploadUrl': presigned_url,
            'fileKey': s3_key,
            'bucketName': bucket_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agentcore/autofill', methods=['POST', 'OPTIONS'])
def autofill_documents():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        data = request.json
        payload = data
        
        print(f"🔍 Autofill request payload: {payload}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:040504913362:runtime/university_autofill_agent-31ubcy27m5',
            runtimeSessionId='autofill_session_12345678901234567890123456789012345678901234567890',
            payload=json.dumps(payload),
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print(f"📥 AgentCore raw response: {str(response_data)[:500]}...")
        
        # Extract the actual data from AgentCore response
        extracted_data = response_data if isinstance(response_data, dict) else {}
        
        # Sanitize numeric fields to prevent validation errors
        if extracted_data and 'academic_background' in extracted_data:
            academic = extracted_data['academic_background']
            if 'gpa_4_scale' in academic:
                try:
                    academic['gpa_4_scale'] = float(academic['gpa_4_scale']) if academic['gpa_4_scale'] is not None else 0.0
                except (ValueError, TypeError):
                    academic['gpa_4_scale'] = 0.0
        
        # Also sanitize at root level if present
        if extracted_data and 'gpa_4_scale' in extracted_data:
            try:
                extracted_data['gpa_4_scale'] = float(extracted_data['gpa_4_scale']) if extracted_data['gpa_4_scale'] is not None else 0.0
            except (ValueError, TypeError):
                extracted_data['gpa_4_scale'] = 0.0
        
        print(f"📤 Final extracted_data keys: {list(extracted_data.keys()) if extracted_data else 'None'}")
        
        return jsonify({
            'success': True,
            'extracted_data': extracted_data,
            'agentcore_response': response_data,
            'session_id': 'autofill-' + str(hash(str(payload)) % 10000000000000)
        })
        
    except Exception as e:
        print(f"AgentCore autofill error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'extracted_data': {}
        }), 500

@app.route('/api/submit-application', methods=['POST', 'OPTIONS'])
def submit_application():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        payload = request.json
        print(f"📤 Submitting application: {payload}")
        
        response = lambda_client.invoke(
            FunctionName='sagemaker-uni-university-persona',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        print(f"📥 Lambda response: {response_payload}")
        
        return jsonify({
            'success': True,
            'response': response_payload
        })
        
    except Exception as e:
        print(f"Lambda submission error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/applications', methods=['GET', 'OPTIONS'])
def get_applications():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        # No mock data - use real applications only
        applications = []
        
        stats = {
            'total': len(applications),
            'pending': len([app for app in applications if app['status'] == 'pending']),
            'approved': len([app for app in applications if app['status'] == 'approved']),
            'rejected': len([app for app in applications if app['status'] == 'rejected'])
        }
        
        return jsonify({
            'success': True,
            'applications': applications,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/applications/status', methods=['POST', 'OPTIONS'])
def update_application_status():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        application_id = data.get('application_id')
        new_status = data.get('status')
        
        print(f"📝 Updating application {application_id} to {new_status}")
        
        # In real implementation, update DynamoDB
        # For now, just return success
        return jsonify({
            'success': True,
            'message': f'Application {application_id} updated to {new_status}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-applications', methods=['POST', 'OPTIONS'])
def list_applications():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        payload = {
            "Records": [
                {
                    "eventSource": "student-application",
                    "action": "list_applicants_v2",
                    "input": {}
                }
            ]
        }
        
        print(f"📤 Listing applications via Lambda")
        
        response = lambda_client.invoke(
            FunctionName='sagemaker-uni-university-persona',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        print(f"📥 Lambda response received")
        
        if response_payload.get('status_code') == 200:
            applications = response_payload.get('result', [])
            
            # Calculate stats
            stats = {
                'total': len(applications),
                'new': len([app for app in applications if app.get('application_status') == 'New']),
                'processing': len([app for app in applications if 'Processing' in app.get('application_status', '')]),
                'complete': len([app for app in applications if app.get('application_status') == 'Processing complete']),
                'accepted': len([app for app in applications if app.get('final_decision') == 'ACCEPT']),
                'waitlisted': len([app for app in applications if app.get('final_decision') == 'WAITLIST']),
                'rejected': len([app for app in applications if app.get('final_decision') == 'REJECT'])
            }
            
            return jsonify({
                'success': True,
                'applications': applications,
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch applications'
            }), 500
        
    except Exception as e:
        print(f"Lambda list applications error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 DRAE Platform - AgentCore Proxy Starting...")
    print("📡 Available endpoints:")
    print("  - POST /api/agentcore/search")
    print("  - POST /api/agentcore/autofill")
    print("  - POST /api/documents/upload") 
    print("  - POST /api/university-insights")
    print("  - POST /api/autofill")
    print("  - POST /api/submit-application")
    print("  - POST /api/list-applications")
    app.run(host='0.0.0.0', port=8081, debug=False)
