import type { ReactNode } from "react";
import type { Finding } from "../types";

export default function FindingCard({ f, children }: { f: Finding; children?: ReactNode }) {
  const checks = Object.entries(f.checks).map(([k, v]) => `${v ? "✓" : "✗"} ${k}`).join(", ");
  return (
    <div className={`finding ${f.status}`}>
      <div className="row">
        <span className={`badge ${f.status}`}>{f.status === "confirmed" ? "CONFIRMED" : "NEEDS HUMAN REVIEW"}</span>
        <b>{f.label}: “{f.quote}”</b>
      </div>
      <p>{f.reason}</p>
      <p className="muted">
        Rule {f.rule_id}{f.fact_id ? ` · Fact ${f.fact_id}` : ""} · {f.label === "AI-suggested" ? "AI-assisted" : "Rule-based"} · checks: {checks}
      </p>
      {children}
    </div>
  );
}
