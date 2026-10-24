
import { useEffect, useState } from "react";
import { api, session } from "./api";
import About from "./pages/About";
import Insights from "./pages/Insights";
import Library from "./pages/Library";
import Login from "./pages/Login";
import Queue from "./pages/Queue";
import Review from "./pages/Review";
import type { User } from "./types";

type Tab = "review" | "queue" | "lib" | "ins" | "about";
type Theme = "light" | "dark";

const NAV_ITEMS: {
  id: Tab;
  label: string;
  icon: string;
  group: string;
}[] = [
  { id: "review", label: "Write & Review", icon: "✎", group: "WORKSPACE" },
  { id: "queue", label: "Reviewer Queue", icon: "☷", group: "WORKSPACE" },
  { id: "lib", label: "Brand Knowledge", icon: "▤", group: "GOVERNANCE" },
  { id: "ins", label: "Insights", icon: "▥", group: "GOVERNANCE" },
  { id: "about", label: "Privacy & How It Works", icon: "◇", group: "GOVERNANCE" },
];

const PAGE_COPY: Record<Tab, { title: string; description: string }> = {
  review: {
    title: "Write & Review",
    description:
      "Check your content against approved brand rules and facts before it goes live.",
  },
  queue: {
    title: "Reviewer Queue",
    description:
      "Review flagged content, verify evidence and record clear decisions.",
  },
  lib: {
    title: "Brand Knowledge",
    description:
      "Manage the rules and approved facts that keep brand content consistent.",
  },
  ins: {
    title: "Insights",
    description:
      "Understand recurring findings, disputed rules and changes in brand health.",
  },
  about: {
    title: "Privacy & How It Works",
    description:
      "Understand how Inkproof checks content, handles evidence and supports human decisions.",
  },
};

function getInitialTheme(): Theme {
  try {
    const saved = localStorage.getItem("inkproof.theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    // Use light mode if browser storage is unavailable.
  }

  return "light";
}

function getInitialTab(role: User["role"] | null): Tab {
  return role === "reviewer" ? "queue" : "review";
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>("review");
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;

    try {
      localStorage.setItem("inkproof.theme", theme);
    } catch {
      // Theme still works for the current session.
    }
  }, [theme]);

  useEffect(() => {
    if (!session.get()) {
      setReady(true);
      return;
    }

    api
      .me()
      .then((currentUser) => {
        setUser(currentUser);
        setTab(getInitialTab(currentUser.role));
      })
      .catch(() => {
        session.clear();
      })
      .finally(() => setReady(true));
  }, []);

  function handleLogin(nextUser: User) {
    setUser(nextUser);
    setTab(getInitialTab(nextUser.role));
  }

  function handleSignOut() {
    session.clear();
    setUser(null);
    setTab("review");
  }

  const page = PAGE_COPY[tab];
  const initials = user
    ? user.name
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase() ?? "")
        .join("")
    : "I";

  if (!ready) {
    return (
      <main className="loading-screen">
        <div className="brand-mark">I</div>
        <h2>Inkproof</h2>
        <p className="muted">Preparing your workspace…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="auth-screen">
        <div className="auth-brand">
          <div className="brand-mark">I</div>
          <div>
            <div className="brand-name">Inkproof</div>
            <div className="muted">Brand governance with evidence.</div>
          </div>
        </div>
        <Login onUser={handleLogin} />
        <p className="auth-footer">
          Evidence-backed reviews. Human-controlled decisions.
        </p>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">I</div>
          <div>
            <div className="brand-name">Inkproof</div>
            <div className="brand-caption">BRAND GOVERNANCE</div>
          </div>
        </div>

        {["WORKSPACE", "GOVERNANCE"].map((group) => (
          <div key={group}>
            <div className="nav-section-label">{group}</div>
            <nav className="app-nav" aria-label={group.toLowerCase()}>
              {NAV_ITEMS.filter((item) => item.group === group).map((item) => {
                const isActive = tab === item.id;

                return (
                  <button
                    key={item.id}
                    type="button"
                    className={isActive ? "on" : ""}
                    aria-current={isActive ? "page" : undefined}
                    onClick={() => setTab(item.id)}
                  >
                    <span className="nav-icon" aria-hidden="true">
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                    {item.id === "queue" && user.role === "reviewer" && (
                      <span className="nav-indicator" aria-hidden="true">
                        •
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}

        <div className="sidebar-spacer" />

        <div className="sidebar-help">
          <strong>Built around evidence</strong>
          <p>Every finding should have a reason. People make the final call.</p>
        </div>

        <div className="sidebar-user">
          <div className="avatar">{initials}</div>
          <div>
            <div className="sidebar-user-name">{user.name}</div>
            <div className="sidebar-user-role">{user.role}</div>
          </div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-context">
            <span className="topbar-overline">YOUR WORKSPACE</span>
            <span className="topbar-page">{page.title}</span>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="theme-toggle"
              onClick={() =>
                setTheme((current) =>
                  current === "light" ? "dark" : "light"
                )
              }
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
              title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            >
              {theme === "light" ? "☾" : "☀"}
            </button>

            <div className="topbar-user">
              <div className="avatar">{initials}</div>
              <div>
                <strong>{user.name}</strong>
                <span>{user.role}</span>
              </div>
            </div>

            <button
              type="button"
              className="signout-button"
              onClick={handleSignOut}
            >
              Sign out
            </button>
          </div>
        </header>

        <main className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">INKPROOF / {user.role.toUpperCase()}</div>
              <h1>{page.title}</h1>
              <p>{page.description}</p>
            </div>
            <span className="workspace-status">
              <span className="status-dot" />
              Workspace active
            </span>
          </div>

          {tab === "review" && <Review />}
          {tab === "queue" && <Queue user={user} />}
          {tab === "lib" && <Library user={user} />}
          {tab === "ins" && <Insights />}
          {tab === "about" && <About />}
        </main>

        <footer className="app-footer">
          <span>Inkproof · Team NOVARA</span>
          <span>Brand governance that shows its evidence.</span>
        </footer>
      </div>
    </div>
  );
}
