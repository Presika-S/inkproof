import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_inkproof.db"
os.environ["SEED_DEMO"] = "true"

# Reset only the disposable test database before importing the app.
Path("test_inkproof.db").unlink(missing_ok=True)
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

TEXT = "Northwind is India’s #1 learning app. Students raise their scores by 60% in just 2 weeks!!! Rated 4.6 stars by parents. Sign up now."


def login(c, who):
    r = c.post("/api/auth/login", json={"email": f"{who}@demo.test", "password": "demo1234"})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["token"]}


def test_full_workflow():
    with TestClient(app) as c:
        w, rv = login(c, "writer"), login(c, "reviewer")
        assert c.post("/api/review", json={"text": TEXT}).status_code == 401
        r = c.post("/api/review", json={"text": TEXT, "use_ai": True}, headers=w).json()
        assert len(r["findings"]) == 4 and "not configured" in r["note"]  # no API key: rule-based review still works
        d = c.post("/api/drafts", json={"text": TEXT, "intent": {"cta": "Sign up now"}}, headers=w).json()
        assert d["status"] == "in_review" and len(d["findings"]) == 4
        assert c.post(f"/api/drafts/{d['id']}/finalize", json={"status": "approved"}, headers=w).status_code == 403
        assert c.post(f"/api/drafts/{d['id']}/finalize", json={"status": "approved"}, headers=rv).status_code == 400
        assert c.post(f"/api/drafts/{d['id']}/findings/0/decision", json={"decision": "waive"}, headers=rv).status_code == 400
        for i in range(4):
            r = c.post(f"/api/drafts/{d['id']}/findings/{i}/decision", json={"decision": "waive", "note": "ok for test"}, headers=rv)
            assert r.status_code == 200
        assert c.post(f"/api/drafts/{d['id']}/finalize", json={"status": "approved"}, headers=rv).json()["status"] == "approved"
        # changing a fact marks drafts that used it for re-check
        p = c.patch("/api/facts/F-012", json={"value": 20, "valid_until": "2027-12-31"}, headers=rv).json()
        assert p["drafts_affected"] >= 1 and p["version"] == 2
        assert c.get("/api/drafts", headers=w).json()[0]["status"] == "recheck"
        ins = c.get("/api/insights", headers=w).json()
        assert any(h["overridden"] for h in ins["health"]) and ins["fact_changes"]
def test_reviewer_cannot_review_or_approve_own_draft():
    with TestClient(app) as c:
        reviewer = login(c, "reviewer")

        draft = c.post(
            "/api/drafts",
            json={
                "text": TEXT,
                "intent": {"cta": "Sign up now"},
            },
            headers=reviewer,
        ).json()

        draft_id = draft["id"]

        decision = c.post(
            f"/api/drafts/{draft_id}/findings/0/decision",
            json={"decision": "waive", "note": "Self-review test"},
            headers=reviewer,
        )
        assert decision.status_code == 403

        finalize = c.post(
            f"/api/drafts/{draft_id}/finalize",
            json={"status": "approved"},
            headers=reviewer,
        )
        assert finalize.status_code == 403