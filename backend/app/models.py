import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from .db import Base


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    agents = relationship("Agent", back_populates="team")


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    expertise = Column(JSON, default=list)  # ["billing", "bug", ...]
    capacity = Column(Integer, default=5)
    active = Column(Boolean, default=True)
    team = relationship("Team", back_populates="agents")


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, default="")
    status = Column(String(20), default="new")  # new, assigned, in_progress, resolved
    topic = Column(String(50), nullable=True)
    urgency = Column(String(20), nullable=True)  # low, medium, high, critical
    priority = Column(Integer, nullable=True)  # 1..4
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    manual_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    assigned_agent = relationship("Agent")


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)
    reason = Column(Text, default="")
    auto = Column(Boolean, default=True)


class ClassificationEvent(Base):
    __tablename__ = "classification_events"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    topic_scores = Column(JSON, nullable=True)
    urgency_scores = Column(JSON, nullable=True)
    provider = Column(String(50), default="")
    latency_ms = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
