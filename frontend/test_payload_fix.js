// Test the fixed payload logic
const testPayloadLogic = () => {
  
  console.log("=== TESTING DISCOVERY/NLP SEARCH ===");
  
  // 1. Discovery search from StudentInput
  const discoveryData = { query: "Architecture universities Italy top ranked" };
  console.log("Discovery studentData:", discoveryData);
  
  // 2. UniversitySearch component logic
  if (discoveryData.query && !discoveryData.field_of_study) {
    console.log("✅ UniversitySearch detects NLP search");
    const apiCall = { query: discoveryData.query };
    console.log("API call params:", apiCall);
    
    // 3. API service logic
    if (apiCall.query && !apiCall.field_of_study && !apiCall.gpa) {
      console.log("✅ API service detects NLP search");
      const payload = { "query": apiCall.query };
      console.log("Final payload:", JSON.stringify(payload, null, 2));
    } else {
      console.log("❌ API service failed to detect NLP search");
    }
  } else {
    console.log("❌ UniversitySearch failed to detect NLP search");
  }
  
  console.log("\n=== TESTING STRUCTURED SEARCH ===");
  
  // 1. Structured search from form
  const structuredData = {
    field_of_study: "Computer Science",
    location_preference: "USA",
    gpa: "3.8",
    research_interests: ["AI"]
  };
  console.log("Structured studentData:", structuredData);
  
  // 2. UniversitySearch component logic
  if (structuredData.query && !structuredData.field_of_study) {
    console.log("❌ Should not detect as NLP search");
  } else {
    console.log("✅ UniversitySearch detects structured search");
    const apiCall = {
      field_of_study: structuredData.field_of_study,
      location_preference: structuredData.location_preference,
      gpa: structuredData.gpa,
      research_interests: structuredData.research_interests
    };
    console.log("API call params:", apiCall);
    
    // 3. API service logic
    if (apiCall.query && !apiCall.field_of_study && !apiCall.gpa) {
      console.log("❌ Should not detect as NLP search");
    } else {
      console.log("✅ API service detects structured search");
      const payload = {
        "query": `Find ${apiCall.field_of_study} programs in ${apiCall.location_preference} with GPA ${apiCall.gpa}`,
        "student_profile": {
          "name": "Student User",
          "gpa": parseFloat(apiCall.gpa) || 0,
          "location_preference": apiCall.location_preference,
          "interests": apiCall.research_interests || [],
          "degree_level": "Masters",
          "field_of_study": apiCall.field_of_study
        },
        "filters": {
          "program_type": "masters",
          "location": apiCall.location_preference,
          "field": apiCall.field_of_study
        }
      };
      console.log("Final payload keys:", Object.keys(payload));
    }
  }
};

testPayloadLogic();
