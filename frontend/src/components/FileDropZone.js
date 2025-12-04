import React from "react";
import { useDropzone } from "react-dropzone";
import { Box, Typography } from "@mui/material";

export default function FileDropZone({ onSelect }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => onSelect(files[0])
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: "2px dashed gray",
        p: 5,
        textAlign: "center",
        borderRadius: 2,
        cursor: "pointer",
        background: isDragActive ? "#1e293b" : "transparent"
      }}
    >
      <input {...getInputProps()} />
      <Typography variant="h6">Drag & Drop your code file here</Typography>
      <Typography>or click to browse</Typography>
      <Typography mt={1} variant="caption">
        Supported: py, js, ts, java, cpp, zip, go
      </Typography>
    </Box>
  );
}
