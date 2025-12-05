import React, { useState } from "react";
import { ThemeProvider, CssBaseline, IconButton } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { getTheme } from "./theme";

import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import SubmitPage from "./components/SubmitPage";
import ReviewPage from "./components/ReviewPage";

import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

export default function App() {
  const [mode, setMode] = useState("dark");
  const theme = getTheme(mode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <Router>
        <div style={{ display: "flex" }}>
          <Sidebar />

          <div style={{ flex: 1, marginLeft: 220 }}>
            {/* Theme Toggle */}
            <div style={{ float: "right", padding: 20 }}>
              <IconButton onClick={() => setMode(mode === "light" ? "dark" : "light")}>
                {mode === "light" ? <Brightness4Icon /> : <Brightness7Icon />}
              </IconButton>
            </div>

            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/submit" element={<SubmitPage />} />
              <Route path="/review/:id" element={<ReviewPage />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}
