// Typed client for the FastAPI backend.
// Base URL comes from NEXT_PUBLIC_API_URL (see .env.local); defaults to local dev.
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    throw new Error(`API GET ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export { API_BASE };
