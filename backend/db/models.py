from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from db.database import Base

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
