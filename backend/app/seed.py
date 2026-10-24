"""Synthetic demo data only (fictional brand Northwind Learning)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .config import settings
from .security import hash_password


def seed(db: Session) -> None:
    if not db.scalar(select(m.Rule).limit(1)):
        db.add_all([
            m.Rule(id="R-TERM-01", name="Avoid absolute or hype terms", kind="term",
                   config={"terms": {"guaranteed": "proven", "best in class": "strong", "world-class": "high-quality"}}),
            m.Rule(id="R-CLM-03", name="Ranking claims need a named, dated source", kind="rank"),
            m.Rule(id="R-NUM-01", name="Numbers must match an approved, current fact", kind="num"),
            m.Rule(id="R-TON-02", name="One exclamation mark at most, never in a claim", kind="tone"),
        ])
        db.add_all([
            m.Fact(id="F-012", text="Average score gain: 18% over an 8-week course", keywords=["score", "improve"],
                   value=18, unit="%", period=8, period_unit="week", cumulative=True, valid_until="2027-12-31"),
            m.Fact(id="F-031", text="Average store rating: 4.6 stars", keywords=["rated", "rating"],
                   value=4.6, unit="stars", valid_until="2026-06-30"),
        ])
    if settings.seed_demo and not db.scalar(select(m.User).limit(1)):
        db.add_all([
            m.User(email="writer@demo.test", name="Demo Writer", pw_hash=hash_password("demo1234"), role="writer"),
            m.User(email="reviewer@demo.test", name="Demo Reviewer", pw_hash=hash_password("demo1234"), role="reviewer"),
        ])
    db.commit()
