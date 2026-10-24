
import { useEffect, useState } from "react";
import { api } from "../api";
import FindingCard from "../components/FindingCard";
import { intentWarnings, removesCta } from "../lib/intent";
import type { Draft, Finding, Intent } from "../types";

const SAMPLE =
  "Northwind is India’s #1 learning app. Students raise their scores by 60% in just 2 weeks!!! Rated 4.6 stars by parents. Sign up now.";

const EMPTY_INTENT: Intent = { cta: "", claims: "" };

const SAMPLE_INTENT: Intent = {
  cta: "Sign up now",
  claims: "top app, score gain",
};

export default function Review() {
  const [text, setText] = useState("");
  const [channel, setChannel] = useState("social");
  const [intent, setIntent] = useState<Intent>({ ...EMPTY_INTENT });
  const [findings, setFindings] = useState<Finding[] | null>(null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [editingDraftId, setEditingDraftId] = useState<number | null>(null);

  const loadDrafts = async () => {
    try {
      const result = await api.drafts();
      setDrafts(result);
    } catch {
      // Keep the current draft list if refreshing fails.
    }
  };

  useEffect(() => {
    void loadDrafts();
  }, []);

  const guard = async (fn: () => Promise<void>) => {
    setBusy(true);
    setNote("");

    try {
      await fn();
    } catch (e) {
      setNote(
        (e as Error).message || "Something went wrong. Please try again."
      );
    } finally {
      setBusy(false);
    }
  };

  const run = (t = text, useAi = false) =>
    guard(async () => {
      if (!t.trim()) {
        setNote("Please enter your content before running a review.");
        return;
      }

      const r = await api.review(t, channel, useAi);
      setFindings(r.findings);
      setNote(r.note ?? "");
    });

  const accept = (f: Finding) => {
    if (!f.fix) return;

    const next = text.replace(f.quote, f.fix);

    if (removesCta(text, next, intent)) {
      setNote("Blocked: this edit would remove your call to action.");
      return;
    }

    setText(next);
    setNote("Edit applied. Refresh the review before submitting.");
    setFindings(null);
    api.event("accept", f.rule_id).catch(() => undefined);
    void run(next);
  };

  const dispute = (f: Finding) => {
    setFindings((fs) =>
      fs && fs.map((x) => (x.id === f.id ? { ...x, disputed: true } : x))
    );

    api.event("dispute", f.rule_id).catch(() => undefined);
  };

  const submit = () =>
    guard(async () => {
      if (!text.trim()) {
        setNote("Please enter your content before submitting.");
        return;
      }

      if (findings === null) {
        setNote("Run a review before submitting your draft.");
        return;
      }

      const aiFindings = findings.filter(
        (f) => f.label === "AI-suggested"
      );

      let d: Draft;

      if (editingDraftId !== null) {
        d = await api.updateDraft(
          editingDraftId,
          text,
          channel,
          intent,
          aiFindings
        );

        setNote(
          `Draft ${d.id} updated with fresh findings. It is awaiting reviewer decisions.`
        );
      } else {
        d = await api.submit(text, channel, intent, aiFindings);

        setNote(
          `Submitted as draft ${d.id}. A reviewer must decide before it can be approved.`
        );
      }

      setEditingDraftId(null);
      await loadDrafts();
    });

  const upload = (file?: File) =>
    file &&
    guard(async () => {
      const imported = await api.importDocx(file);

      setText(imported.text);
      setFindings(null);
      setEditingDraftId(null);
      setNote("DOCX imported. Run a review when you're ready.");
    });

  const loadExample = () => {
    setText(SAMPLE);
    setChannel("social");
    setIntent({ ...SAMPLE_INTENT });
    setFindings(null);
    setEditingDraftId(null);
    setNote("Northwind demo loaded. You can edit every field.");
  };

  const clearDraft = () => {
    setText("");
    setChannel("social");
    setIntent({ ...EMPTY_INTENT });
    setFindings(null);
    setEditingDraftId(null);
    setNote("");
  };

  const reopenDraft = (d: Draft) => {
    setEditingDraftId(d.id);
    setText(d.text);
    setChannel(d.channel);

    const savedIntent = d.intent as Intent | undefined;
    setIntent({
      ...EMPTY_INTENT,
      ...(savedIntent ?? {}),
    });

    setFindings(null);
    setNote(
      `Draft ${d.id} reopened for editing. Run a fresh review before updating it.`
    );
  };

  return (
    <div className="grid">
      <div>
        <div className="card">
          <h2>1. Draft and intent</h2>

          <p className="muted">
            Paste your own content, describe what must stay unchanged, and
            review it against your brand requirements.
          </p>

          {editingDraftId !== null && (
            <p role="status">
              <b>Editing existing draft #{editingDraftId}</b>
            </p>
          )}

          <label htmlFor="draft-channel">Content type</label>
          <select
            id="draft-channel"
            value={channel}
            onChange={(e) => {
              setChannel(e.target.value);
              setFindings(null);
            }}
          >
            <option value="social">Social post</option>
            <option value="web">Web page</option>
            <option value="email">Email</option>
          </select>

          <label htmlFor="draft-text">Your content</label>
          <textarea
            id="draft-text"
            value={text}
            placeholder="Paste or write your own social post, webpage copy, or email here..."
            onChange={(e) => {
              setText(e.target.value);
              setFindings(null);
              setNote("");
            }}
          />

          <div className="row">
            <button disabled={busy} onClick={loadExample}>
              Load Northwind example
            </button>

            <button disabled={busy} onClick={clearDraft}>
              Clear draft
            </button>
          </div>

          <label htmlFor="draft-file">
            Import a Word document (.docx)
          </label>

          <input
            id="draft-file"
            type="file"
            accept=".docx"
            onChange={(e) => {
              const file = e.target.files?.[0];
              void upload(file);
              e.currentTarget.value = "";
            }}
          />

          <h3>Intent Card</h3>

          <p className="muted">
            Define the important details your content should preserve.
          </p>

          <label htmlFor="draft-cta">
            Required call to action (optional)
          </label>

          <input
            id="draft-cta"
            className="full"
            placeholder="e.g. Register today"
            value={intent.cta}
            onChange={(e) =>
              setIntent({ ...intent, cta: e.target.value })
            }
          />

          <label htmlFor="draft-claims">
            Key claims or facts (optional)
          </label>

          <input
            id="draft-claims"
            className="full"
            placeholder="e.g. free delivery, launched in 2024, 24-hour support"
            value={intent.claims}
            onChange={(e) =>
              setIntent({ ...intent, claims: e.target.value })
            }
          />

          <div className="row">
            <button
              className="primary"
              disabled={busy || !text.trim()}
              onClick={() => void run()}
            >
              {busy ? "Working..." : "Run review"}
            </button>

            <button
              disabled={busy || !text.trim()}
              onClick={() => void run(text, true)}
            >
              Run with AI review
            </button>
          </div>
        </div>

        <div className="card">
          <h2>Your drafts</h2>

          {drafts.length === 0 && (
            <p className="muted">
              Your submitted drafts will appear here.
            </p>
          )}

          {drafts.map((d) => (
            <p key={d.id}>
              #{d.id} · {d.title} ·{" "}
              <b>
                {d.status === "recheck" ? "Needs re-check" : d.status}
              </b>{" "}

              <button
                disabled={busy || d.status === "approved"}
                onClick={() => reopenDraft(d)}
              >
                Reopen
              </button>{" "}

              <button
                disabled={busy}
                onClick={() =>
                  guard(async () => {
                    await api.remove(d.id);

                    if (editingDraftId === d.id) {
                      setEditingDraftId(null);
                      setFindings(null);
                    }

                    await loadDrafts();
                    setNote(`Draft ${d.id} deleted.`);
                  })
                }
              >
                Delete
              </button>
            </p>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>2. Findings with evidence</h2>

        {note && (
          <p role="status">
            <b>{note}</b>
          </p>
        )}

        {findings === null && (
          <p className="muted">
            Your review findings will appear here with the relevant rules,
            evidence, quoted text, and suggested edits.
          </p>
        )}

        {findings?.length === 0 && (
          <div className="finding ok">
            <b>No findings.</b> No conflicts were detected by the current
            review rules and approved facts.
          </div>
        )}

        {findings?.map((f) => {
          const warnings = intentWarnings(f, intent);

          return (
            <FindingCard key={f.id} f={f}>
              {f.fix && (
                <p>
                  Suggested edit: <b>{f.quote}</b> → <b>{f.fix}</b>{" "}
                  <span className="muted">
                    (not applied automatically)
                  </span>
                </p>
              )}

              {warnings.map((warning) => (
                <p key={warning} className="muted">
                  ⚠ Intent Lock: {warning}
                </p>
              ))}

              <div className="row">
                {f.fix && (
                  <button onClick={() => accept(f)}>
                    {warnings.length ? "Accept anyway" : "Accept edit"}
                  </button>
                )}

                <button
                  disabled={f.disputed}
                  onClick={() => dispute(f)}
                >
                  {f.disputed ? "Disputed" : "Dispute"}
                </button>
              </div>
            </FindingCard>
          );
        })}

        {findings !== null && (
          <button
            className="primary"
            disabled={busy || !text.trim()}
            onClick={submit}
          >
            {busy
              ? "Working..."
              : editingDraftId !== null
                ? `Update draft #${editingDraftId}`
                : "Submit for reviewer decision"}
          </button>
        )}
      </div>
    </div>
  );
}
