import React, { useState, useRef } from 'react';
import axios from 'axios';
import { 
  Container, 
  Paper, 
  Typography, 
  Button,
  Box,
  TextField,
  Alert,
  CircularProgress,
  LinearProgress,
  Tabs,
  Tab,
  TextareaAutosize
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CodeIcon from '@mui/icons-material/Code';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function SubmitCode() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [submissionId, setSubmissionId] = useState(null);
  const [tabValue, setTabValue] = useState(0); // 0 = upload, 1 = paste
  const [pastedCode, setPastedCode] = useState('');
  const [fileName, setFileName] = useState('code.py');
  const [language, setLanguage] = useState('python');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    processFile(file);
  };

  const processFile = (file) => {
    if (!file) return;

    // Check file extension
    const validExtensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go', '.zip'];
    const fileExt = '.' + file.name.split('.').pop();
    
    if (!validExtensions.includes(fileExt.toLowerCase())) {
      setMessage({
        type: 'error',
        text: `Unsupported file type. Supported: ${validExtensions.join(', ')}`
      });
      return;
    }

    setSelectedFile(file);
    setMessage(null);
    setSubmissionId(null);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);

    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/submit`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      setSubmissionId(response.data.submission_id);
      setMessage({ 
        type: 'success', 
        text: `File submitted successfully! Submission ID: ${response.data.submission_id}` 
      });
      
      // Auto-navigate to results after 2 seconds
      setTimeout(() => {
        navigate(`/results/${response.data.submission_id}`);
      }, 2000);

    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: `Upload failed: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      setUploading(false);
    }
  };

  const handlePasteSubmit = async () => {
    if (!pastedCode.trim()) {
      setMessage({ type: 'error', text: 'Please paste some code first' });
      return;
    }

    if (!fileName.trim()) {
      setMessage({ type: 'error', text: 'Please enter a filename' });
      return;
    }

    setUploading(true);
    setMessage(null);

    // Create a blob from the pasted code
    const blob = new Blob([pastedCode], { type: 'text/plain' });
    const file = new File([blob], fileName, { type: 'text/plain' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/submit`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      setSubmissionId(response.data.submission_id);
      setMessage({ 
        type: 'success', 
        text: `Code submitted successfully! Submission ID: ${response.data.submission_id}` 
      });
      
      // Auto-navigate to results after 2 seconds
      setTimeout(() => {
        navigate(`/results/${response.data.submission_id}`);
      }, 2000);

    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: `Submission failed: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      setUploading(false);
    }
  };

  const handleBatchUpload = async () => {
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }

    if (!selectedFile.name.endsWith('.zip')) {
      setMessage({ type: 'error', text: 'Batch upload requires a .zip file' });
      return;
    }

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('project_name', selectedFile.name.replace('.zip', ''));

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/submit-batch`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      setMessage({ 
        type: 'success', 
        text: `Batch submitted! Processing ${response.data.total_files} files. Batch ID: ${response.data.batch_id}` 
      });

    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: `Batch upload failed: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Submit Code for Review
        </Typography>
        
        <Typography variant="body1" color="textSecondary" paragraph>
          Upload a file, drag & drop, or paste your code for AI-powered analysis.
        </Typography>

        {/* Tabs for Upload vs Paste */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab icon={<UploadFileIcon />} label="Upload/Drop File" />
            <Tab icon={<CodeIcon />} label="Paste Code" />
          </Tabs>
        </Box>

        {/* Tab 0: Upload/Drop File */}
        {tabValue === 0 && (
          <>
            {/* Drag & Drop Zone */}
            <Box
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              sx={{
                border: dragOver ? '3px dashed #1976d2' : '2px dashed #ccc',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                bgcolor: dragOver ? '#e3f2fd' : '#fafafa',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                mb: 3,
                '&:hover': {
                  bgcolor: '#f5f5f5',
                  borderColor: '#1976d2'
                }
              }}
              onClick={handleBrowseClick}
            >
              <CloudUploadIcon sx={{ fontSize: 60, color: dragOver ? '#1976d2' : '#999', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {dragOver ? 'Drop your file here' : 'Drag & Drop your code file here'}
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                or click to browse
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Supported: .py, .js, .jsx, .ts, .tsx, .java, .cpp, .c, .go, .zip
              </Typography>
            </Box>

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.c,.go,.zip"
              style={{ display: 'none' }}
              type="file"
              onChange={handleFileSelect}
            />

            {/* Selected File Display */}
            {selectedFile && (
              <Box sx={{ mb: 3 }}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Selected:</strong> {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </Typography>
                </Alert>
              </Box>
            )}

            {/* Upload Buttons */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFile || uploading || selectedFile?.name.endsWith('.zip')}
                fullWidth
                size="large"
              >
                {uploading ? 'Uploading...' : 'Submit Single File'}
              </Button>

              <Button
                variant="contained"
                color="secondary"
                onClick={handleBatchUpload}
                disabled={!selectedFile || uploading || !selectedFile?.name.endsWith('.zip')}
                fullWidth
                size="large"
              >
                {uploading ? 'Uploading...' : 'Submit Batch (Zip)'}
              </Button>
            </Box>
          </>
        )}

        {/* Tab 1: Paste Code */}
        {tabValue === 1 && (
          <>
            {/* Language Selection */}
            <Box sx={{ mb: 2 }}>
              <TextField
                select
                label="Language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                fullWidth
                SelectProps={{ native: true }}
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="c">C</option>
                <option value="go">Go</option>
              </TextField>
            </Box>

            {/* Filename Input */}
            <Box sx={{ mb: 2 }}>
              <TextField
                label="Filename"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                fullWidth
                placeholder="e.g., my_code.py"
                helperText="Enter a filename with extension"
              />
            </Box>

            {/* Code Text Area */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" gutterBottom>
                Paste your code here:
              </Typography>
              <TextField
                multiline
                rows={15}
                value={pastedCode}
                onChange={(e) => setPastedCode(e.target.value)}
                placeholder="# Paste your code here
def hello_world():
    print('Hello, World!')

hello_world()"
                fullWidth
                variant="outlined"
                sx={{
                  '& .MuiInputBase-root': {
                    fontFamily: 'monospace',
                    fontSize: '14px'
                  }
                }}
              />
              <Typography variant="caption" color="textSecondary">
                {pastedCode.length} characters
              </Typography>
            </Box>

            {/* Submit Button */}
            <Button
              variant="contained"
              onClick={handlePasteSubmit}
              disabled={!pastedCode.trim() || uploading}
              fullWidth
              size="large"
            >
              {uploading ? 'Submitting...' : 'Submit Code'}
            </Button>
          </>
        )}

        {/* Progress Bar */}
        {uploading && (
          <Box sx={{ mb: 3, mt: 3 }}>
            <LinearProgress />
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1, textAlign: 'center' }}>
              Uploading and processing your code...
            </Typography>
          </Box>
        )}

        {/* Messages */}
        {message && (
          <Alert severity={message.type} sx={{ mt: 3 }}>
            {message.text}
          </Alert>
        )}

        {/* Instructions */}
        <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50', mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            <strong>Three Ways to Submit:</strong>
          </Typography>
          <Typography variant="body2" component="div">
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li><strong>Upload:</strong> Click or drag & drop a file</li>
              <li><strong>Paste:</strong> Copy code directly into the editor</li>
              <li><strong>Batch:</strong> Upload a .zip file with multiple files</li>
            </ul>
          </Typography>
        </Paper>

        {/* Navigation */}
        <Box sx={{ mt: 3 }}>
          <Button onClick={() => navigate('/')}>
            ← Back to Dashboard
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default SubmitCode;