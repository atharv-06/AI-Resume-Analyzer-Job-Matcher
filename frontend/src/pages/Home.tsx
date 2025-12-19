import React, { useState } from "react";
import FileUploader from "../components/FileUploader";
import { analyzeResume } from "../api/resumeApi";
import ResultCard from "../components/ResultCard";

const Home: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<{
    match_score: number;
    skills_detected: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setError(null);
    if (!file || !jobDescription.trim()) {
      alert("Please upload a resume and enter a job description.");
      return;
    }

    setLoading(true);
    try {
      const data = await analyzeResume(file, jobDescription);
      setResult(data);
    } catch (err) {
      console.error("❌ Error analyzing resume:", err);
      setError("Failed to analyze resume. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "720px",
        margin: "40px auto",
        textAlign: "center",
        padding: "0 20px",
      }}
    >
      <h1 style={{ marginBottom: "20px" }}>🤖 AI Resume Analyzer & Job Matcher</h1>

      {/* ✅ Resume Uploader */}
      <FileUploader onFileSelected={(f) => setFile(f)} />
      {file && (
        <p style={{ marginTop: "10px", color: "#555" }}>
          ✅ Selected File: <b>{file.name}</b>
        </p>
      )}

      {/* ✅ Job Description Input */}
      <textarea
        placeholder="Paste job description here..."
        style={{
          width: "100%",
          height: "120px",
          marginTop: "20px",
          padding: "10px",
          fontSize: "16px",
          borderRadius: "8px",
          border: "1px solid #ccc",
          resize: "none",
        }}
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />

      {/* ✅ Analyze Button */}
      <button
        style={{
          marginTop: "20px",
          padding: "12px 24px",
          fontSize: "16px",
          cursor: "pointer",
          border: "none",
          borderRadius: "8px",
          backgroundColor: "#007bff",
          color: "#fff",
        }}
        onClick={handleAnalyze}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Resume"}
      </button>

      {/* ✅ Error Message */}
      {error && (
        <p style={{ color: "red", marginTop: "15px" }}>
          ⚠️ {error}
        </p>
      )}

      {/* ✅ Match Result */}
      {result && (
        <ResultCard
          score={result.match_score}
          skills={result.skills_detected}
        />
      )}
    </div>
  );
};

export default Home;
