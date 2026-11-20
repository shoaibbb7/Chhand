/**
 * API client module for Chhand.
 * Pure fetch wrappers with structured error handling and abort support.
 */

const API_BASE = "/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: HTTP ${res.status}`);
  }
  return await res.json();
}

export async function analyzePoem(payload, signal = null) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || "Failed to analyze meter.";
    throw new Error(errorMsg);
  }
  return data;
}

export async function requestRewrite(payload, signal = null) {
  const res = await fetch(`${API_BASE}/rewrite`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || "Failed to generate rewrites.";
    const err = new Error(errorMsg);
    err.code = data?.error?.code;
    throw err;
  }
  return data;
}

export async function findRhymes(word, limit = 10, signal = null) {
  const res = await fetch(`${API_BASE}/rhyme`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, limit }),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || "Failed to fetch rhymes.";
    throw new Error(errorMsg);
  }
  return data;
}

export async function fetchRhymeFamilies(signal = null) {
  const res = await fetch(`${API_BASE}/rhyme/families`, { signal });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.error?.message || "Failed to load rhyme families.");
  }
  return data;
}
