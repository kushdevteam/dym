from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import os
from datetime import datetime
from typing import List, Optional
import asyncio
import uvicorn

# Import our modules (will create these next)
from database import get_db_session
from models import Narrative, Mention, NarrativeWindowStats
from schemas import NarrativeResponse, TopNarrativesResponse, HealthResponse
from ingestion_routes import router as ingestion_router

# Initialize FastAPI app
app = FastAPI(
    title="Solana Narrative Scanner API",
    description="API for scanning social platforms and tracking emerging narratives",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion_router)

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with get_db_session() as db:
            await db.execute(text("SELECT 1"))
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={
                "database": "connected",
                "redis": "connected"  # Will implement redis check later
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/narratives/top", response_model=TopNarrativesResponse)
async def get_top_narratives(
    window: str = "1h",
    limit: int = 20,
    category: Optional[str] = None
):
    """Get top narratives by window and category"""
    # Placeholder implementation - will implement full logic later
    return TopNarrativesResponse(
        narratives=[],
        window=window,
        total_count=0,
        generated_at=datetime.utcnow()
    )

@app.get("/narratives/{narrative_id}", response_model=NarrativeResponse)
async def get_narrative_details(narrative_id: int):
    """Get detailed information about a specific narrative"""
    # Placeholder implementation
    raise HTTPException(status_code=404, detail="Narrative not found")

@app.get("/mentions")
async def get_mentions(
    narrative_id: Optional[int] = None,
    since: Optional[datetime] = None,
    limit: int = 100,
    source: Optional[str] = None
):
    """Get mentions, optionally filtered by narrative and time"""
    try:
        async with get_db_session() as db:
            # Build query with SQLAlchemy text() bind parameters
            query = "SELECT * FROM mention WHERE 1=1"
            params = {}
            
            if source:
                query += " AND source = :source"
                params["source"] = source
                
            if since:
                query += " AND created_at >= :since"
                params["since"] = since
                
            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit
            
            result = await db.execute(text(query), params)
            rows = result.fetchall()
            
            mentions = []
            for row in rows:
                mentions.append({
                    "id": row["id"],
                    "source": row["source"],
                    "source_id": row["source_id"],
                    "author": row["author"],
                    "text": row["text"][:200] + "..." if row["text"] and len(row["text"]) > 200 else row["text"],
                    "url": row["url"],
                    "created_at": row["created_at"].isoformat(),
                    "metrics": row["metrics"],
                    "entities": row["entities"]
                })
            
            return {
                "mentions": mentions,
                "total_count": len(mentions),
                "source_filter": source,
                "limit": limit
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mentions: {str(e)}")

@app.post("/coin_ideas")
async def generate_coin_ideas(request: dict):
    """Generate coin ideas for a narrative"""
    narrative_id = request.get("narrative_id")
    if not narrative_id:
        raise HTTPException(status_code=400, detail="narrative_id is required")
    
    # Placeholder implementation
    return {"coin_ideas": [], "narrative_id": narrative_id}

@app.post("/alerts")
async def create_alert(request: dict):
    """Create an alert for a narrative"""
    # Placeholder implementation
    return {"alert_id": 1, "status": "created"}

@app.get("/tokens/launched")
async def get_launched_tokens():
    """Get list of launched tokens"""
    # Placeholder implementation
    return {"tokens": []}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )