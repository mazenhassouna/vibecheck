"""FastAPI server for vibecheck."""

import json
import asyncio
import logging
from typing import Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import config
from parser import InstagramParser, ParsedInstagramData, parse_zip_file
from instagram_scraper import enrich_user_data, extract_profile_info, extract_reel_info
from llm_analyzer import analyze_and_compare

# Create FastAPI app
app = FastAPI(
    title="Vibecheck",
    description="Find what you have in common with someone based on Instagram data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""
    user_a_data: dict[str, Any]
    user_b_data: dict[str, Any]
    skip_scraping: bool = False


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    success: bool
    vibe_score: int
    tier: str
    tier_description: str
    exact_matches: list[dict[str, Any]]
    category_matches: list[dict[str, Any]]
    broad_overlaps: list[dict[str, Any]]
    unique_to_a: list[str]
    unique_to_b: list[str]
    narrative: str
    user_a_summary: str
    user_b_summary: str


@app.get("/")
async def root():
    """Serve the frontend."""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Vibecheck API is running. Frontend not found."}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    missing_keys = config.validate()
    return {
        "status": "healthy" if not missing_keys else "degraded",
        "missing_config": missing_keys,
        "version": "1.0.0"
    }


@app.post("/api/parse")
async def parse_instagram_data(file: UploadFile = File(...)):
    """
    Parse an uploaded Instagram JSON data export.
    
    Returns parsed data summary without enrichment.
    """
    try:
        # Read and parse the uploaded file
        content = await file.read()
        json_data = json.loads(content.decode("utf-8"))
        
        # Parse the data
        parser = InstagramParser()
        parsed = parser.parse_json_content(json_data, file.filename)
        
        return {
            "success": True,
            "filename": file.filename,
            "summary": parsed.summary(),
            "following": parsed.following[:100],  # Limit for response size
            "liked_posts_sample": parsed.liked_posts[:20],
            "saved_posts_sample": parsed.saved_posts[:20],
            "comments_sample": parsed.comments[:20],
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse-multiple")
async def parse_multiple_files(files: list[UploadFile] = File(...)):
    """
    Parse multiple Instagram JSON data export files.
    
    Useful when user uploads multiple files from their export.
    """
    try:
        parser = InstagramParser()
        
        for file in files:
            content = await file.read()
            try:
                json_data = json.loads(content.decode("utf-8"))
                parser.parse_json_content(json_data, file.filename)
            except json.JSONDecodeError:
                # Skip invalid files
                continue
        
        parsed = parser.data
        
        return {
            "success": True,
            "files_processed": len(files),
            "summary": parsed.summary(),
            "following": parsed.following[:100],
            "liked_posts_sample": parsed.liked_posts[:20],
            "saved_posts_sample": parsed.saved_posts[:20],
            "comments_sample": parsed.comments[:20],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def parse_user_files(files: list[UploadFile]) -> ParsedInstagramData:
    """Parse user files, supporting both ZIP and JSON formats."""
    logger.info(f"Parsing {len(files)} files")
    parser = InstagramParser()
    
    for file in files:
        content = await file.read()
        filename = file.filename or ""
        logger.info(f"Processing file: {filename} ({len(content)} bytes)")
        
        try:
            if filename.lower().endswith('.zip'):
                # Parse ZIP file
                logger.info(f"Detected ZIP file: {filename}")
                zip_data = parse_zip_file(content)
                logger.info(f"ZIP parsed: {zip_data.summary()}")
                parser.merge_data(zip_data)
            elif filename.lower().endswith('.json'):
                # Parse JSON file
                logger.info(f"Detected JSON file: {filename}")
                try:
                    json_str = content.decode('utf-8')
                except UnicodeDecodeError:
                    json_str = content.decode('latin-1')
                json_data = json.loads(json_str)
                parser.parse_json_content(json_data, filename)
        except Exception as e:
            logger.error(f"Error parsing {filename}: {e}", exc_info=True)
            continue
    
    logger.info(f"Total parsed data: {parser.data.summary()}")
    return parser.data


@app.post("/api/analyze")
async def analyze_users(
    user_a_files: list[UploadFile] = File(..., description="User A's Instagram data files (ZIP or JSON)"),
    user_b_files: list[UploadFile] = File(..., description="User B's Instagram data files (ZIP or JSON)"),
    skip_scraping: bool = False
):
    """
    Full analysis pipeline: parse, enrich, and compare two users.
    
    Accepts ZIP files (Instagram data export) or individual JSON files.
    
    Args:
        user_a_files: Instagram data files for User A (ZIP or JSON)
        user_b_files: Instagram data files for User B (ZIP or JSON)
        skip_scraping: If True, skip Apify scraping (for testing/quick mode)
    """
    logger.info("="*50)
    logger.info("Starting analysis request")
    logger.info(f"User A files: {[f.filename for f in user_a_files]}")
    logger.info(f"User B files: {[f.filename for f in user_b_files]}")
    logger.info(f"Skip scraping: {skip_scraping}")
    
    try:
        # Parse both users' data (supports ZIP and JSON)
        logger.info("Parsing User A files...")
        parsed_a = await parse_user_files(user_a_files)
        logger.info("Parsing User B files...")
        parsed_b = await parse_user_files(user_b_files)
        
        # Prepare data for analysis
        if skip_scraping:
            logger.info("Skip scraping enabled - using parsed data directly")
            # Use parsed data directly without enrichment
            user_a_data = {
                "profiles": [{"username": u, "followersCount": 10000} for u in parsed_a.following[:50]],
                "reels": [],
                "comments": parsed_a.comments,
            }
            user_b_data = {
                "profiles": [{"username": u, "followersCount": 10000} for u in parsed_b.following[:50]],
                "reels": [],
                "comments": parsed_b.comments,
            }
            logger.info(f"User A: {len(user_a_data['profiles'])} profiles, {len(user_a_data['comments'])} comments")
            logger.info(f"User B: {len(user_b_data['profiles'])} profiles, {len(user_b_data['comments'])} comments")
        else:
            # Enrich with Apify scraping
            liked_urls_a = [p.get("url", "") for p in parsed_a.liked_posts if p.get("url")]
            saved_urls_a = [p.get("url", "") for p in parsed_a.saved_posts if p.get("url")]
            liked_urls_b = [p.get("url", "") for p in parsed_b.liked_posts if p.get("url")]
            saved_urls_b = [p.get("url", "") for p in parsed_b.saved_posts if p.get("url")]
            
            # Enrich both users in parallel
            enriched_a, enriched_b = await asyncio.gather(
                enrich_user_data(parsed_a.following, liked_urls_a, saved_urls_a),
                enrich_user_data(parsed_b.following, liked_urls_b, saved_urls_b)
            )
            
            user_a_data = {
                "profiles": enriched_a.filtered_profiles,
                "reels": enriched_a.reels,
                "comments": parsed_a.comments,
            }
            user_b_data = {
                "profiles": enriched_b.filtered_profiles,
                "reels": enriched_b.reels,
                "comments": parsed_b.comments,
            }
        
        # Run LLM analysis
        logger.info("Starting LLM analysis...")
        result = await analyze_and_compare(user_a_data, user_b_data)
        
        logger.info("LLM analysis complete")
        comparison = result["comparison"]
        logger.info(f"Vibe Score: {comparison.get('vibe_score', 'N/A')}")
        logger.info(f"Tier: {comparison.get('tier', 'N/A')}")
        logger.info("="*50)
        
        return {
            "success": True,
            "vibe_score": comparison.get("vibe_score", 0),
            "tier": comparison.get("tier", "Unknown"),
            "tier_description": comparison.get("tier_description", ""),
            "exact_matches": comparison.get("exact_matches", []),
            "category_matches": comparison.get("category_matches", []),
            "broad_overlaps": comparison.get("broad_overlaps", []),
            "unique_to_a": comparison.get("unique_to_a", []),
            "unique_to_b": comparison.get("unique_to_b", []),
            "narrative": comparison.get("narrative", ""),
            "user_a_summary": result["user_a_profile"].get("summary", ""),
            "user_b_summary": result["user_b_profile"].get("summary", ""),
            "user_a_interests": result["user_a_profile"].get("interests", [])[:10],
            "user_b_interests": result["user_b_profile"].get("interests", [])[:10],
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-json")
async def analyze_users_json(request: AnalysisRequest):
    """
    Analyze two users from pre-parsed JSON data.
    
    Useful for testing or when data is already parsed.
    """
    try:
        # Run LLM analysis directly
        result = await analyze_and_compare(request.user_a_data, request.user_b_data)
        
        comparison = result["comparison"]
        
        return {
            "success": True,
            "vibe_score": comparison.get("vibe_score", 0),
            "tier": comparison.get("tier", "Unknown"),
            "tier_description": comparison.get("tier_description", ""),
            "exact_matches": comparison.get("exact_matches", []),
            "category_matches": comparison.get("category_matches", []),
            "broad_overlaps": comparison.get("broad_overlaps", []),
            "unique_to_a": comparison.get("unique_to_a", []),
            "unique_to_b": comparison.get("unique_to_b", []),
            "narrative": comparison.get("narrative", ""),
            "user_a_summary": result["user_a_profile"].get("summary", ""),
            "user_b_summary": result["user_b_profile"].get("summary", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
