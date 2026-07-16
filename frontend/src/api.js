import { useCallback, useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL;

if (!BASE) {
  console.error("VITE_API_BASE_URL is not set. API calls will fail.");
}

// 90s — long enough for a Render free-tier cold start.
const DEFAULT_TIMEOUT_MS = 90_000;

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function responseDetail(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const payload = await response.json().catch(() => null);
    if (typeof payload?.detail === "string") return payload.detail;
  }

  return response.text().catch(() => "");
}

function apiErrorMessage(status, detail) {
  if (status === 503) {
    return "SupportOps is temporarily unavailable while its data service recovers. Wait a moment, then try again.";
  }
  if (status >= 500) {
    return "SupportOps hit a server error. Try again in a moment.";
  }
  return detail || `Request failed with status ${status}.`;
}

async function request(path, { method = "GET", body, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
  if (!BASE) {
    throw new ApiError("SupportOps is missing its API configuration.");
  }

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
      const detail = await responseDetail(res);
      throw new ApiError(apiErrorMessage(res.status, detail), res.status);
    }

    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    if (err.name === "AbortError") {
      throw new ApiError(
        "SupportOps took too long to respond. The service may be waking up; please try again."
      );
    }
    if (err instanceof TypeError) {
      throw new ApiError("SupportOps could not reach its API. Check your connection and try again.");
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

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.get(path);
      setData(result);
      setError(null);
    } catch (error) {
      setError(error.message || String(error));
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, error, loading, reload: load, setData };
}
