import React from "react";
import { useDropzone } from "react-dropzone";
import { Box, Typography, Chip } from "@mui/material";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

export default function FileDropZone({ onSelect, selectedFile }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => onSelect(files[0])
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: selectedFile ? "2px solid #1976d2" : "2px dashed gray",
        p: 5,
        textAlign: "center",
        borderRadius: 2,
        cursor: "pointer",
        background: isDragActive ? "#1e293b" : selectedFile ? "#0a1929" : "transparent",
        transition: "all 0.3s ease"
      }}
    >
      <input {...getInputProps()} />
      
      {selectedFile ? (
        <>
          <InsertDriveFileIcon sx={{ fontSize: 60, color: "#1976d2", mb: 2 }} />
          <Typography variant="h6" sx={{ color: "#1976d2", mb: 1 }}>
            {selectedFile.name}
          </Typography>
          <Chip 
            label={`${(selectedFile.size / 1024).toFixed(2)} KB`}
            size="small"
            sx={{ mb: 2 }}
          />
          <Typography variant="body2" sx={{ opacity: 0.7 }}>
            Click or drag to replace file
          </Typography>
        </>
      ) : (
        <>
          <CloudUploadIcon sx={{ fontSize: 60, color: "gray", mb: 2 }} />
          <Typography variant="h6">Drag & Drop your code file here</Typography>
          <Typography>or click to browse</Typography>
          <Typography mt={1} variant="caption">
            Supported: py, js, ts, java, cpp, zip, go
          </Typography>
        </>
      )}
    </Box>
  );
}