import { useCallback, useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL;

if (!BASE) {
  console.error("VITE_API_BASE_URL is not set. API calls will fail.");
}

// 90s — long enough for a Render free-tier cold start.
const DEFAULT_TIMEOUT_MS = 90_000;

async function request(path, { method = "GET", body, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`${res.status} ${res.statusText}${text ? ` — ${text.slice(0, 200)}` : ""}`);
    }

    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error(
        "Request timed out. The demo backend runs on Render's free tier and may take up to a minute to wake from sleep — please retry."
      );
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  delete: (path) => request(path, { method: "DELETE" }),
};

// Fire-and-forget warmup so the Render dyno is already waking by the
// time the user navigates to a page that fetches real data.
export function warmupBackend() {
  if (!BASE) return;
  fetch(`${BASE}/health`).catch(() => {});
}

// useApiResource: small hook that gives every page the same three-state UX
// (loading / error / data) plus a retry handle.
export function useApiResource(path) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    api
      .get(path)
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e) => setError(e.message || String(e)))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, error, loading, reload: load, setData };
}
