import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Paper, 
  Typography, 
  Box,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText
} from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function ViewResults() {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResults();
    // Poll for results every 5 seconds if still processing
    const interval = setInterval(() => {
      if (!results || results.status === 'processing' || results.status === 'pending') {
        fetchResults();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [submissionId]);

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/results/${submissionId}`);
      setResults(response.data);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch results');
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      error: 'error',
      warning: 'warning',
      info: 'info',
      critical: 'error',
      high: 'error',
      medium: 'warning',
      low: 'info'
    };
    return colors[severity?.toLowerCase()] || 'default';
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading results...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
        <Button onClick={() => navigate('/')} sx={{ mt: 2 }}>
          ← Back to Dashboard
        </Button>
      </Container>
    );
  }

  if (results?.status === 'processing' || results?.status === 'pending') {
    return (
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Processing Your Code...
          </Typography>
          <LinearProgress sx={{ my: 2 }} />
          <Typography variant="body2" color="textSecondary">
            Status: {results.status}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {results.message || 'Your code is being analyzed. This usually takes 10-30 seconds.'}
          </Typography>
          <Button onClick={() => navigate('/')} sx={{ mt: 3 }}>
            ← Back to Dashboard
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 2 }}>
        <Button onClick={() => navigate('/')}>
          ← Back to Dashboard
        </Button>
      </Box>

      <Typography variant="h3" gutterBottom>
        Code Review Results
      </Typography>

      {/* Overall Score Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Overall Score
              </Typography>
              <Typography variant="h3" sx={{ color: getScoreColor(results.overall_score) }}>
                {results.overall_score?.toFixed(1) || 'N/A'}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                out of 100
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Quality Score
              </Typography>
              <Typography variant="h4" sx={{ color: getScoreColor(results.quality_score) }}>
                {results.quality_score?.toFixed(1) || 'N/A'}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={results.quality_score || 0} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Security Score
              </Typography>
              <Typography variant="h4" sx={{ color: getScoreColor(results.security_score) }}>
                {results.security_score?.toFixed(1) || 'N/A'}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={results.security_score || 0} 
                color="secondary"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Issues Found
              </Typography>
              <Typography variant="h4" color="error">
                {results.issues_count || 0}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Total problems
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Code Review Issues */}
      {results.ai_review?.issues && results.ai_review.issues.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Code Quality Issues
          </Typography>
          <List>
            {results.ai_review.issues.map((issue, idx) => (
              <ListItem key={idx} sx={{ 
                bgcolor: 'error.light', 
                mb: 1, 
                borderRadius: 1,
                flexDirection: 'column',
                alignItems: 'flex-start'
              }}>
                <Box sx={{ display: 'flex', width: '100%', mb: 1 }}>
                  <Chip 
                    label={issue.severity || 'warning'} 
                    color={getSeverityColor(issue.severity)}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  {issue.line && (
                    <Chip label={`Line ${issue.line}`} size="small" />
                  )}
                </Box>
                <ListItemText
                  primary={issue.message}
                  secondary={issue.category && `Category: ${issue.category}`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Security Vulnerabilities */}
      {results.security_analysis?.vulnerabilities && results.security_analysis.vulnerabilities.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom color="error">
            Security Vulnerabilities
          </Typography>
          <List>
            {results.security_analysis.vulnerabilities.map((vuln, idx) => (
              <ListItem key={idx} sx={{ 
                bgcolor: 'warning.light', 
                mb: 1, 
                borderRadius: 1,
                flexDirection: 'column',
                alignItems: 'flex-start'
              }}>
                <Box sx={{ display: 'flex', width: '100%', mb: 1 }}>
                  <Chip 
                    label={vuln.severity || vuln.issue_severity || 'medium'} 
                    color="error"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  {vuln.line && (
                    <Chip label={`Line ${vuln.line}`} size="small" />
                  )}
                </Box>
                <ListItemText
                  primary={vuln.description || vuln.issue}
                  secondary={vuln.recommendation || 'Review and fix this security issue'}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Suggestions */}
      {results.ai_review?.suggestions && results.ai_review.suggestions.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Improvement Suggestions
          </Typography>
          <List>
            {results.ai_review.suggestions.map((suggestion, idx) => (
              <ListItem key={idx} sx={{ bgcolor: 'info.light', mb: 1, borderRadius: 1 }}>
                <ListItemText primary={suggestion} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Positive Aspects */}
      {results.ai_review?.positive_aspects && results.ai_review.positive_aspects.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom color="success.main">
            What You Did Well ✓
          </Typography>
          <List>
            {results.ai_review.positive_aspects.map((aspect, idx) => (
              <ListItem key={idx} sx={{ bgcolor: 'success.light', mb: 1, borderRadius: 1 }}>
                <ListItemText primary={aspect} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Summary */}
      {results.summary && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'grey.100' }}>
          <Typography variant="h6" gutterBottom>
            Summary
          </Typography>
          <Typography variant="body1">
            {results.summary}
          </Typography>
        </Paper>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <Button 
          variant="contained" 
          onClick={() => navigate('/submit')}
        >
          Submit Another File
        </Button>
        <Button 
          variant="outlined" 
          onClick={() => window.location.reload()}
        >
          Refresh Results
        </Button>
      </Box>
    </Container>
  );
}

export default ViewResults;