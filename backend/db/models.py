from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    model_used = Column(String(50))
    response_time_ms = Column(Integer)
    ip_address = Column(String(50))  # Client IP address
    user_agent = Column(Text)  # Browser/client info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_metadata = Column(JSON)  # Stores geolocation, device info, etc.

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)  # Clerk user ID
    user_agent = Column(Text)
    ip_address = Column(String(50))
    country = Column(String(100))  # Country from IP
    city = Column(String(100))  # City from IP
    region = Column(String(100))  # State/Region from IP
    timezone = Column(String(50))  # User timezone
    latitude = Column(String(20))  # Geographic coordinates
    longitude = Column(String(20))  # Geographic coordinates
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    extra_metadata = Column(JSON)  # Additional device/browser fingerprinting data


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String(200), nullable=False, index=True)
    title = Column(String(300), nullable=True)
    summary = Column(Text, nullable=False)
    mechanism = Column(Text, nullable=True)
    food_groups = Column(JSON)  # e.g. ["leafy_greens","grapefruit"]
    recommended_actions = Column(Text, nullable=True)
    evidence_quality = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Reference(Base):
    __tablename__ = "references"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    excerpt = Column(Text, nullable=True)

    interaction = relationship("Interaction", backref="references")


class APICache(Base):
    __tablename__ = "api_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    api_source = Column(String(50), nullable=False)  # rxnorm, fda, pubchem, etc.
    response_data = Column(JSON, nullable=False)  # Cached API response
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
