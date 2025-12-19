import React from "react";

interface Props {
  score: number;
  skills: string[];
}

const ResultCard: React.FC<Props> = ({ score, skills }) => {
  return (
    <div style={{ marginTop: "30px", textAlign: "center" }}>
      <h2>🎯 Match Score: {score}%</h2>
      <h3>Detected Skills:</h3>
      <p>{skills.length ? skills.join(", ") : "No skills detected"}</p>
    </div>
  );
};

export default ResultCard;
