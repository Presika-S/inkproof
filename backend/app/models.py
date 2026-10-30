from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    pw_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(20), default="writer")  # writer | reviewer


class Rule(Base):
    __tablename__ = "rules"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(20))  # term | rank | num | tone
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    approved: Mapped[bool] = mapped_column(Boolean, default=True)


class Fact(Base):
    __tablename__ = "facts"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    text: Mapped[str] = mapped_column(String(300))
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    period: Mapped[float | None] = mapped_column(Float, nullable=True)
    period_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cumulative: Mapped[bool] = mapped_column(Boolean, default=False)
    rank: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_until: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD
    owner: Mapped[str] = mapped_column(String(100), default="Research team")
    version: Mapped[int] = mapped_column(Integer, default=1)
    approved: Mapped[bool] = mapped_column(Boolean, default=True)


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(80))
    text: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(20), default="social")
    intent: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="in_review")
    findings: Mapped[list] = mapped_column(JSON, default=list)
    facts_used: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Event(Base):
    """Audit trail: flag, accept, dispute, uphold, waive, decision."""
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(20), index=True)
    rule_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    draft_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str] = mapped_column(String(300), default="")
    before_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class FactChange(Base):
    __tablename__ = "fact_changes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fact_id: Mapped[str] = mapped_column(String(40))
    old: Mapped[str] = mapped_column(String(100))
    new: Mapped[str] = mapped_column(String(100))
    drafts_affected: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class EvidenceDocument(Base):
    __tablename__ = "evidence_documents"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    extracted_text: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="active")
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class EvidenceProposal(Base):
    __tablename__ = "evidence_proposals"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_documents.id")
    )
    source_quote: Mapped[str] = mapped_column(Text)
    fact_text: Mapped[str] = mapped_column(String(300))
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    period: Mapped[float | None] = mapped_column(Float, nullable=True)
    period_unit: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    cumulative: Mapped[bool] = mapped_column(Boolean, default=False)
    rank: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_until: Mapped[str] = mapped_column(String(10))
    owner: Mapped[str] = mapped_column(
        String(100), default="Research team"
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fact_id: Mapped[str | None] = mapped_column(
        ForeignKey("facts.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now
    )


class FactEvidence(Base):
    __tablename__ = "fact_evidence"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    fact_id: Mapped[str] = mapped_column(ForeignKey("facts.id"))
    document_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_documents.id")
    )
    source_quote: Mapped[str] = mapped_column(Text)
    source_version: Mapped[int] = mapped_column(Integer)
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now
    )