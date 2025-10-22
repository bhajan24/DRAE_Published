import React, { useState } from 'react';
import { Button, Box, Typography, Alert } from '@mui/material';
import { uploadToS3 } from '../services/upload';

const TestUpload = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTestUpload = async () => {
    setLoading(true);
    setResult(null);

    try {
      // Create a test file
      const testContent = 'This is a test document for university application';
      const testFile = new File([testContent], 'test-transcript.pdf', {
        type: 'application/pdf'
      });

      console.log('🧪 Testing upload with:', {
        fileName: testFile.name,
        fileSize: testFile.size,
        fileType: testFile.type
      });

      const uploadResult = await uploadToS3(testFile, 'test-student');
      
      setResult({
        success: uploadResult.success,
        message: uploadResult.success 
          ? `✅ Upload successful! File uploaded to: ${uploadResult.key}`
          : `❌ Upload failed: ${uploadResult.error}`,
        details: uploadResult
      });

    } catch (error) {
      setResult({
        success: false,
        message: `❌ Error: ${error.message}`,
        details: { error: error.message }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        Upload Test
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={handleTestUpload}
        disabled={loading}
        sx={{ mb: 2 }}
      >
        {loading ? 'Testing Upload...' : 'Test Upload to S3'}
      </Button>

      {result && (
        <Alert severity={result.success ? 'success' : 'error'} sx={{ mb: 2 }}>
          {result.message}
        </Alert>
      )}

      {result && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1,
            fontSize: '0.8rem',
            overflow: 'auto'
          }}>
            {JSON.stringify(result.details, null, 2)}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default TestUpload;
