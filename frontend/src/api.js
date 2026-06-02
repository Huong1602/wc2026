const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  const payload = await response.json();

  if (!payload.success) {
    throw new Error(payload.error || "API request failed");
  }

  return payload.data;
}

export function fetchTeams() {
  return request("/teams");
}

export function fetchMatches() {
  return request("/matches");
}

export function fetchPredictions() {
  return request("/predictions");
}

export function createPrediction(data) {
  return request("/predictions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

