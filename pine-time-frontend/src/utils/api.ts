import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1", // Adjust if your API base path is different
  timeout: 10000,
  withCredentials: true, // Set to true if using cookies for auth, false for JWT in headers
});

// Optionally: Attach JWT token if stored in localStorage/sessionStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Optionally: Add error handling/refresh logic here

export default api;
