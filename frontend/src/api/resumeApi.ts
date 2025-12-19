import axios from "axios";

// ✅ Correct backend route
const API_URL = "http://127.0.0.1:8000/api/resume/analyze";

export const analyzeResume = async (resume: File, jobDescription: string) => {
  const formData = new FormData();
  formData.append("resume", resume);                 // backend expects `resume`
  formData.append("job_description", jobDescription); // backend expects `job_description`

  try {
    const response = await axios.post(API_URL, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  } catch (err) {
    console.error("❌ API Error:", err);
    throw err;
  }
};
