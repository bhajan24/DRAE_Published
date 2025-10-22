// Test both payload types
const testPayloads = () => {
  
  // 1. Discovery/NLP Search Test
  const nlpSearchParams = {
    query: "Architecture universities Italy top ranked"
  };
  
  console.log("=== NLP SEARCH PAYLOAD ===");
  console.log("Condition: query.length > 20 =", nlpSearchParams.query.length > 20);
  
  if (nlpSearchParams.query && nlpSearchParams.query.length > 20) {
    const nlpPayload = { "query": nlpSearchParams.query };
    console.log("NLP Payload:", JSON.stringify(nlpPayload, null, 2));
  }
  
  // 2. Regular Structured Search Test  
  const structuredSearchParams = {
    field_of_study: "Computer Science",
    location_preference: "USA", 
    gpa: "3.8",
    research_interests: ["AI", "ML"]
  };
  
  console.log("\n=== STRUCTURED SEARCH PAYLOAD ===");
  console.log("Condition: No long query, has structured data");
  
  const structuredPayload = {
    "query": `Find ${structuredSearchParams.field_of_study} programs in ${structuredSearchParams.location_preference} with GPA ${structuredSearchParams.gpa}`,
    "student_profile": {
      "name": "Student User",
      "gpa": parseFloat(structuredSearchParams.gpa) || 0,
      "location_preference": structuredSearchParams.location_preference,
      "interests": structuredSearchParams.research_interests || [],
      "degree_level": "Masters",
      "field_of_study": structuredSearchParams.field_of_study
    },
    "filters": {
      "program_type": "masters",
      "location": structuredSearchParams.location_preference,
      "field": structuredSearchParams.field_of_study
    }
  };
  
  console.log("Structured Payload:", JSON.stringify(structuredPayload, null, 2));
  
  // 3. Edge Case Test - Short query
  console.log("\n=== EDGE CASE: SHORT QUERY ===");
  const shortQuery = { query: "MIT" };
  console.log("Short query length:", shortQuery.query.length);
  console.log("Will use structured search:", shortQuery.query.length <= 20);
};

testPayloads();
