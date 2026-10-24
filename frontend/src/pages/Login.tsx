import { FormEvent, MouseEvent, useState } from "react";
import { api, session } from "../api";
import type { User } from "../types";

export default function Login({ onUser }: { onUser: (u: User) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function go(
    e: FormEvent<HTMLFormElement> | MouseEvent<HTMLButtonElement>,
    creds?: [string, string]
  ) {
    e.preventDefault();
    setBusy(true);
    setErr("");

    try {
      const r = creds
        ? await api.login(creds[0], creds[1])
        : mode === "login"
          ? await api.login(email, pw)
          : await api.register(email, name, pw);

      session.set(r.token);
      onUser(r.user);
    } catch (x) {
      setErr((x as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <style>{`
        .inkproof-brand {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          margin: 0 auto 22px;
          text-align: center;
        }

        .inkproof-logo {
          width: 76px;
          height: 76px;
          overflow: visible;
          margin-bottom: 9px;
        }

        .inkproof-logo-orbit {
          transform-origin: 40px 40px;
          animation: inkproof-orbit 12s linear infinite;
        }

        .inkproof-logo-draw {
          stroke-dasharray: 150;
          stroke-dashoffset: 150;
          animation: inkproof-draw 1.7s ease-out forwards;
        }

        .inkproof-logo-check {
          stroke-dasharray: 45;
          stroke-dashoffset: 45;
          animation: inkproof-draw 0.65s ease-out 1.1s forwards;
        }

        .inkproof-logo-pulse {
          transform-box: fill-box;
          transform-origin: center;
          animation: inkproof-pulse 3s ease-in-out infinite;
        }

        .inkproof-brand-name {
          margin: 0;
          font-size: 25px;
          font-weight: 800;
          line-height: 1.2;
          letter-spacing: -1.1px;
          color: var(--text, #173b30);
        }

        .inkproof-brand-name span {
          color: #6b9e45;
        }

        .inkproof-brand-tagline {
          margin: 6px 0 0;
          font-size: 12px;
          letter-spacing: 1.8px;
          text-transform: uppercase;
          font-weight: 600;
          opacity: 0.7;
        }

        @keyframes inkproof-orbit {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes inkproof-draw {
          to { stroke-dashoffset: 0; }
        }

        @keyframes inkproof-pulse {
          0%, 100% { opacity: 0.65; transform: scale(0.96); }
          50% { opacity: 1; transform: scale(1.04); }
        }

        @media (prefers-reduced-motion: reduce) {
          .inkproof-logo-orbit,
          .inkproof-logo-draw,
          .inkproof-logo-check,
          .inkproof-logo-pulse {
            animation: none;
            stroke-dashoffset: 0;
          }
        }
      `}</style>

      <div className="card narrow">
        <div className="inkproof-brand" aria-label="Inkproof by Novara">
          <svg
            className="inkproof-logo"
            viewBox="0 0 80 80"
            role="img"
            aria-label="Animated Inkproof mark"
          >
            <defs>
              <linearGradient id="inkproof-gradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#9bc96b" />
                <stop offset="100%" stopColor="#27664d" />
              </linearGradient>
              <filter id="inkproof-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <circle
              cx="40"
              cy="40"
              r="34"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.8"
              opacity="0.12"
            />

            <g className="inkproof-logo-orbit">
              <circle
                cx="40"
                cy="6"
                r="3"
                fill="#9bc96b"
                filter="url(#inkproof-glow)"
              />
              <path
                d="M40 2 A38 38 0 0 1 77 40"
                fill="none"
                stroke="#8dbd62"
                strokeWidth="1.4"
                strokeLinecap="round"
                opacity="0.8"
              />
            </g>

            <g className="inkproof-logo-pulse">
              <path
                className="inkproof-logo-draw"
                d="M19 17 L19 63 L48 63 C62 63 67 44 54 36 C64 26 53 15 41 18 L19 17"
                fill="none"
                stroke="url(#inkproof-gradient)"
                strokeWidth="5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              <path
                d="M30 27 L30 51"
                fill="none"
                stroke="#8dbd62"
                strokeWidth="4"
                strokeLinecap="round"
              />

              <path
                className="inkproof-logo-check"
                d="M35 41 L43 49 L59 30"
                fill="none"
                stroke="#9bc96b"
                strokeWidth="4.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </g>
          </svg>

          <p className="inkproof-brand-name">
            ink<span>proof</span>
          </p>
          <p className="inkproof-brand-tagline">Words. Verified.</p>
        </div>

        <h2>
          {mode === "login" ? "Sign in" : "Create a writer account"}
        </h2>

        <form onSubmit={go} className="stack">
          {mode === "register" && (
            <input
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password (8+ characters)"
            value={pw}
            onChange={(e) => setPw(e.target.value)}
            minLength={8}
            required
          />

          <button className="primary" disabled={busy}>
            {busy
              ? "Please wait…"
              : mode === "login"
                ? "Sign in"
                : "Register"}
          </button>
        </form>

        {err && <p className="error" role="alert">{err}</p>}

        <button
          type="button"
          className="link"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setErr("");
          }}
        >
          {mode === "login"
            ? "New here? Create an account"
            : "Have an account? Sign in"}
        </button>

        <hr />

        <p className="muted">
          Judges: try the demo accounts (synthetic data only). The first
          sign-in can take a minute while the server wakes up.
        </p>

        <div className="row">
          <button
            type="button"
            disabled={busy}
            onClick={(e) => go(e, ["writer@demo.test", "demo1234"])}
          >
            Demo writer
          </button>

          <button
            type="button"
            disabled={busy}
            onClick={(e) => go(e, ["reviewer@demo.test", "demo1234"])}
          >
            Demo reviewer
          </button>
        </div>
      </div>
    </>
  );
}
