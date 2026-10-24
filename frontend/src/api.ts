
import type { Draft, Fact, Finding, Insights, Rule, User } from "./types";

const BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ??
  "http://127.0.0.1:8000";

const TOKEN = "inkproof.token";

export const session = {
  get: () => localStorage.getItem(TOKEN),
  set: (t: string) => localStorage.setItem(TOKEN, t),
  clear: () => localStorage.removeItem(TOKEN),
};

async function req<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string>),
  };

  const t = session.get();
  if (t) headers.Authorization = `Bearer ${t}`;

  if (init.body && !(init.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  let res: Response;

  try {
    res = await fetch(BASE + path, { ...init, headers });
  } catch {
    throw new Error(
      "Cannot reach the server. If it was idle it may take about a minute to wake up, then try again."
    );
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `Request failed (${res.status})`
    );
  }

  return res.json() as Promise<T>;
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  body: JSON.stringify(body),
});

export const api = {
  login: (email: string, password: string) =>
    req<{ token: string; user: User }>(
      "/api/auth/login",
      json("POST", { email, password })
    ),

  register: (email: string, name: string, password: string) =>
    req<{ token: string; user: User }>(
      "/api/auth/register",
      json("POST", { email, name, password })
    ),

  me: () => req<User>("/api/me"),

  library: () => req<{ rules: Rule[]; facts: Fact[] }>("/api/library"),

  patchRule: (id: string, approved: boolean) =>
    req<Rule>(`/api/rules/${id}`, json("PATCH", { approved })),

  patchFact: (id: string, value: number, valid_until: string) =>
    req<Fact & { drafts_affected: number }>(
      `/api/facts/${id}`,
      json("PATCH", { value, valid_until })
    ),

  review: (text: string, channel: string, use_ai: boolean) =>
    req<{ findings: Finding[]; note: string | null }>(
      "/api/review",
      json("POST", { text, channel, use_ai })
    ),

  importDocx: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);

    return req<{ text: string }>("/api/import/docx", {
      method: "POST",
      body: fd,
    });
  },

  // Create a new draft
  submit: (
    text: string,
    channel: string,
    intent: unknown,
    findings: Finding[]
  ) =>
    req<Draft>(
      "/api/drafts",
      json("POST", { text, channel, intent, findings })
    ),

  // Update an existing draft without creating a duplicate
  updateDraft: (
    id: number,
    text: string,
    channel: string,
    intent: unknown,
    findings: Finding[]
  ) =>
    req<Draft>(
      `/api/drafts/${id}`,
      json("PUT", { text, channel, intent, findings })
    ),

  drafts: () => req<Draft[]>("/api/drafts"),

  decide: (
    id: number,
    idx: number,
    decision: "uphold" | "waive",
    note: string
  ) =>
    req<Draft>(
      `/api/drafts/${id}/findings/${idx}/decision`,
      json("POST", { decision, note })
    ),

  finalize: (
    id: number,
    status: "approved" | "changes_requested"
  ) =>
    req<Draft>(
      `/api/drafts/${id}/finalize`,
      json("POST", { status })
    ),

  event: (
    type: "accept" | "dispute",
    rule_id: string,
    draft_id?: number
  ) =>
    req("/api/events", json("POST", { type, rule_id, draft_id })),

  remove: (id: number) =>
    req(`/api/drafts/${id}`, { method: "DELETE" }),

  insights: () => req<Insights>("/api/insights"),
};
