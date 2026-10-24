import { useEffect, useState } from "react";
import { api } from "../api";
import type { Insights as I } from "../types";

export default function Insights() {
  const [d, setD] = useState<I | null>(null);
  useEffect(() => { api.insights().then(setD); }, []);
  if (!d) return <p className="muted">Loading…</p>;
  return (
    <div className="grid">
      <div className="card">
        <h2>Rule Health</h2>
        <div className="scroll"><table>
          <thead><tr><th>Rule</th><th>Flagged</th><th>Waived or disputed</th><th>Rate</th></tr></thead>
          <tbody>{d.health.map((h) => (
            <tr key={h.rule_id}><td>{h.rule_id}</td><td>{h.flagged}</td><td>{h.overridden}</td><td>{h.rate}%{h.unclear ? " · possibly unclear" : ""}</td></tr>
          ))}</tbody>
        </table></div>
        <p className="muted">Rules flagged often and overridden often are marked as possibly unclear.</p>
      </div>
      <div>
        <div className="card">
          <h2>Fact changes</h2>
          {d.fact_changes.length === 0 && <p className="muted">No fact has changed yet.</p>}
          {d.fact_changes.map((c, i) => <p key={i}>{c.fact_id}: {c.old} → {c.new} · {c.drafts_affected} drafts affected</p>)}
        </div>
        <div className="card">
          <h2>Decision history</h2>
          {d.history.map((h, i) => <p key={i} className="muted">{h.at.slice(0, 19).replace("T", " ")} · {h.type} {h.rule_id ?? ""} {h.draft_id ? "#" + h.draft_id : ""} {h.note}</p>)}
        </div>
      </div>
    </div>
  );
}
