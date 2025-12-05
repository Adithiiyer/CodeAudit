import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getSubmission } from "../api";
import { Box, Typography, Paper, Divider } from "@mui/material";

export default function ReviewPage() {
  const { id } = useParams();
  const [sub, setSub] = useState(null);

  useEffect(() => {
    getSubmission(id).then(setSub);
  }, [id]);

  if (!sub) return <Typography p={4}>Loading...</Typography>;

  const r = sub.review_result;

  // -------- ISSUE COUNT --------
  const issueLines = r?.issues
    ? r.issues.split("\n").filter((i) => i.trim() !== "")
    : [];

  const issueCount = issueLines.length;

  // -------- FORMAT LLM ANALYSIS --------
  const formattedLLM =
    r?.summary
      ?.replace(/```/g, "")
      .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
      .replace(/\n/g, "<br/>") || "";

  // -------- SUGGESTIONS --------
  const suggestions =
    r?.summary_json?.suggestions && Array.isArray(r.summary_json.suggestions)
      ? r.summary_json.suggestions
      : [];

  return (
    <Box p={4}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Review for: {sub.filename}
      </Typography>

      <Paper sx={{ p: 4 }}>
        {/* SCORE */}
        <Typography variant="h6">Score:</Typography>
        <Typography sx={{ mb: 2 }}>{r?.score}</Typography>

        <Divider sx={{ my: 2 }} />

        {/* ISSUES */}
        <Typography variant="h6">Issues ({issueCount}):</Typography>

        {issueCount === 0 ? (
          <Typography sx={{ mt: 1, opacity: 0.8 }}>No issues found 🎉</Typography>
        ) : (
          <pre
            style={{
              whiteSpace: "pre-wrap",
              marginTop: "10px",
              fontSize: "1rem",
            }}
          >
            {issueLines.join("\n")}
          </pre>
        )}

        <Divider sx={{ my: 3 }} />

        {/* LLM ANALYSIS */}
        <Typography variant="h6" sx={{ mb: 1 }}>
          LLM Analysis:
        </Typography>

        <Paper
          sx={{
            p: 2,
            mt: 1,
            background: "#111",
            color: "white",
            whiteSpace: "pre-wrap",
            lineHeight: 1.7,
            fontSize: "1rem",
          }}
        >
          {/* Render the analysis markdown */}
          <div
            dangerouslySetInnerHTML={{
              __html: formattedLLM,
            }}
          />

          {/* INLINE SUGGESTIONS BELOW PERFORMANCE */}
          {suggestions.length > 0 && (
            <div style={{ marginTop: "25px" }}>
              <b>SUGGESTIONS:</b>
              <br />

              {suggestions.map((s, idx) => (
                <div key={idx} style={{ marginTop: "8px" }}>
                  • {s}
                </div>
              ))}
            </div>
          )}
        </Paper>
      </Paper>
    </Box>
  );
}
