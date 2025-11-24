import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

function TrendsChart({ projectId }) {
  const [trendsData, setTrendsData] = useState([]);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    fetchTrends();
  }, [projectId, period]);

  const fetchTrends = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/v1/projects/${projectId}/trends?days=${period}`
      );
      setTrendsData(response.data.trends);
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  return (
    <Paper sx={{ p: 3, mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Code Quality Trends
      </Typography>
      
      <FormControl sx={{ mb: 2, minWidth: 120 }}>
        <InputLabel>Period</InputLabel>
        <Select value={period} onChange={(e) => setPeriod(e.target.value)}>
          <MenuItem value={7}>Last 7 days</MenuItem>
          <MenuItem value={30}>Last 30 days</MenuItem>
          <MenuItem value={90}>Last 90 days</MenuItem>
        </Select>
      </FormControl>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={trendsData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="overall_score" 
            stroke="#8884d8" 
            name="Overall Score"
            strokeWidth={2}
          />
          <Line 
            type="monotone" 
            dataKey="quality_score" 
            stroke="#82ca9d" 
            name="Quality"
          />
          <Line 
            type="monotone" 
            dataKey="security_score" 
            stroke="#ffc658" 
            name="Security"
          />
          <Line 
            type="monotone" 
            dataKey="maintainability_score" 
            stroke="#ff7c7c" 
            name="Maintainability"
          />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default TrendsChart;