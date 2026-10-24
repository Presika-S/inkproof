import { useEffect, useState } from "react";
import { api } from "../api";
import FindingCard from "../components/FindingCard";
import type { Draft, User } from "../types";

function Decide({ onDec, label }: { onDec: (d: "uphold" | "waive", note: string) => void; label?: string }) {
  const [note, setNote] = useState("");
  return (
    <div className="row">
      <input placeholder="Reason (needed to waive)" value={note} onChange={(e) => setNote(e.target.value)} />
      <button onClick={() => onDec("uphold", note)}>Uphold</button>
      <button disabled={!note.trim()} onClick={() => onDec("waive", note)}>Waive</button>
      {label && <span className="muted">{label}</span>}
    </div>
  );
}

export default function Queue({ user }: { user: User }) {
  const [drafts, setDrafts] = useState<Draft[]>([]), [sel, setSel] = useState<number | null>(null), [err, setErr] = useState("");
  const rev = user.role === "reviewer";
  const load = () => api.drafts().then(setDrafts).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const D = drafts.find((d) => d.id === sel);
  const act = (p: Promise<Draft>) => p.then((d) => setDrafts((ds) => ds.map((x) => (x.id === d.id ? d : x)))).catch((e) => setErr(e.message));
  const sorted = [...drafts].sort((a, b) => b.findings.length - a.findings.length);

  return (
    <div className="grid">
      <div className="card">
        <h2>Drafts, riskiest first</h2>
        {!rev && <p className="muted">Sign in as a reviewer to decide on drafts.</p>}
        {sorted.map((d) => (
          <p key={d.id}><button onClick={() => setSel(d.id)}>#{d.id}</button> {d.title}… · {d.findings.length} findings · <b>{d.status}</b></p>
        ))}
        {drafts.length === 0 && <p className="muted">No drafts yet.</p>}
      </div>
      <div className="card">
        {err && <p className="error">{err}</p>}
        {!D ? <p className="muted">Select a draft.</p> : (
          <>
            <h2>Draft #{D.id}</h2>
            <p>{D.text}</p>
            {D.findings.map((f, i) => (
              <FindingCard key={f.id} f={f}>
                {rev
                  ? <Decide label={f.dec ? `Decision: ${f.dec.d}${f.dec.note ? " – " + f.dec.note : ""}` : undefined} onDec={(d, n) => act(api.decide(D.id, i, d, n))} />
                  : f.dec && <p className="muted">Decision: {f.dec.d} – {f.dec.note}</p>}
              </FindingCard>
            ))}
            {rev && (
              <div className="row">
                <button className="primary" disabled={D.findings.some((f) => f.dec?.d !== "waive")} onClick={() => act(api.finalize(D.id, "approved"))}>Approve</button>
                <button onClick={() => act(api.finalize(D.id, "changes_requested"))}>Request changes</button>
              </div>
            )}
            <p className="muted">Approval needs every finding waived with a written reason. Otherwise request changes.</p>
          </>
        )}
      </div>
    </div>
  );
}
