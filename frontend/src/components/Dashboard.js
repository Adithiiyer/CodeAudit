import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Container, 
  Paper, 
  Typography, 
  Grid, 
  Card, 
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Box
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function Dashboard() {
  const [stats, setStats] = useState({
    totalSubmissions: 0,
    averageScore: 0,
    totalIssues: 0
  });
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/dashboard/stats`);
      setStats(response.data.stats);
      setRecentSubmissions(response.data.recent_submissions);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: 'success',
      processing: 'warning',
      pending: 'info',
      failed: 'error'
    };
    return colors[status] || 'default';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h3" gutterBottom sx={{ mb: 4 }}>
        CodeAudit Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Submissions
              </Typography>
              <Typography variant="h4">
                {stats.totalSubmissions}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Score
              </Typography>
              <Typography variant="h4" sx={{ color: getScoreColor(stats.averageScore) }}>
                {stats.averageScore.toFixed(1)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Issues Found
              </Typography>
              <Typography variant="h4" color="error">
                {stats.totalIssues}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Submit Button */}
      <Box sx={{ mb: 4 }}>
        <Button 
          variant="contained" 
          size="large"
          onClick={() => navigate('/submit')}
        >
          Submit New Code
        </Button>
      </Box>

      {/* Recent Submissions Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Recent Submissions
        </Typography>
        
        {recentSubmissions.length === 0 ? (
          <Typography color="textSecondary" sx={{ py: 4, textAlign: 'center' }}>
            No submissions yet. Submit your first file!
          </Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Filename</TableCell>
                  <TableCell>Language</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Submitted</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentSubmissions.map((submission) => (
                  <TableRow key={submission.id}>
                    <TableCell>{submission.filename}</TableCell>
                    <TableCell>
                      <Chip label={submission.language} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={submission.status} 
                        color={getStatusColor(submission.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {submission.created_at ? 
                        new Date(submission.created_at).toLocaleString() : 
                        'N/A'
                      }
                    </TableCell>
                    <TableCell>
                      {submission.status === 'completed' ? (
                        <Button 
                          size="small" 
                          onClick={() => navigate(`/results/${submission.id}`)}
                        >
                          View Results
                        </Button>
                      ) : (
                        <Typography variant="body2" color="textSecondary">
                          {submission.status === 'processing' ? 'Processing...' : 'Pending'}
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Container>
  );
}

export default Dashboard;