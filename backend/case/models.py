from sqlalchemy import Column, BigInteger, Integer, Text, Boolean, DateTime, Date, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
# Support both package and script imports
try:
    from .database import Base  # type: ignore
except Exception:
    from database import Base  # type: ignore

class AppUser(Base):
    __tablename__ = "app_user"
    id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Case(Base):
    __tablename__ = "case"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, nullable=False)
    title = Column(Text)
    latest_summary = Column(Text)
    needs_review = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user = relationship("AppUser")

"""Receipt model removed per requirement: we no longer persist receipts in DB."""

class Issue(Base):
    __tablename__ = "issue"
    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    classification = Column(Text)
    clf_confidence = Column(Numeric(5,2))
    ai_annotations = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class PolicySnapshot(Base):
    __tablename__ = "policy_snapshot"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    matched_rules = Column(JSON, nullable=False)
    captured_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class EligibilityDecision(Base):
    __tablename__ = "eligibility_decision"
    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    policy_snapshot_id = Column(BigInteger, ForeignKey("policy_snapshot.id"))
    status = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    lenient_flag = Column(Boolean, default=False)
    decided_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class WarrantyDeadline(Base):
    __tablename__ = "warranty_deadline"
    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    deadline_date = Column(Date, nullable=False)
    type = Column(Text, nullable=False)
    source = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminder"
    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    deadline_id = Column(BigInteger, ForeignKey("warranty_deadline.id", ondelete="SET NULL"))
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    status = Column(Text, nullable=False)
    channel = Column(Text, nullable=False)
