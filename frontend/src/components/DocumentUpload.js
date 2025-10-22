import React, { useState } from 'react';
import { 
  Card, CardContent, Typography, Button, LinearProgress,
  List, ListItem, ListItemText, ListItemIcon, Box, Chip, IconButton
} from '@mui/material';
import { CloudUpload, Description, Delete, AttachFile } from '@mui/icons-material';
import { uploadToS3 } from '../services/upload';

const DocumentUpload = ({ docs = [], setDocs, onNext, onBack, studentData }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const requiredDocs = [
    { id: 'transcripts', name: 'Academic Transcripts', required: true },
    { id: 'sop', name: 'Statement of Purpose', required: true },
    { id: 'lor', name: 'Letters of Recommendation (3)', required: true },
    { id: 'resume', name: 'Resume/CV', required: false },
    { id: 'test_scores', name: 'Test Scores', required: false }
  ];

  const handleFileUpload = async (docType, files) => {
    setUploading(true);
    const fileArray = Array.from(files);
    
    try {
      for (const file of fileArray) {
        const progressKey = `${docType}_${Date.now()}`;
        setUploadProgress(prev => ({ ...prev, [progressKey]: 0 }));
        
        // Progress simulation
        const interval = setInterval(() => {
          setUploadProgress(prev => ({
            ...prev, [progressKey]: Math.min((prev[progressKey] || 0) + 25, 90)
          }));
        }, 300);

        const studentName = studentData?.name || 'Student';
        const result = await uploadToS3(file, studentName);
        clearInterval(interval);
        
        if (result.success) {
          const newDoc = {
            id: `${docType}_${Date.now()}`,
            name: file.name,
            type: docType,
            s3Key: result.key
          };
          setDocs(prev => [...prev, newDoc]);
          setUploadProgress(prev => ({ ...prev, [progressKey]: 100 }));
          
          setTimeout(() => {
            setUploadProgress(prev => {
              const newProg = { ...prev };
              delete newProg[progressKey];
              return newProg;
            });
          }, 1000);
        }
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const deleteDoc = (docId) => {
    setDocs(prev => prev.filter(doc => doc.id !== docId));
  };

  const getDocsForType = (type) => docs.filter(doc => doc.type === type);
  const isRequired = (docType) => requiredDocs.find(d => d.id === docType)?.required;
  const allRequiredUploaded = requiredDocs.filter(d => d.required).every(d => getDocsForType(d.id).length > 0);

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>Upload Documents</Typography>
      
      <Card>
        <CardContent>
          <List>
            {requiredDocs.map((docType) => {
              const uploadedDocs = getDocsForType(docType.id);
              
              return (
                <ListItem key={docType.id} sx={{ flexDirection: 'column', alignItems: 'stretch', py: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                    <ListItemIcon>
                      <Description color={uploadedDocs.length > 0 ? "success" : "action"} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={docType.name}
                      secondary={docType.required ? 'Required' : 'Optional'}
                    />
                    <Button
                      variant="outlined"
                      component="label"
                      size="small"
                      startIcon={<CloudUpload />}
                      disabled={uploading}
                      sx={{ minWidth: 80, fontSize: '0.75rem' }}
                    >
                      Upload
                      <input
                        type="file"
                        hidden
                        multiple
                        accept=".pdf,.doc,.docx"
                        onChange={(e) => handleFileUpload(docType.id, e.target.files)}
                      />
                    </Button>
                  </Box>

                  {/* Progress bars */}
                  {Object.entries(uploadProgress).map(([key, progress]) => 
                    key.startsWith(docType.id) && (
                      <Box key={key} sx={{ mb: 1 }}>
                        <LinearProgress variant="determinate" value={progress} />
                      </Box>
                    )
                  )}

                  {/* Uploaded files */}
                  {uploadedDocs.map((doc) => (
                    <Box key={doc.id} sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      bgcolor: 'grey.100', 
                      p: 1, 
                      borderRadius: 1,
                      mb: 0.5
                    }}>
                      <AttachFile fontSize="small" />
                      <Typography variant="body2" sx={{ flexGrow: 1, ml: 1 }}>
                        {doc.name}
                      </Typography>
                      <Chip label="Uploaded" color="success" size="small" sx={{ mr: 1 }} />
                      <IconButton size="small" onClick={() => deleteDoc(doc.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  ))}
                </ListItem>
              );
            })}
          </List>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
            <Button onClick={onBack} disabled={uploading}>Back</Button>
            <Button
              variant="contained"
              onClick={onNext}
              disabled={!allRequiredUploaded || uploading}
            >
              Continue
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DocumentUpload;
