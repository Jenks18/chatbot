from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pydantic import AnyHttpUrl
from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User's question")
    session_id: Optional[str] = Field(None, description="Session identifier")

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    model_used: str
    response_time_ms: int
    consumer_summary: Optional[str] = None
    sources: Optional[List[str]] = None
    evidence: Optional[List[dict]] = None
    # Provenance for the consumer_summary: where it came from and which evidence IDs were used
    class Provenance(BaseModel):
        source: str
        evidence_ids: Optional[List[int]] = None

    provenance: Optional[Provenance] = None
    
    model_config = {"protected_namespaces": ()}

class ChatLogResponse(BaseModel):
    id: int
    session_id: str
    question: str
    answer: str
    model_used: Optional[str]
    response_time_ms: Optional[int]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    extra_metadata: Optional[dict] = None

    model_config = {"from_attributes": True, "protected_namespaces": ()}

class SessionResponse(BaseModel):
    session_id: str
    started_at: datetime
    last_active: datetime
    message_count: int
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    user_agent: Optional[str] = None


class Reference(BaseModel):
    id: int
    title: str
    url: AnyHttpUrl
    excerpt: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    drug_name: str
    title: Optional[str]
    summary: str
    mechanism: Optional[str]
    food_groups: Optional[List[str]]
    recommended_actions: Optional[str]
    evidence_quality: Optional[str]
    references: Optional[List[Reference]] = None

    model_config = {"from_attributes": True}

class HealthResponse(BaseModel):
    status: str
    database: str
    model_server: str
    timestamp: datetime
    
    model_config = {"protected_namespaces": ()}
