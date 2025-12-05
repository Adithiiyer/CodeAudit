import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

// Submit file or pasted code
export async function submitCode(formData) {
  const res = await api.post("/submissions/", formData);
  return res.data;
}

// Fetch full analysis result
export async function getSubmission(id) {
  const res = await api.get(`/submissions/${id}`);
  return res.data;
}

// Fetch all submissions
export async function getAllSubmissions() {
  const res = await api.get("/submissions/");
  return res.data;
}
