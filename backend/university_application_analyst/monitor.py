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
    
    test_prompt = json.dumps({
        "prompt": "Quick test - please provide a brief acknowledgment."
    })
    
    results = []
    
    logger.info("Starting performance monitoring...")
    
    for i in range(5):
        start_time = time.time()
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                payload=test_prompt,
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
                'timestamp': datetime.utcnow().isoformat()
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
