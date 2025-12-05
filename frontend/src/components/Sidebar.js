import React from "react";
import { Drawer, List, ListItemButton, ListItemText, Toolbar, Typography } from "@mui/material";

export default function Sidebar({ onSelect }) {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 220,
        "& .MuiDrawer-paper": {
          width: 220,
          background: "#111827",
          color: "white"
        }
      }}
    >
      <Toolbar />
      <Typography sx={{ px: 2, fontSize: 14, opacity: 0.8 }}>Navigation</Typography>

      <List>
        <ListItemButton onClick={() => onSelect("dashboard")}>
          <ListItemText primary="Dashboard" />
        </ListItemButton>

        <ListItemButton onClick={() => onSelect("submit")}>
          <ListItemText primary="Submit Code" />
        </ListItemButton>
      </List>
    </Drawer>
  );
}
