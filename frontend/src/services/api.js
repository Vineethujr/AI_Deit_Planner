const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

function getToken() {
  return localStorage.getItem("dp_token");
}

async function request(path, { method = "GET", json, formData, auth = true } = {}) {
  const headers = {};
  if (json) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: formData ? formData : json ? JSON.stringify(json) : undefined,
  });

  let data = null;
  try {
    data = await resp.json();
  } catch {
    data = null;
  }

  if (!resp.ok) {
    const message = data?.error || `Request failed with status ${resp.status}`;
    const err = new Error(message);
    err.status = resp.status;
    err.details = data?.details;
    throw err;
  }
  return data;
}

export const api = {
  register: (payload) => request("/register", { method: "POST", json: payload, auth: false }),
  login: (payload) => request("/login", { method: "POST", json: payload, auth: false }),
  logout: () => request("/logout", { method: "POST" }),

  getProfile: () => request("/profile"),
  updateProfile: (payload) => request("/profile", { method: "PUT", json: payload }),

  generatePlan: (overrides = {}) => request("/generate-plan", { method: "POST", json: overrides }),
  listPlans: () => request("/plans"),
  getPlan: (planId) => request(`/plans/${planId}`),
  deletePlan: (planId) => request(`/plans/${planId}`, { method: "DELETE" }),

  uploadFile: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/upload", { method: "POST", formData });
  },
  listFiles: () => request("/files"),
  deleteFile: (fileId) => request(`/files/${fileId}`, { method: "DELETE" }),
};

export { getToken, API_BASE_URL };
