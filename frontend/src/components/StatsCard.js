import { Card, CardContent, Typography } from "@mui/material";

export default function StatsCard({ title, value }) {
  return (
    <Card sx={{ minWidth: 200, textAlign: "center", p: 1 }}>
      <CardContent>
        <Typography variant="subtitle1">{title}</Typography>
        <Typography variant="h4" sx={{ mt: 1 }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}
