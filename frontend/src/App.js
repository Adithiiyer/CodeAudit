import React, { useState } from "react";
import { ThemeProvider, CssBaseline, IconButton } from "@mui/material";
import { getTheme } from "./theme";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import SubmitPage from "./components/SubmitPage";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [mode, setMode] = useState("dark");

  const theme = getTheme(mode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <div style={{ display: "flex" }}>
        <Sidebar onSelect={setPage} />

        <div style={{ flex: 1, marginLeft: 220 }}>
          {/* Light/Dark Toggle */}
          <div style={{ float: "right", padding: 20 }}>
            <IconButton onClick={() => setMode(mode === "light" ? "dark" : "light")}>
              {mode === "light" ? <Brightness4Icon /> : <Brightness7Icon />}
            </IconButton>
          </div>

          {page === "dashboard" && <Dashboard />}
          {page === "submit" && <SubmitPage />}
        </div>
      </div>
    </ThemeProvider>
  );
}
