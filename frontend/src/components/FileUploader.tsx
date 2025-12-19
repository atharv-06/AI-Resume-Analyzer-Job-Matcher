import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  onFileSelected: (file: File) => void;
}

const FileUploader: React.FC<Props> = ({ onFileSelected }) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelected(acceptedFiles[0]);
      }
    },
    [onFileSelected]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [] },
    multiple: false,
    onDrop
  });

  return (
    <div
      {...getRootProps()}
      style={{
        border: "2px dashed #888",
        borderRadius: "10px",
        padding: "30px",
        textAlign: "center",
        cursor: "pointer",
        color: "#555",
        backgroundColor: isDragActive ? "#f0f0f0" : "transparent"
      }}
    >
      {/* getInputProps already has correct types */}
      <input {...getInputProps()} />

      <p>📄 Drag & drop your resume here, or click to upload</p>
    </div>
  );
};

export default FileUploader;
