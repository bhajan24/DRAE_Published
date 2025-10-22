import axios from 'axios';

export const extractDocumentData = async (studentName) => {
  try {
    // Sanitize student name to remove spaces and special characters
    const safeStudentName = studentName.replace(/\s+/g, '_').replace(/[^\w\-_.]/g, '');
    
    const payload = {
      s3_bucket_name: "aimlusecases-pvt",
      s3_key: `university-applications/personas/Student/${safeStudentName}/Docs/`
    };

    const response = await axios.post('/api/agentcore/autofill', payload);
    
    return {
      success: true,
      data: response.data.extracted_data || response.data
    };

  } catch (error) {
    console.error('AgentCore autofill failed:', error);
    return { 
      success: false, 
      error: error.message 
    };
  }
};

export default { extractDocumentData };
