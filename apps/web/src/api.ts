const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const demoTokens = {
  admin: "admin-token",
  developer: "developer-token",
  approver: "approver-token",
  auditor: "auditor-token",
} as const;

export type DemoRole = keyof typeof demoTokens;

export function getToken(): string {
  return localStorage.getItem("agentguard_token") || demoTokens.admin;
}

export function setDemoRole(role: DemoRole): void {
  localStorage.setItem("agentguard_token", demoTokens[role]);
}

async function request(path: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${getToken()}`);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export function apiGet(path: string) {
  return request(path);
}

export function apiPost(path: string, body: unknown) {
  return request(path, { method: "POST", body: JSON.stringify(body) });
}

export function apiPatch(path: string, body: unknown) {
  return request(path, { method: "PATCH", body: JSON.stringify(body) });
}

export async function apiDownload(path: string, filename: string): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!response.ok) throw new Error(await response.text());
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
