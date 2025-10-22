import axios from 'axios';

const apiService = {
  searchUniversities: async (searchParams, onLogUpdate) => {
    const sessionId = `search-${Date.now()}`;
    
    const logUpdate = (agent, message, details = null) => {
      const log = {
        timestamp: new Date().toLocaleTimeString(),
        type: 'info',
        agent,
        message,
        details
      };
      if (onLogUpdate) onLogUpdate(log);
    };

    // Discovery/NLP search - send only the query
    if (searchParams.query && !searchParams.field_of_study && !searchParams.gpa) {
      const payload = { "query": searchParams.query };
      
      logUpdate('DiscoveryAgent', 'Processing natural language query', { query: searchParams.query });
      
      try {
        const response = await axios.post('/api/agentcore/search', payload);
        
        return {
          data: {
            success: true,
            universities: response.data.universities || [],
            agentcore_response: response.data.agentcore_response,
            session_id: response.data.session_id || sessionId,
            search_metadata: response.data.search_metadata || {
              query: payload.query,
              results_count: response.data.universities?.length || 0,
              search_type: "Discovery NLP Search"
            }
          }
        };
      } catch (error) {
        console.error('Discovery search error:', error);
        throw error;
      }
    }

    // Regular structured search
    logUpdate('SearchAgent', 'Initializing university search request', { sessionId, searchParams });
    
    const payload = {
      "query": `Find ${searchParams.field_of_study} programs in ${searchParams.location_preference} with GPA ${searchParams.gpa}`,
      "student_profile": {
        "name": "Student User",
        "gpa": parseFloat(searchParams.gpa) || 0,
        "location_preference": searchParams.location_preference,
        "interests": searchParams.research_interests || [],
        "degree_level": "Masters",
        "field_of_study": searchParams.field_of_study
      },
      "filters": {
        "program_type": "masters",
        "location": searchParams.location_preference,
        "field": searchParams.field_of_study
      }
    };

    try {
      const response = await axios.post('/api/agentcore/search', payload);
      
      return {
        data: {
          success: true,
          universities: response.data.universities || [],
          agentcore_response: response.data.agentcore_response,
          session_id: response.data.session_id || sessionId,
          search_metadata: response.data.search_metadata || {
            query: payload.query,
            results_count: response.data.universities?.length || 0,
            search_type: "Structured Search"
          }
        }
      };
    } catch (error) {
      console.error('Search error:', error);
      throw error;
    }
  },

  getUniversityInsights: async (universityName, studentProfile) => {
    const payload = {
      "university_name": universityName,
      "student_profile": studentProfile,
      "insights_requested": [
        "admission_requirements",
        "application_process", 
        "deadlines",
        "scholarships",
        "campus_life",
        "placement_statistics"
      ]
    };

    try {
      const response = await axios.post('/api/university-insights', payload);
      return response.data;
    } catch (error) {
      console.error('Insights error:', error);
      throw error;
    }
  },

  uploadDocument: async (formDataOrFile, options = {}) => {
    let formData;
    
    // Check if it's already FormData or a file
    if (formDataOrFile instanceof FormData) {
      formData = formDataOrFile;
    } else {
      // It's a file, create FormData
      formData = new FormData();
      formData.append('file', formDataOrFile);
      formData.append('document_type', options.documentType || 'transcript');
      formData.append('student_name', options.studentName || 'Student User');
    }

    try {
      const response = await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: options.onUploadProgress
      });
      return response.data;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },

  autoFillForm: async (documents, formFields) => {
    const payload = {
      documents: documents,
      form_fields: formFields
    };

    try {
      const response = await axios.post('/api/autofill', payload);
      return response.data;
    } catch (error) {
      console.error('Autofill error:', error);
      throw error;
    }
  }
};

export default apiService;
