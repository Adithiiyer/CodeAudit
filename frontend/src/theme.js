import { createTheme } from "@mui/material/styles";

export const getTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: { main: "#1E3A8A" },
      secondary: { main: "#9333EA" }
    },
    typography: {
      fontFamily: "Inter, sans-serif"
    }
  });
