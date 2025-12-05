import { useEffect, useState } from "react";
import { Box, Typography, Grid, Paper } from "@mui/material";
import { Link } from "react-router-dom";
import StatsCard from "./StatsCard";
import { getAllSubmissions } from "../api";

export default function Dashboard() {
  const [subs, setSubs] = useState([]);

  useEffect(() => {
    getAllSubmissions().then(setSubs);
  }, []);

  const avgScore =
    subs.length > 0
      ? (
          subs.reduce((sum, s) => sum + (s.review_result?.score || 0), 0) /
          subs.length
        ).toFixed(1)
      : 0;

  const totalIssues = subs.reduce((total, s) => {
    if (s.review_result?.issues) {
      const count = s.review_result.issues
        .split("\n")
        .filter((i) => i.trim() !== "").length;
      return total + count;
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
          <Typography>No submissions yet.</Typography>
        )}

        {subs.map((s) => (
          <Box key={s.id} sx={{ mt: 1 }}>
            <Link
              to={`/review/${s.id}`}
              style={{ color: "#60a5fa", textDecoration: "none" }}
            >
              <b>{s.filename}</b>
            </Link>
            {" — "}
            {s.status} (Score: {s.review_result?.score ?? "Pending"})
          </Box>
        ))}
      </Paper>
    </Box>
  );
}
