from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class NarrativeScores(BaseModel):
    VS: float  # Virality Score
    LRS: Optional[float] = None  # Launch Readiness Score
    
class NarrativeStats(BaseModel):
    mentions: int
    growth_rate: float
    sentiment: float
    influencers: float

class NarrativeResponse(BaseModel):
    id: int
    label: str
    scores: NarrativeScores
    stats: NarrativeStats
    sources: Dict[str, float]
    keywords: List[str]
    category: Optional[str]
    created_at: datetime
    last_seen: datetime

class TopNarrativesResponse(BaseModel):
    narratives: List[NarrativeResponse]
    window: str
    total_count: int
    generated_at: datetime

class MentionResponse(BaseModel):
    id: int
    source: str
    source_id: str
    author: Optional[str]
    text: Optional[str]
    url: Optional[str]
    created_at: datetime
    metrics: Dict[str, Any]
    lang: Optional[str]
    entities: Dict[str, Any]
    
class CoinIdeaResponse(BaseModel):
    name: str
    symbol: str
    description: str
    tagline: str
    emoji_set: List[str]
    risk_flags: Dict[str, Any]