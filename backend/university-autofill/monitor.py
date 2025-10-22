#!/usr/bin/env python3
"""
Simple monitoring script for AgentCore performance
"""

import boto3
import json
import time
import logging
from datetime import datetime, timedelta
from config import AWS_REGION, get_agent_arn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_agent_performance():
    """Monitor agent response times and success rates"""
    
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    agent_arn = get_agent_arn()
    
    # Test payload for autofill agent
    test_payload = json.dumps({
        "s3_bucket_name": "test-bucket",
        "s3_key": "test-documents/"
    })
    
    results = []
    
    logger.info("Starting performance monitoring...")
    
    for i in range(5):
        start_time = time.time()
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                payload=test_payload,
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                'test': i + 1,
                'success': True,
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat(),
                'has_structure': isinstance(response_data, dict)
            })
            
            logger.info(f"Test {i + 1}: ✓ Success ({response_time:.2f}s)")
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                'test': i + 1,
                'success': False,
                'response_time': response_time,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.error(f"Test {i + 1}: ✗ Failed ({response_time:.2f}s) - {e}")
        
        # Wait between tests
        if i < 4:
            time.sleep(2)
    
    # Calculate statistics
    successful_tests = [r for r in results if r['success']]
    success_rate = len(successful_tests) / len(results) * 100
    
    if successful_tests:
        avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        min_response_time = min(r['response_time'] for r in successful_tests)
        max_response_time = max(r['response_time'] for r in successful_tests)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    logger.info("=== Performance Summary ===")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    logger.info(f"Average Response Time: {avg_response_time:.2f}s")
    logger.info(f"Min Response Time: {min_response_time:.2f}s")
    logger.info(f"Max Response Time: {max_response_time:.2f}s")
    
    return results

def monitor_s3_document_processing():
    """Monitor S3 document processing capabilities"""
    
    logger.info("Testing S3 document processing...")
    
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    agent_arn = get_agent_arn()
    
    # Test different S3 scenarios
    test_scenarios = [
        {
            "name": "Valid S3 path",
            "payload": {
                "s3_bucket_name": "your-documents-bucket",
                "s3_key": "student-documents/test/"
            }
        },
        {
            "name": "Non-existent bucket",
            "payload": {
                "s3_bucket_name": "non-existent-bucket-12345",
                "s3_key": "documents/"
            }
        },
        {
            "name": "Empty key path",
            "payload": {
                "s3_bucket_name": "your-documents-bucket",
                "s3_key": ""
            }
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"Testing: {scenario['name']}")
        
        try:
            payload = json.dumps(scenario['payload'])
            
            start_time = time.time()
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                payload=payload,
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            end_time = time.time()
            
            logger.info(f"  ✓ Response received ({end_time - start_time:.2f}s)")
            
            # Check if response has expected structure
            if isinstance(response_data, dict):
                if 'error' in response_data:
                    logger.info(f"  ⚠ Error response: {response_data['error']}")
                else:
                    logger.info(f"  ✓ Structured response with {len(response_data)} fields")
            
        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")

def get_cloudwatch_metrics():
    """Get CloudWatch metrics for the agent (if available)"""
    
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)
        
        # Get metrics for the last hour
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        # Try to get some basic metrics
        metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/BedrockAgentCore',
            MetricName='Invocations',
            Dimensions=[
                {
                    'Name': 'AgentId',
                    'Value': get_agent_arn().split('/')[-1]
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Sum']
        )
        
        if metrics['Datapoints']:
            total_invocations = sum(dp['Sum'] for dp in metrics['Datapoints'])
            logger.info(f"Total invocations in last hour: {total_invocations}")
        else:
            logger.info("No CloudWatch metrics available")
            
    except Exception as e:
        logger.warning(f"CloudWatch metrics not available: {e}")

if __name__ == "__main__":
    # Run performance monitoring
    results = monitor_agent_performance()
    
    # Test S3 processing
    monitor_s3_document_processing()
    
    # Try to get CloudWatch metrics
    get_cloudwatch_metrics()
    
    logger.info("Monitoring completed")
            })
            
            logger.info(f"Test {i+1}: Success - {response_time:.2f}s")
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                'test': i + 1,
                'success': False,
                'response_time': response_time,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.error(f"Test {i+1}: Failed - {e}")
        
        if i < 4:  # Don't sleep after last test
            time.sleep(2)
    
    # Calculate statistics
    successful_tests = [r for r in results if r['success']]
    success_rate = len(successful_tests) / len(results) * 100
    
    if successful_tests:
        avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        min_response_time = min(r['response_time'] for r in successful_tests)
        max_response_time = max(r['response_time'] for r in successful_tests)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    logger.info("=== Performance Summary ===")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    logger.info(f"Average Response Time: {avg_response_time:.2f}s")
    logger.info(f"Min Response Time: {min_response_time:.2f}s")
    logger.info(f"Max Response Time: {max_response_time:.2f}s")
    
    return {
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'min_response_time': min_response_time,
        'max_response_time': max_response_time,
        'results': results
    }

if __name__ == "__main__":
    monitor_agent_performance()
