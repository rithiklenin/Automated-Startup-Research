from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import logging
import os
from pathlib import Path

from app.services.database import DatabaseService
from app.services.research_service import ResearchService
from app.models.startup import Startup

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Startup Research API")

class StartupRequest(BaseModel):
    startups: List[str]

class ChatRequest(BaseModel):
    query: str


def get_db_service():
    return DatabaseService()


def get_research_service(db_service: DatabaseService = Depends(get_db_service)):
    return ResearchService(db_service)


@app.post("/api/research", response_model=List[Startup])
async def research_startups(
    request: StartupRequest,
    research_service: ResearchService = Depends(get_research_service)
):
    if not request.startups:
        raise HTTPException(status_code=400, detail="No startups provided")
    
    results = await research_service.research_startups(request.startups)
    return results

@app.get("/api/startups", response_model=List[Startup])
async def get_all_startups(
    db_service: DatabaseService = Depends(get_db_service)
):
    return db_service.get_all_startups()

@app.get("/api/startups/{startup_id}", response_model=Startup)
async def get_startup(
    startup_id: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    startup = db_service.get_startup(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup

@app.post("/api/chat", response_model=Dict[str, Any])
async def chat_query(
    request: ChatRequest,
    db_service: DatabaseService = Depends(get_db_service)
):
    query = request.query.lower()
    
    if any(word in query for word in ["industry", "sector", "industries"]):
        return db_service.run_analytics("industry_count")
    
    
    elif any(word in query for word in ["funding", "investment", "money", "raised"]):
        return db_service.run_analytics("funding_stats")
    
    
    elif any(word in query for word in ["founder", "started", "created"]):
        startups = db_service.get_all_startups()
        founders = {s.name: s.founders for s in startups if s.founders}
        return {"type": "founders", "data": founders}
    
    
    elif any(word in query for word in ["location", "headquarter", "based", "where"]):
        startups = db_service.get_all_startups()
        locations = {s.name: s.headquarters for s in startups if s.headquarters}
        return {"type": "locations", "data": locations}
    
    
    else:
        results = db_service.search_startups(query)
        return {"type": "search_results", "data": [r.model_dump() for r in results]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)