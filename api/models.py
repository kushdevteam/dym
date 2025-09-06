from sqlalchemy import Column, Integer, String, DateTime, Text, REAL, BIGINT, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class Mention(Base):
    __tablename__ = "mention"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    author = Column(String)
    text = Column(Text)
    url = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False)
    metrics = Column(JSONB, default={})
    lang = Column(String)
    entities = Column(JSONB, default={})
    ingest_ts = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to enriched data
    enriched = relationship("MentionEnriched", back_populates="mention", uselist=False)

class MentionEnriched(Base):
    __tablename__ = "mention_enriched"
    
    mention_id = Column(BIGINT, ForeignKey("mention.id", ondelete="CASCADE"), primary_key=True)
    sentiment = Column(REAL)
    embedding = Column(Vector(384))
    keywords = Column(ARRAY(String))
    influencers_score = Column(REAL)
    platform_features = Column(JSONB)
    toxicity = Column(REAL)
    
    # Relationship back to mention
    mention = relationship("Mention", back_populates="enriched")

class Narrative(Base):
    __tablename__ = "narrative"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True))
    centroid = Column(Vector(384))
    keywords = Column(ARRAY(String))
    category = Column(String)
    
    # Relationships
    window_stats = relationship("NarrativeWindowStats", back_populates="narrative")
    coin_ideas = relationship("CoinIdea", back_populates="narrative")
    alerts = relationship("Alert", back_populates="narrative")

class NarrativeWindowStats(Base):
    __tablename__ = "narrative_window_stats"
    
    narrative_id = Column(BIGINT, ForeignKey("narrative.id", ondelete="CASCADE"), primary_key=True)
    window_start = Column(DateTime(timezone=True), primary_key=True)
    window_end = Column(DateTime(timezone=True))
    mentions = Column(Integer)
    unique_authors = Column(Integer)
    avg_engagement = Column(REAL)
    growth_rate = Column(REAL)
    sentiment = Column(REAL)
    sources = Column(JSONB)
    
    # Relationship back to narrative
    narrative = relationship("Narrative", back_populates="window_stats")

class CoinIdea(Base):
    __tablename__ = "coin_idea"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    narrative_id = Column(BIGINT, ForeignKey("narrative.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    description = Column(Text)
    tagline = Column(String)
    emoji_set = Column(ARRAY(String))
    risk_flags = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to narrative
    narrative = relationship("Narrative", back_populates="coin_ideas")

class DeployedToken(Base):
    __tablename__ = "deployed_token"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    coin_idea_id = Column(BIGINT, ForeignKey("coin_idea.id"))
    mint_address = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    decimals = Column(Integer, nullable=False)
    initial_supply = Column(BIGINT, nullable=False)
    metadata_uri = Column(String)
    raydium_pool_address = Column(String)
    deployment_tx = Column(String)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_by = Column(String)

class Alert(Base):
    __tablename__ = "alert"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    narrative_id = Column(BIGINT, ForeignKey("narrative.id", ondelete="CASCADE"))
    alert_type = Column(String, nullable=False)
    threshold_config = Column(JSONB, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String)
    
    # Relationship back to narrative
    narrative = relationship("Narrative", back_populates="alerts")