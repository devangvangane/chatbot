from fastapi import APIRouter, HTTPException, Header
from app.services.git_service import GitHubService
from app.config import config
import json

from app.services.vectordb_service import VectorDB
from app.services.youtube_fetch import YouTubeService
from app.utils.logger import logger

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])


@router.post("/update/youtube")
async def update_youtube_kb(admin_secret_key: str = Header(...)):
    if admin_secret_key != config.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        youtube_s = YouTubeService()
        videos = youtube_s.get_channel_videos()
        logger.info(f"Fetched {len(videos)} YouTube videos")

        vectordb = VectorDB()
        success = vectordb.ingest(videos, source="youtube")

        return {"success": success, "count": len(videos), "source": "youtube"}
    except Exception as e:
        logger.error(f"YouTube KB update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update/github")
async def update_github_kb(admin_secret_key: str =  Header(...)):
    if admin_secret_key != config.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        # You'll need a GitHubService similar to YouTubeService — see note below

        github_s = GitHubService()
        repos = github_s.get_repos()
        logger.info(f"Fetched {len(repos)} GitHub repos")

        vectordb = VectorDB()
        success = vectordb.ingest(repos, source="github")

        return {"success": success, "count": len(repos), "source": "github"}
    except Exception as e:
        logger.error(f"GitHub KB update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))