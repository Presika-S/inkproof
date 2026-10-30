

import io
import json
from collections import defaultdict
from copy import deepcopy

import docx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import ai, engine as eng, models as m, schemas as s
from .db import get_db
from .security import (
    create_token,
    get_current_user,
    hash_password,
    require_reviewer,
    verify_password,
)

router = APIRouter(prefix="/api")


def _rule(r: m.Rule) -> dict:
    return dict(
        id=r.id,
        name=r.name,
        kind=r.kind,
        config=r.config,
        version=r.version,
        approved=r.approved,
    )


def _fact(f: m.Fact, sources: list[dict] | None = None) -> dict:
    sources = sources or []

    return dict(
        id=f.id,
        text=f.text,
        keywords=f.keywords,
        value=f.value,
        unit=f.unit,
        period=f.period,
        period_unit=f.period_unit,
        cumulative=f.cumulative,
        rank=f.rank,
        valid_until=f.valid_until,
        owner=f.owner,
        version=f.version,
        approved=f.approved,
        expired=eng.is_expired(dict(valid_until=f.valid_until)),
        sources=sources,
        source_stale=bool(sources) and all(
            source["stale"] for source in sources
        ),
    )


def _lib(db: Session):
    rules = [
        _rule(r)
        for r in db.scalars(select(m.Rule).order_by(m.Rule.id))
    ]

    facts = list(
        db.scalars(select(m.Fact).order_by(m.Fact.id))
    )

    links = list(db.scalars(select(m.FactEvidence)))
    documents = {
        document.id: document
        for document in db.scalars(select(m.EvidenceDocument))
    }

    sources_by_fact = defaultdict(list)

    for link in links:
        document = documents.get(link.document_id)

        stale = (
            link.stale
            or document is None
            or document.status != "active"
            or document.version != link.source_version
        )

        sources_by_fact[link.fact_id].append({
            "document_id": link.document_id,
            "filename": document.filename if document else None,
            "source_quote": link.source_quote,
            "document_version": link.source_version,
            "current_document_version": (
                document.version if document else None
            ),
            "stale": stale,
        })

    return (
        rules,
        [
            _fact(f, sources_by_fact.get(f.id, []))
            for f in facts
        ],
    )

def _draft(d: m.Draft) -> dict:
    return dict(
        id=d.id,
        title=d.title,
        text=d.text,
        channel=d.channel,
        intent=d.intent,
        status=d.status,
        findings=d.findings,
        author_id=d.author_id,
        created_at=d.created_at.isoformat(),
    )


def _log(
    db: Session,
    type_: str,
    user: m.User | None,
    rule_id=None,
    draft_id=None,
    note="",
    before_value=None,
    after_value=None,
):
    db.add(
        m.Event(
            type=type_,
            rule_id=rule_id,
            draft_id=draft_id,
            note=note[:300],
            before_value=before_value,
            after_value=after_value,
            user_id=user.id if user else None,
        )
    )

# ---------- auth ----------

@router.post("/auth/register")
def register(body: s.RegisterIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()

    if db.scalar(select(m.User).where(m.User.email == email)):
        raise HTTPException(409, "That email is already registered")

    user = m.User(
        email=email,
        name=body.name.strip(),
        pw_hash=hash_password(body.password),
        role="writer",
    )
    db.add(user)
    db.commit()

    return {"token": create_token(user.id), "user": _user(user)}


@router.post("/auth/login")
def login(body: s.LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(
        select(m.User).where(m.User.email == body.email.strip().lower())
    )

    if not user or not verify_password(body.password, user.pw_hash):
        raise HTTPException(401, "Wrong email or password")

    return {"token": create_token(user.id), "user": _user(user)}


def _user(u: m.User) -> dict:
    return dict(id=u.id, name=u.name, email=u.email, role=u.role)


@router.get("/me")
def me(user: m.User = Depends(get_current_user)):
    return _user(user)


# ---------- library ----------

@router.get("/library")
def library(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    rules, facts = _lib(db)
    return {"rules": rules, "facts": facts}


@router.patch("/rules/{rule_id}")
def patch_rule(
    rule_id: str,
    body: s.RulePatch,
    db: Session = Depends(get_db),
    user: m.User = Depends(require_reviewer),
):
    r = db.get(m.Rule, rule_id)

    if not r:
        raise HTTPException(404, "Unknown rule")

    r.approved = body.approved
    r.version += 1

    db.commit()
    return _rule(r)


@router.patch("/facts/{fact_id}")
def patch_fact(
    fact_id: str,
    body: s.FactPatch,
    db: Session = Depends(get_db),
    user: m.User = Depends(require_reviewer),
):
    f = db.get(m.Fact, fact_id)

    if not f:
        raise HTTPException(404, "Unknown fact")

    old = f"{f.value:g}, until {f.valid_until}"
    f.text = f.text.replace(f"{f.value:g}", f"{body.value:g}", 1)
    f.value = body.value
    f.valid_until = body.valid_until
    f.version += 1

    affected = [
        d
        for d in db.scalars(select(m.Draft))
        if fact_id in (d.facts_used or [])
    ]

    for d in affected:
        d.status = "recheck"

    new_value = f"{body.value:g}, until {body.valid_until}"
    db.add(
        m.FactChange(
            fact_id=fact_id,
            old=old,
            new=new_value,
            drafts_affected=len(affected),
            user_id=user.id,
        )
    )
    _log(
        db,
        "fact_updated",
        user,
        rule_id=fact_id,
        note=f"Fact updated; {len(affected)} draft(s) marked for recheck",
        before_value=old,
        after_value=new_value,
    )

    db.commit()

    return {**_fact(f), "drafts_affected": len(affected)}


# ---------- review ----------

def _run_review(
    text: str,
    use_ai: bool,
    db: Session,
    extra: list[dict] | None = None,
):
    rules, facts = _lib(db)
    findings = eng.review(text, rules, facts)

    note = None
    rejected = 0
    proposed = list(extra or [])

    if use_ai:
        try:
            proposed += ai.propose(text, rules, facts)
        except ai.AIUnavailable as e:
            note = str(e)

    seen = {f["quote"] for f in findings}

    for i, p in enumerate(proposed):
        v = eng.verify(
            {
                "id": f"AI-{i}",
                "rule_id": p.get("rule_id"),
                "fact_id": p.get("fact_id"),
                "label": "AI-suggested",
                "quote": str(p.get("quote", "")),
                "reason": str(p.get("reason", "")),
                "fix": None,
            },
            text,
            rules,
            facts,
        )

        checks = v["checks"]

        if (
            checks["rule"]
            and checks["quote"]
            and checks["fact"]
            and v["quote"] not in seen
        ):
            findings.append(v)
            seen.add(v["quote"])
        else:
            rejected += 1

    if proposed:
        note = (note or "") + (
            f"AI proposed {len(proposed)} findings; "
            f"the verifier rejected {rejected}."
        )

    return findings, note, facts


@router.post("/review")
def review(
    body: s.ReviewIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    findings, note, _ = _run_review(body.text, body.use_ai, db)
    return {"findings": findings, "note": note}


@router.post("/import/docx")
async def import_docx(
    file: UploadFile = File(...),
    user: m.User = Depends(get_current_user),
):
    if not (file.filename or "").lower().endswith(".docx"):
        raise HTTPException(400, "Upload a .docx file")

    data = await file.read()

    if len(data) > 5_000_000:
        raise HTTPException(413, "File too large (5 MB max)")

    try:
        text = "\n".join(
            p.text for p in docx.Document(io.BytesIO(data)).paragraphs
        ).strip()
    except Exception:
        raise HTTPException(400, "Could not read that DOCX file")

    return {"text": text}


# ---------- drafts ----------

@router.post("/drafts")
def submit(
    body: s.DraftIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    ai_extra = [
        f for f in body.findings
        if f.get("label") == "AI-suggested"
    ]

    findings, _, facts = _run_review(body.text, False, db, ai_extra)
    lo = body.text.lower()

    d = m.Draft(
        author_id=user.id,
        title=body.text[:40],
        text=body.text,
        channel=body.channel,
        intent=body.intent,
        findings=[{**f, "dec": None} for f in findings],
        facts_used=[
            f["id"]
            for f in facts
            if any(k in lo for k in f["keywords"])
        ],
    )

    db.add(d)
    db.flush()

    for f in findings:
        _log(db, "flag", user, f["rule_id"], d.id)

    db.commit()
    db.refresh(d)

    return _draft(d)


@router.get("/drafts")
def list_drafts(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    q = select(m.Draft).order_by(m.Draft.id.desc())

    if user.role != "reviewer":
        q = q.where(m.Draft.author_id == user.id)

    return [_draft(d) for d in db.scalars(q)]


def _get_draft(db: Session, did: int) -> m.Draft:
    d = db.get(m.Draft, did)

    if not d:
        raise HTTPException(404, "Draft not found")

    return d


# ---------- update existing draft ----------

@router.put("/drafts/{did}")
def update_draft(
    did: int,
    body: s.DraftIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    d = _get_draft(db, did)

    # Only the draft's author can update it.
    if d.author_id != user.id:
        raise HTTPException(403, "Not your draft")

    if d.status == "approved":
        raise HTTPException(400, "Approved drafts cannot be edited")

    ai_extra = [
        f for f in body.findings
        if f.get("label") == "AI-suggested"
    ]

    findings, _, facts = _run_review(body.text, False, db, ai_extra)
    lo = body.text.lower()

    # Update the existing record instead of creating a duplicate.
    d.title = body.text[:40]
    d.text = body.text
    d.channel = body.channel
    d.intent = body.intent
    d.findings = [{**f, "dec": None} for f in findings]
    d.facts_used = [
        f["id"]
        for f in facts
        if any(k in lo for k in f["keywords"])
    ]
    d.status = "in_review"

    for f in findings:
        _log(db, "flag", user, f["rule_id"], d.id)

    db.commit()
    db.refresh(d)

    return _draft(d)


# ---------- decisions ----------

@router.post("/drafts/{did}/findings/{idx}/decision")
def decide(
    did: int,
    idx: int,
    body: s.DecisionIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(require_reviewer),
):
    d = _get_draft(db, did)

    if d.author_id == user.id:
        raise HTTPException(403, "You cannot review or approve your own draft")

    if body.decision not in ("uphold", "waive"):
        raise HTTPException(400, "decision must be uphold or waive")

    if body.decision == "waive" and not body.note.strip():
        raise HTTPException(400, "A written reason is required to waive a finding")

    if not 0 <= idx < len(d.findings):
        raise HTTPException(404, "No such finding")

    fs = deepcopy(d.findings)
    before = fs[idx].get("dec")
    after = {"d": body.decision, "note": body.note.strip()}
    fs[idx]["dec"] = after
    d.findings = fs

    _log(
        db,
        body.decision,
        user,
        fs[idx]["rule_id"],
        d.id,
        body.note,
        before_value=json.dumps(before, sort_keys=True) if before is not None else None,
        after_value=json.dumps(after, sort_keys=True),
    )

    db.commit()
    db.refresh(d)
    return _draft(d)


@router.post("/drafts/{did}/finalize")
def finalize(
    did: int,
    body: s.FinalizeIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(require_reviewer),
):
    d = _get_draft(db, did)

    if d.author_id == user.id:
        raise HTTPException(403, "You cannot review or approve your own draft")

    if body.status not in ("approved", "changes_requested"):
        raise HTTPException(400, "status must be approved or changes_requested")

    if body.status == "approved" and any(
        not f.get("dec") or f["dec"]["d"] != "waive"
        for f in d.findings
    ):
        raise HTTPException(
            400,
            "Approval needs every finding waived with a written reason",
        )

    before = d.status
    d.status = body.status

    _log(
        db,
        "decision",
        user,
        None,
        d.id,
        body.status,
        before_value=before,
        after_value=body.status,
    )

    db.commit()
    db.refresh(d)
    return _draft(d)


# ---------- events ----------

@router.post("/events")
def event(
    body: s.EventIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    if body.type not in ("accept", "dispute"):
        raise HTTPException(400, "type must be accept or dispute")

    _log(db, body.type, user, body.rule_id, body.draft_id)
    db.commit()

    return {"ok": True}


@router.delete("/drafts/{did}")
def delete_draft(
    did: int,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    d = _get_draft(db, did)

    if d.author_id != user.id and user.role != "reviewer":
        raise HTTPException(403, "Not your draft")

    db.delete(d)
    db.commit()

    return {"deleted": did}


# ---------- insights ----------

@router.get("/insights")
def insights(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    flagged, overridden = defaultdict(int), defaultdict(int)
    events = list(
        db.scalars(select(m.Event).order_by(m.Event.id.desc()))
    )

    for e in events:
        if e.type == "flag" and e.rule_id:
            flagged[e.rule_id] += 1
        elif e.type in ("waive", "dispute") and e.rule_id:
            overridden[e.rule_id] += 1

    health = []

    for r in db.scalars(select(m.Rule)):
        fl, ov = flagged[r.id], overridden[r.id]
        rate = round(100 * ov / fl) if fl else 0

        health.append(
            dict(
                rule_id=r.id,
                name=r.name,
                flagged=fl,
                overridden=ov,
                rate=rate,
                unclear=fl >= 2 and rate >= 50,
            )
        )

    health.sort(key=lambda x: -x["rate"])

    changes = [
        dict(
            fact_id=c.fact_id,
            old=c.old,
            new=c.new,
            drafts_affected=c.drafts_affected,
            at=c.created_at.isoformat(),
        )
        for c in db.scalars(
            select(m.FactChange)
            .order_by(m.FactChange.id.desc())
            .limit(10)
        )
    ]

    history = [
        dict(
            id=e.id,
            type=e.type,
            rule_id=e.rule_id,
            draft_id=e.draft_id,
            note=e.note,
            before_value=e.before_value,
            after_value=e.after_value,
            user_id=e.user_id,
            at=e.created_at.isoformat(),
        )
        for e in events[:12]
    ]

    return {
        "health": health,
        "fact_changes": changes,
        "history": history,
    }
