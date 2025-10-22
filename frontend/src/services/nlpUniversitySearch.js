export const searchUniversitiesNLP = async (searchQuery, studentProfile) => {
  try {
    const response = await fetch('/api/agentcore/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        searchQuery: searchQuery,
        studentProfile: studentProfile,
        searchType: "nlp_based"
      })
    });

    if (!response.ok) {
      throw new Error(`Search failed: ${response.status}`);
    }

    const result = await response.json();

    return {
      success: true,
      universities: result.universities || [],
      searchPayload: result.searchPayload || {
        search_criteria: extractSearchCriteria(searchQuery),
        student_match: studentProfile,
        nlp_query: searchQuery,
        search_timestamp: new Date().toISOString()
      },
      nlpAnalysis: result.nlpAnalysis || {
        original_query: searchQuery,
        extracted_fields: extractSearchCriteria(searchQuery),
        intent: "university_search",
        confidence: 0.9
      }
    };

  } catch (error) {
    console.error('AgentCore search failed:', error);
    
    // Fallback to local processing
    return fallbackSearch(searchQuery, studentProfile);
  }
};

function extractSearchCriteria(query) {
  const criteria = {};
  const queryLower = query.toLowerCase();
  
  // Extract program
  const programs = ["computer science", "cs", "engineering", "business", "mba", "data science", "ai", "machine learning"];
  for (const program of programs) {
    if (queryLower.includes(program)) {
      criteria.program = program;
      break;
    }
  }
  
  // Extract location
  const locations = ["usa", "us", "canada", "uk", "germany", "california", "new york", "boston"];
  for (const location of locations) {
    if (queryLower.includes(location)) {
      criteria.location = location;
      break;
    }
  }
  
  // Extract preferences
  if (queryLower.includes("top") || queryLower.includes("best")) {
    criteria.ranking_preference = "high";
  }
  
  return criteria;
}

function fallbackSearch(searchQuery, studentProfile) {
  const searchPayload = {
    search_criteria: extractSearchCriteria(searchQuery),
    student_match: studentProfile,
    nlp_query: searchQuery,
    search_timestamp: new Date().toISOString(),
    fallback_mode: true
  };

  const universities = [
    {
      id: "stanford",
      name: "Stanford University",
      location: "California, USA",
      programs: ["Computer Science", "AI", "Data Science"],
      ranking: 1,
      match_score: 0.95,
      match_reasons: ["Top CS program", "Strong AI research", "Excellent match for your profile"]
    },
    {
      id: "mit", 
      name: "MIT",
      location: "Massachusetts, USA",
      programs: ["Computer Science", "Engineering", "AI"],
      ranking: 2,
      match_score: 0.92,
      match_reasons: ["World-class CS program", "Leading AI research", "Strong technical focus"]
    },
    {
      id: "cmu",
      name: "Carnegie Mellon University",
      location: "Pennsylvania, USA", 
      programs: ["Computer Science", "Machine Learning", "Robotics"],
      ranking: 3,
      match_score: 0.88,
      match_reasons: ["Excellent ML program", "Strong industry connections", "Good fit for your background"]
    }
  ];

  return {
    success: true,
    universities: universities,
    searchPayload: searchPayload,
    nlpAnalysis: {
      original_query: searchQuery,
      extracted_fields: extractSearchCriteria(searchQuery),
      intent: "university_search",
      confidence: 0.8,
      fallback_mode: true
    }
  };
}

export default { searchUniversitiesNLP };
