
import type { ReactNode } from "react";
import type { Finding } from "../types";

export default function FindingCard({
  f,
  children,
}: {
  f: Finding;
  children?: ReactNode;
}) {
  const checks = Object.entries(f.checks)
    .map(([key, value]) => `${value ? "✓" : "✗"} ${key}`)
    .join(", ");

  const evidence = f.evidence;

  const evidenceLabels = {
    linked: "Evidence linked",
    expired: "Evidence expired",
    unapproved: "Evidence not approved",
    missing: "Evidence missing",
    stale: "Source document outdated",
  };

  return (
    <div className={`finding ${f.status}`}>
      <div className="row">
        <span className={`badge ${f.status}`}>
          {f.status === "confirmed" ? "CONFIRMED" : "NEEDS HUMAN REVIEW"}
        </span>

        <b>
          {f.label}: “{f.quote}”
        </b>
      </div>

      <p>{f.reason}</p>

      <p className="muted">
        Rule {f.rule_id}
        {f.fact_id ? ` · Fact ${f.fact_id}` : ""}
        {" · "}
        {f.label === "AI-suggested" ? "AI-assisted" : "Rule-based"}
        {" · checks: "}
        {checks}
      </p>

      <div className="evidence-panel">
        <h4>Evidence details</h4>

        <p>
          <b>Status:</b>{" "}
          {evidence
            ? evidenceLabels[evidence.status]
            : "Evidence metadata unavailable"}
        </p>

        {evidence?.text && (
          <p>
            <b>Supporting fact:</b> {evidence.text}
          </p>
        )}

        {evidence && (
          <>
            <p>
              <b>Fact ID:</b> {evidence.fact_id ?? "Not linked"}
              {" · "}
              <b>Version:</b> {evidence.version ?? "Unavailable"}
            </p>

            <p>
              <b>Approved:</b> {evidence.approved ? "Yes" : "No"}
              {" · "}
              <b>Expired:</b> {evidence.expired ? "Yes" : "No"}
            </p>

            <p>
              <b>Valid until:</b> {evidence.valid_until ?? "Not specified"}
            </p>

            {evidence.sources?.length > 0 && (
              <div className="source-details">
                <h4>Source documents</h4>

                {evidence.sources.map((source, index) => (
                  <div
                    key={`${source.document_id}-${index}`}
                    className="source-item"
                  >
                    <p>
                      <b>Document:</b>{" "}
                      {source.filename ?? "Document unavailable"}
                    </p>

                    <p>
                      <b>Original source quote:</b>
                    </p>

                    <blockquote>{source.source_quote}</blockquote>

                    <p>
                      <b>Document version:</b> {source.document_version}
                      {" · "}
                      <b>Current version:</b>{" "}
                      {source.current_document_version ?? "Unavailable"}
                    </p>

                    {source.stale && (
                      <p role="alert" className="source-warning">
                        ⚠ This source document is outdated. A reviewer should
                        verify the updated evidence before relying on this fact.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {!evidence && (
          <p className="muted">
            Run a fresh review to check whether evidence metadata is available.
          </p>
        )}
      </div>

      {children}
    </div>
  );
}
