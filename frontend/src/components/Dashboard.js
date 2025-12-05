import { useEffect, useState } from "react";
import { api } from "../api";
import { Box, Typography, Grid, Paper } from "@mui/material";
import StatsCard from "./StatsCard";

export default function Dashboard() {
  const [subs, setSubs] = useState([]);

  useEffect(() => {
    api.get("/submissions/").then((res) => setSubs(res.data));
  }, []);

  const avgScore =
    subs.length > 0
      ? (
          subs.reduce((a, b) => a + (b.review_result?.score || 0), 0) / subs.length
        ).toFixed(1)
      : 0;

  // Calculate total issues by parsing the issues string
  const totalIssues = subs.reduce((total, sub) => {
    if (sub.review_result?.issues) {
      // Split by newline and filter out empty strings
      const issueList = sub.review_result.issues
        .split('\n')
        .filter(issue => issue.trim() !== '');
      return total + issueList.length;
    }
    return total;
  }, 0);

  return (
    <Box p={4}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        CodeAudit Dashboard
      </Typography>

      <Grid container spacing={2}>
        <Grid item>
          <StatsCard title="Total Submissions" value={subs.length} />
        </Grid>
        <Grid item>
          <StatsCard title="Average Score" value={avgScore} />
        </Grid>
        <Grid item>
          <StatsCard title="Total Issues Found" value={totalIssues} />
        </Grid>
      </Grid>

      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6">Recent Submissions</Typography>

        {subs.length === 0 && (
          <Typography>No submissions yet. Submit your first file!</Typography>
        )}

        {subs.map((s) => (
          <Box key={s.id} sx={{ mt: 1 }}>
            <b>{s.filename}</b> — {s.status} (Score: {s.review_result?.score || 'Pending'})
          </Box>
        ))}
      </Paper>
    </Box>
  );
}