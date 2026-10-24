import { useEffect, useState } from "react";
import { api } from "../api";
import type { Fact, Rule, User } from "../types";

function FactRow({ f, can, onSaved }: { f: Fact; can: boolean; onSaved: (n: number) => void }) {
  const [v, setV] = useState(String(f.value)), [u, setU] = useState(f.valid_until);
  const dirty = Number(v) !== f.value || u !== f.valid_until;
  return (
    <tr>
      <td>{f.id}</td><td>{f.text}</td>
      <td><input type="number" step="any" value={v} disabled={!can} onChange={(e) => setV(e.target.value)} /></td>
      <td><input type="date" value={u} disabled={!can} onChange={(e) => setU(e.target.value)} /></td>
      <td>v{f.version}{f.expired ? " · expired" : ""}</td>
      <td><button disabled={!can || !dirty} onClick={() => api.patchFact(f.id, Number(v), u).then((r) => onSaved(r.drafts_affected))}>Save</button></td>
    </tr>
  );
}

export default function Library({ user }: { user: User }) {
  const [lib, setLib] = useState<{ rules: Rule[]; facts: Fact[] } | null>(null), [msg, setMsg] = useState("");
  const load = () => api.library().then(setLib);
  useEffect(() => { load(); }, []);
  const can = user.role === "reviewer";
  if (!lib) return <p className="muted">Loading…</p>;
  return (
    <>
      <div className="card">
        <h2>Approved rules</h2>
        <div className="scroll"><table>
          <thead><tr><th>ID</th><th>Rule</th><th>Version</th><th>Approved</th></tr></thead>
          <tbody>{lib.rules.map((r) => (
            <tr key={r.id}><td>{r.id}</td><td>{r.name}</td><td>v{r.version}</td>
              <td><input type="checkbox" checked={r.approved} disabled={!can} onChange={() => api.patchRule(r.id, !r.approved).then(load)} /></td></tr>
          ))}</tbody>
        </table></div>
        <p className="muted">Unapproved rules cannot confirm a finding, so those go to human review.</p>
      </div>
      <div className="card">
        <h2>Approved facts</h2>
        {!can && <p className="muted">Sign in as a reviewer to edit facts.</p>}
        {msg && <p><b>{msg}</b></p>}
        <div className="scroll"><table>
          <thead><tr><th>ID</th><th>Fact</th><th>Value</th><th>Valid until</th><th>Version</th><th /></tr></thead>
          <tbody>{lib.facts.map((f) => (
            <FactRow key={f.id + f.version} f={f} can={can} onSaved={(n) => { setMsg(`Saved. ${n} submitted draft(s) that used this fact are marked for re-check.`); load(); }} />
          ))}</tbody>
        </table></div>
      </div>
    </>
  );
}
