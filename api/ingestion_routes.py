from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import os
import uuid
import json
from datetime import datetime

# Use proper package imports
import importlib.util
import os

# Load the ingest module dynamically (better than sys.path manipulation)
ingest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ingest", "reddit_connector.py")
spec = importlib.util.spec_from_file_location("reddit_connector", ingest_path)
reddit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reddit_module)
RedditConnector = reddit_module.RedditConnector

router = APIRouter(prefix="/ingest", tags=["ingestion"])

# In-memory job tracking (in production, use Redis or database)
active_jobs = {}

class IngestionJobStatus(BaseModel):
    job_id: str
    source: str
    status: str  # "running", "completed", "failed"
    progress: Optional[Dict[str, Any]] = None
    mentions_count: int = 0
    message: str = ""
    started_at: datetime
    completed_at: Optional[datetime] = None

class IngestionStatus(BaseModel):
    source: str
    status: str
    mentions_count: int
    message: str

class RedditIngestionRequest(BaseModel):
    subreddits: Optional[list[str]] = None
    limit_per_subreddit: int = 50

async def run_reddit_ingestion(job_id: str, request: RedditIngestionRequest):
    """Background task to run Reddit ingestion"""
    try:
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["message"] = "Starting Reddit ingestion..."
        
        connector = RedditConnector()
        
        # Override subreddits if provided
        if request.subreddits:
            connector.subreddits = request.subreddits
            
        # Run ingestion (PRAW operations are synchronous, so we run in executor)
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            mentions_count = await loop.run_in_executor(
                executor, 
                lambda: asyncio.run(connector.ingest_all_subreddits(request.limit_per_subreddit))
            )
        
        active_jobs[job_id].update({
            "status": "completed",
            "mentions_count": mentions_count,
            "message": f"Successfully ingested {mentions_count} mentions from Reddit",
            "completed_at": datetime.utcnow()
        })
        
    except Exception as e:
        active_jobs[job_id].update({
            "status": "failed",
            "message": f"Reddit ingestion failed: {str(e)}",
            "completed_at": datetime.utcnow()
        })

@router.post("/reddit", status_code=status.HTTP_202_ACCEPTED)
async def ingest_reddit_data(request: RedditIngestionRequest, background_tasks: BackgroundTasks):
    """Trigger Reddit data ingestion as background job"""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        active_jobs[job_id] = {
            "job_id": job_id,
            "source": "reddit",
            "status": "queued",
            "progress": None,
            "mentions_count": 0,
            "message": "Job queued for processing",
            "started_at": datetime.utcnow(),
            "completed_at": None
        }
        
        # Add background task
        background_tasks.add_task(run_reddit_ingestion, job_id, request)
        
        return {
            "job_id": job_id,
            "status": "queued", 
            "message": f"Reddit ingestion job started. Use /ingest/reddit/jobs/{job_id} to check progress."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Reddit ingestion: {str(e)}")

@router.get("/reddit/jobs/{job_id}", response_model=IngestionJobStatus)
async def get_reddit_job_status(job_id: str):
    """Get status of a specific Reddit ingestion job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = active_jobs[job_id]
    return IngestionJobStatus(**job_data)

@router.get("/reddit/jobs")
async def list_reddit_jobs(limit: int = 10):
    """List recent Reddit ingestion jobs"""
    jobs = list(active_jobs.values())[-limit:]
    return {"jobs": jobs, "total": len(jobs)}

@router.get("/reddit/status", response_model=Dict[str, Any])
async def get_reddit_status():
    """Get Reddit connector status and configuration"""
    try:
        connector = RedditConnector()
        
        # Test Reddit API connectivity
        try:
            # Try to access a small subreddit to test API
            test_sub = connector.reddit.subreddit("test")
            test_sub.display_name  # This will trigger an API call
            api_status = "connected"
        except Exception as e:
            api_status = f"error: {str(e)}"
            
        return {
            "status": "configured" if os.getenv("REDDIT_CLIENT_ID") else "not_configured",
            "api_status": api_status,
            "target_subreddits": connector.subreddits,
            "subreddit_count": len(connector.subreddits)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/status")
async def get_ingestion_status():
    """Get overall ingestion system status"""
    status = {
        "reddit": {
            "configured": bool(os.getenv("REDDIT_CLIENT_ID")),
            "api_key_present": bool(os.getenv("REDDIT_CLIENT_ID"))
        },
        "telegram": {
            "configured": bool(os.getenv("TELEGRAM_API_ID")),
            "api_key_present": bool(os.getenv("TELEGRAM_API_ID"))
        },
        "twitter": {
            "configured": bool(os.getenv("TWITTER_BEARER_TOKEN")),
            "api_key_present": bool(os.getenv("TWITTER_BEARER_TOKEN"))
        }
    }
    
    return status