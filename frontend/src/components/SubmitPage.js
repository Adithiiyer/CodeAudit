import { useState } from "react";
import { api } from "../api";
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Button,
  Paper,
  Stack
} from "@mui/material";
import FileDropZone from "./FileDropZone";
import CodeEditor from "./CodeEditor";

export default function SubmitPage() {
  const [tab, setTab] = useState(0);
  const [file, setFile] = useState(null);
  const [code, setCode] = useState("");

  // upload one file
  const uploadFile = async () => {
    const form = new FormData();
    form.append("file", file);
    await api.post("/submissions/", form);
    alert("File submitted!");
  };

  // paste code
  const uploadCode = async () => {
    const blob = new Blob([code], { type: "text/plain" });
    const fileObj = new File([blob], "pasted_code.py");
    const form = new FormData();
    form.append("file", fileObj);
    await api.post("/submissions/", form);
    alert("Code submitted!");
  };

  return (
    <Box p={4}>
      <Typography variant="h4" mb={3}>
        Submit Code for Review
      </Typography>

      <Tabs value={tab} onChange={(e, v) => setTab(v)}>
        <Tab label="Upload File" />
        <Tab label="Paste Code" />
      </Tabs>

      <Paper sx={{ p: 3, mt: 3 }}>
        {tab === 0 && (
          <Stack spacing={2}>
            <FileDropZone onSelect={setFile} />
            <Button
              variant="contained"
              disabled={!file}
              onClick={uploadFile}
            >
              Submit File
            </Button>
          </Stack>
        )}

        {tab === 1 && (
          <>
            <CodeEditor value={code} onChange={setCode} />
            <Button
              variant="contained"
              sx={{ mt: 3 }}
              disabled={!code}
              onClick={uploadCode}
            >
              Submit Code
            </Button>
          </>
        )}
      </Paper>
    </Box>
  );
}
