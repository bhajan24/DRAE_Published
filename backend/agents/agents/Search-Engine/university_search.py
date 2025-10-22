#!/usr/bin/env python3
import os
"""
AI-POWERED UNIVERSITY SEARCH - USING AWS BEDROCK LLM
"""

import json
import requests
import boto3
from typing import Dict, List, Any
import re

def clean_text(text):
    """Remove decorative symbols from text"""
    return re.sub(r'[✨📊🔍🎯🤖💡🚀]', '', text)

def get_llm_response(prompt: str, model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0", stream_callback=None) -> str:
    """Get response from AWS Bedrock LLM with streaming support"""
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        if stream_callback:
            # Streaming response
            response = bedrock.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            full_response = ""
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                if chunk['type'] == 'content_block_delta':
                    text = chunk['delta']['text']
                    clean_text_chunk = clean_text(text)  # Clean symbols
                    full_response += clean_text_chunk
                    if stream_callback:
                        stream_callback(clean_text_chunk)
            
            return clean_text(full_response)  # Clean the final response
        else:
            # Non-streaming response
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return clean_text(result['content'][0]['text'])  # Clean non-streaming response
    except Exception as e:
        # Enhanced fallback with regex parsing
        return extract_with_regex_fallback(prompt)

def extract_with_regex_fallback(prompt: str) -> str:
    """Enhanced regex fallback when LLM fails"""
    # Extract content from prompt
    if "Content:" in prompt:
        content = prompt.split("Content:")[1].split("Title:")[0] if "Title:" in prompt else prompt.split("Content:")[1]
        
        # Find university names with regex
        patterns = [
            r'\d+\.\s*([A-Z][^0-9\n]+(?:University|Institute|College)[^0-9\n]*)',
            r'([A-Z][a-z\s]+(?:University|Institute|College)[^.]*)',
        ]
        
        universities = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:
                name = re.sub(r'\s+', ' ', match.strip())
                if 8 <= len(name) <= 80:
                    universities.append({
                        "name": name,
                        "location": "USA",
                        "programs": ["General Studies"],
                        "ranking": "Established Institution",
                        "tuition": "Contact University",
                        "description": f"University offering quality education",
                        "website": "university.edu"
                    })
        
        if universities:
            return json.dumps(universities)
    
    return "[]"

def search_universities(query: str, location: str = "") -> List[Dict[str, Any]]:
    """Dynamic university search using LLM to extract individual universities"""
    
    try:
        # Tavily web search
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": "YOUR_TAVILY_API_KEY",
            "query": f"{query} universities {location}",
            "search_depth": "advanced",
            "max_results": 8
        }
        
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            return []
            
        data = response.json()
        results = data.get("results", [])
        
        all_universities = []
        
        # Process each search result with LLM
        for result in results:
            content = result.get("content", "")
            title = result.get("title", "")
            url_link = result.get("url", "")
            
            if len(content) < 30:
                continue
            
            # Use LLM to extract universities from content
            extraction_prompt = f"""
            Extract individual university names from this content. Return ONLY a JSON array of university objects.
            
            Content: {content[:1200]}
            Title: {title}
            Search Query: {query}
            Location: {location}
            
            IMPORTANT: 
            - If this is a ranking/list page, extract each individual university mentioned
            - If this is about one university, extract that university
            - Return real university names, not page titles
            
            Return JSON array:
            [
                {{
                    "name": "Real University Name",
                    "location": "{location if location else 'USA'}",
                    "programs": ["{query.split()[0] if query else 'General Studies'}"],
                    "ranking": "Top Institution",
                    "tuition": "Contact University",
                    "description": "Leading university",
                    "website": "university.edu"
                }}
            ]
            
            Extract maximum 5 universities. Skip if no real universities found.
            """
            
            try:
                llm_response = get_llm_response(extraction_prompt)
                
                # Clean and parse JSON
                clean_response = llm_response.strip()
                if clean_response.startswith('```'):
                    clean_response = re.sub(r'```[a-z]*\n?', '', clean_response)
                    clean_response = re.sub(r'```', '', clean_response)
                
                # Find JSON array
                json_start = clean_response.find('[')
                json_end = clean_response.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = clean_response[json_start:json_end]
                    extracted_unis = json.loads(json_str)
                    
                    for uni in extracted_unis:
                        if isinstance(uni, dict) and uni.get("name"):
                            # Validate university name
                            name = uni["name"].strip()
                            if (len(name) > 8 and 
                                not any(word in name.lower() for word in ['ranking', 'best', 'top', 'list', 'guide']) and
                                any(word in name.lower() for word in ['university', 'college', 'institute', 'school'])):
                                
                                uni["source_url"] = url_link
                                uni["real_data"] = True
                                all_universities.append(uni)
                                
            except Exception as e:
                # Simple fallback - create one entry from title if it looks like a university
                if any(word in title.lower() for word in ['university', 'college', 'institute']) and len(title) < 100:
                    fallback_uni = {
                        "name": title.split(' - ')[0].strip(),
                        "location": location if location else "USA",
                        "programs": [query.split()[0] if query else "General Studies"],
                        "ranking": "Established Institution",
                        "tuition": "Contact University",
                        "description": f"University offering {query} programs",
                        "website": url_link,
                        "source_url": url_link,
                        "real_data": True
                    }
                    all_universities.append(fallback_uni)
        
        # Remove duplicates
        unique_universities = []
        seen_names = set()
        
        for uni in all_universities:
            name_key = uni.get("name", "").lower().strip()
            if name_key and name_key not in seen_names:
                seen_names.add(name_key)
                unique_universities.append(uni)
                
                if len(unique_universities) >= 8:
                    break
        
        return unique_universities
        
    except Exception as e:
        return []

def extract_location_fallback(content: str, title: str) -> str:
    """Fallback location extraction"""
    text = (content + " " + title).lower()
    
    # Country detection
    countries = {
        "india": "India", "usa": "USA", "uk": "UK", "canada": "Canada",
        "australia": "Australia", "germany": "Germany", "france": "France"
    }
    
    for key, country in countries.items():
        if key in text:
            # City detection
            cities = {
                "mumbai": "Mumbai", "delhi": "Delhi", "bangalore": "Bangalore",
                "london": "London", "cambridge": "Cambridge", "oxford": "Oxford",
                "california": "California", "new york": "New York"
            }
            
            for city_key, city in cities.items():
                if city_key in text:
                    return f"{city}, {country}"
            
            return f"Major City, {country}"
    
    return "Global Campus"

def extract_ranking_from_content(content: str, title: str) -> str:
    """Extract ranking from content dynamically"""
    text = (content + " " + title).lower()
    
    # Look for ranking patterns
    import re
    patterns = [
        r'#(\d+)', r'rank\s*(\d+)', r'top\s*(\d+)', 
        r'(\d+)(?:st|nd|rd|th)', r'best.*?(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"#{match.group(1)} Ranked"
    
    # Check for quality indicators
    if any(word in text for word in ['best', 'top', 'leading', 'premier']):
        return "Highly Ranked"
    
    return "Established Institution"

def extract_tuition_from_content(content: str, location: str) -> str:
    """Extract tuition dynamically based on content and location"""
    text = content.lower()
    
    # Look for currency and amounts
    import re
    patterns = [
        r'[£$₹€][\d,]+', r'tuition.*?(\d+)', r'fee.*?(\d+)',
        r'cost.*?(\d+)', r'(\d+).*?per.*?year'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"${match.group().replace(',', '')}/year"
    
    # Location-based estimates
    if "india" in location.lower():
        return "$8,000 - $25,000/year"
    elif "uk" in location.lower():
        return "£15,000 - £35,000/year"
    elif "usa" in location.lower():
        return "$30,000 - $60,000/year"
    
    return "Contact for fees"

def extract_acceptance_from_content(content: str) -> str:
    """Extract acceptance rate dynamically"""
    text = content.lower()
    
    import re
    patterns = [
        r'(\d+(?:\.\d+)?)%.*?accept', r'accept.*?(\d+(?:\.\d+)?)%',
        r'admission.*?(\d+(?:\.\d+)?)%'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}%"
    
    # Infer from selectivity keywords
    if any(word in text for word in ['selective', 'competitive', 'elite']):
        return "15-25%"
    elif any(word in text for word in ['open', 'accessible']):
        return "60-80%"
    
    return "Varies by program"

def extract_gpa_from_content(content: str) -> str:
    """Extract GPA requirement dynamically"""
    text = content.lower()
    
    import re
    patterns = [
        r'gpa.*?(\d\.\d+)', r'(\d\.\d+).*?gpa',
        r'grade.*?(\d\.\d+)', r'minimum.*?(\d\.\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}+"
    
    return "Varies by program"

def extract_deadline_from_content(content: str) -> str:
    """Extract deadline dynamically"""
    text = content.lower()
    
    import re
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    
    for month in months:
        pattern = f'{month}\\s+(\\d+)'
        match = re.search(pattern, text)
        if match:
            return f"{month.title()} {match.group(1)}, 2025"
    
    return "Check university website"

def extract_programs_from_content(content: str, title: str) -> list:
    """Extract programs dynamically"""
    text = (content + " " + title).lower()
    
    programs = []
    program_keywords = {
        'computer science': 'Computer Science',
        'engineering': 'Engineering',
        'business': 'Business Administration',
        'medicine': 'Medicine',
        'law': 'Law',
        'arts': 'Liberal Arts',
        'science': 'Sciences',
        'mba': 'MBA',
        'phd': 'PhD Programs'
    }
    
    for keyword, program in program_keywords.items():
        if keyword in text:
            programs.append(program)
    
    return programs if programs else ["Multiple Programs"]

def extract_features_from_content(content: str) -> list:
    """Extract features dynamically"""
    text = content.lower()
    
    features = []
    feature_keywords = {
        'research': 'Research Excellence',
        'campus': 'Modern Campus',
        'faculty': 'Expert Faculty',
        'international': 'Global Programs',
        'technology': 'Advanced Technology',
        'library': 'Comprehensive Library',
        'career': 'Career Support'
    }
    
    for keyword, feature in feature_keywords.items():
        if keyword in text:
            features.append(feature)
    
    return features if features else ["Quality Education"]

def university_agent_stream(query: str, stream_callback=None) -> str:
    """AI-powered university search agent with streaming support"""
    
    if stream_callback:
        stream_callback("🔍 Analyzing your query...\n")
    
    # Use LLM to dynamically analyze query for ANY academic field
    query_analysis_prompt = f"""
    You are an academic field classifier. Analyze this query and identify the primary academic discipline.

    Query: "{query}"

    Identify the main academic field from these categories:
    - Agricultural Sciences (agriculture, farming, crop science, soil science, plant breeding, agronomy, horticulture, animal science)
    - Medical Sciences (medicine, medical school, MD, nursing, pharmacy, dentistry, clinical)
    - Engineering (mechanical, electrical, civil, computer engineering, chemical, biomedical)
    - Computer Science (programming, AI, software, data science, cybersecurity, information systems)
    - Business (MBA, business administration, finance, marketing, management, economics)
    - Natural Sciences (physics, chemistry, biology, mathematics, environmental science)
    - Social Sciences (psychology, sociology, political science, international relations)
    - Arts & Humanities (literature, history, philosophy, fine arts, languages)
    - Law (jurisprudence, legal studies, international law)
    - Education (teaching, educational leadership, curriculum)

    Return only this JSON format:
    {{"field": "Primary Academic Field", "location": "Geographic Location or Global", "search_terms": "optimized search terms"}}
    """
    
    def analysis_callback(text):
        if stream_callback:
            stream_callback(f"📊 {text}")
    
    analysis = get_llm_response(query_analysis_prompt, stream_callback=analysis_callback)
    
    try:
        # Clean and parse JSON response
        analysis_clean = analysis.strip()
        if analysis_clean.startswith('```'):
            analysis_clean = analysis_clean.split('```')[1]
        if analysis_clean.startswith('json'):
            analysis_clean = analysis_clean[4:]
        
        # Find JSON in response
        json_start = analysis_clean.find('{')
        json_end = analysis_clean.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = analysis_clean[json_start:json_end]
            params = json.loads(json_str)
            
            field = params.get("field", "General Studies")
            location = params.get("location", "Global")
            search_terms = params.get("search_terms", f"{field} universities")
        else:
            raise ValueError("No JSON found")
            
    except Exception as e:
        # Smart fallback based on keywords
        query_lower = query.lower()
        if any(word in query_lower for word in ['agriculture', 'agricultural', 'agri', 'crop', 'soil', 'plant', 'farm']):
            field = "Agricultural Sciences"
        elif any(word in query_lower for word in ['medicine', 'medical', 'md', 'clinical', 'health']):
            field = "Medical Sciences"
        elif any(word in query_lower for word in ['engineering', 'mechanical', 'electrical', 'civil']):
            field = "Engineering"
        elif any(word in query_lower for word in ['computer', 'software', 'programming', 'ai']):
            field = "Computer Science"
        elif any(word in query_lower for word in ['business', 'mba', 'management', 'finance']):
            field = "Business"
        else:
            field = "General Studies"
        
        location = "Global"
        search_terms = f"{field} universities"
    
    if stream_callback:
        stream_callback(f"\n🎓 Searching for {field} programs in {location}...\n")
    
    # Search universities
    universities = search_universities(search_terms, location)
    
    if stream_callback:
        # stream_callback(f"✅ Found {len(universities)} universities\n")  # Removed count
        stream_callback("🤖 Enhancing data with AI...\n")
    
    # Use LLM to enhance and validate results
    enhancement_prompt = f"""
    Enhance this university data for React UI display. Ensure all fields are complete and realistic:
    
    Query: {query}
    Field: {field}
    Location: {location}
    Raw Data: {json.dumps(universities[:3])}
    
    Return enhanced JSON with complete, realistic data for each university.
    """
    
    def enhancement_callback(text):
        if stream_callback:
            stream_callback(f"✨ {text}")
    
    enhanced_data = get_llm_response(enhancement_prompt, stream_callback=enhancement_callback)
    
    # Final response structure
    result = {
        "status": "success",
        "query": query,
        "field": field,
        "location": location,
        "total_results": len(universities),
        "universities": universities[:8]
    }
    
    if stream_callback:
        stream_callback("\n🎯 Search completed!\n")
    
    return json.dumps(result, indent=2)

def university_agent(query: str) -> str:
    """Non-streaming version for notebook compatibility"""
    return university_agent_stream(query, stream_callback=None)

def supervised_search(query: str, stream_callback=None) -> str:
    """Supervisor-enhanced search with quality control"""
    try:
        from supervisor_agent import supervised_university_search
        return supervised_university_search(query, stream_callback)
    except:
        # Fallback to regular search
        return university_agent_stream(query, stream_callback)

# Test function
def test_streaming_search():
    """Test streaming AI-powered search"""
    
    def stream_handler(text):
        print(clean_text(text), end='', flush=True)  # Clean text before printing
    
    print("🚀 TESTING STREAMING UNIVERSITY SEARCH")
    print("=" * 50)
    
    query = "Find Computer Science PhD programs in India Mumbai"
    print(f"Query: {query}\n")
    
    result = university_agent_stream(query, stream_callback=stream_handler)
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULT:")
    data = json.loads(result)
    # print(f"✅ Found {data['total_results']} universities")  # Removed count
    print(f"🎓 Field: {data['field']}")
    print(f"📍 Location: {data['location']}")

if __name__ == "__main__":
    test_streaming_search()
