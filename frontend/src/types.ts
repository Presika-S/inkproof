
export type Role = "writer" | "reviewer";

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
}

export interface EvidenceSource {
  document_id: string;
  filename: string | null;
  source_quote: string;
  document_version: number;
  current_document_version: number | null;
  stale: boolean;
}

export interface Finding {
  id: string;
  rule_id: string;
  fact_id: string | null;
  label: string;
  quote: string;
  reason: string;
  fix: string | null;
  status: "confirmed" | "human";
  checks: {
    rule: boolean;
    quote: boolean;
    fact: boolean;
    context: boolean;
  };
  evidence?: {
    status: "linked" | "expired" | "unapproved" | "missing" | "stale";
    fact_id: string | null;
    text: string | null;
    version: number | null;
    approved: boolean;
    valid_until: string | null;
    expired: boolean;
    sources: EvidenceSource[];
  };
  dec?: { d: "uphold" | "waive"; note: string } | null;
  disputed?: boolean;
}

export interface Draft {
  id: number;
  title: string;
  text: string;
  channel: string;
  intent: Intent;
  status: string;
  findings: Finding[];
  created_at: string;
}

export interface Intent {
  cta: string;
  claims: string;
}

export interface Rule {
  id: string;
  name: string;
  version: number;
  approved: boolean;
}

export interface Fact {
  id: string;
  text: string;
  value: number;
  unit: string;
  valid_until: string;
  version: number;
  expired: boolean;
  owner: string;
}

export interface Insights {
  health: {
    rule_id: string;
    name: string;
    flagged: number;
    overridden: number;
    rate: number;
    unclear: boolean;
  }[];
  fact_changes: {
    fact_id: string;
    old: string;
    new: string;
    drafts_affected: number;
    at: string;
  }[];
  history: {
    type: string;
    rule_id: string | null;
    draft_id: number | null;
    note: string;
    at: string;
  }[];
}
