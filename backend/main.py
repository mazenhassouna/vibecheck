"""
Instagram Compatibility API

FastAPI backend for the Instagram compatibility analysis service.
Handles session management, file uploads, and compatibility scoring.
"""

import os
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from parser import parse_instagram_export
from analyzer import analyze_compatibility
from gemini_client import create_gemini_client
from scoring_config import SCORING_CONFIG, ALLOWED_FILES

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Compatibility API",
    description="Analyze Instagram compatibility between two people",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, Dict] = {}

# Session expiry time
SESSION_EXPIRY_HOURS = 24


# Pydantic models
class SessionResponse(BaseModel):
    session_code: str
    created_at: str
    expires_at: str
    status: str


class SessionStatus(BaseModel):
    session_code: str
    status: str
    person_a_uploaded: bool
    person_b_uploaded: bool
    result_ready: bool


class CompatibilityResult(BaseModel):
    score: int
    label: dict
    breakdown: dict
    shared_interests: list
    conversation_starters: list
    bonus_points: int


# Helper functions
def generate_session_code() -> str:
    """Generate a friendly 6-character session code."""
    # Use uppercase letters and numbers, avoiding confusing characters
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(6))


def cleanup_expired_sessions():
    """Remove expired sessions."""
    now = datetime.utcnow()
    expired = [
        code for code, session in sessions.items()
        if session["expires_at"] < now
    ]
    for code in expired:
        del sessions[code]


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Instagram Compatibility API",
        "version": "1.0.0"
    }


@app.get("/api/privacy-info")
async def get_privacy_info():
    """Return information about what data is processed."""
    return {
        "allowed_categories": [
            {
                "name": "Likes",
                "description": "Content you've liked - used to identify shared interests",
                "files": ["likes/liked_posts.json"]
            },
            {
                "name": "Saved Posts",
                "description": "Posts you've saved - indicates strong interests",
                "files": ["saved/saved_posts.json"]
            },
            {
                "name": "Comments",
                "description": "Your engagement style (not actual comment text)",
                "files": ["comments/post_comments.json"]
            },
            {
                "name": "Following",
                "description": "Accounts you follow - shows your interests",
                "files": ["following.json"]
            },
            {
                "name": "Topics",
                "description": "Instagram's inferred interest topics",
                "files": ["your_topics/your_topics.json"]
            }
        ],
        "blocked_data": [
            "Messages/DMs",
            "Search history",
            "Login activity",
            "Personal information",
            "Story interactions",
            "Device information"
        ],
        "data_handling": "Your data is processed in memory and deleted immediately after analysis."
    }


@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new matching session."""
    cleanup_expired_sessions()
    
    # Generate unique session code
    session_code = generate_session_code()
    while session_code in sessions:
        session_code = generate_session_code()
    
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=SESSION_EXPIRY_HOURS)
    
    sessions[session_code] = {
        "created_at": now,
        "expires_at": expires_at,
        "status": "waiting_for_uploads",
        "person_a": None,
        "person_b": None,
        "result": None,
    }
    
    return SessionResponse(
        session_code=session_code,
        created_at=now.isoformat(),
        expires_at=expires_at.isoformat(),
        status="waiting_for_uploads"
    )


@app.get("/api/sessions/{session_code}", response_model=SessionStatus)
async def get_session_status(session_code: str):
    """Get the status of a session."""
    session_code = session_code.upper()
    
    if session_code not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_code]
    
    if session["expires_at"] < datetime.utcnow():
        del sessions[session_code]
        raise HTTPException(status_code=404, detail="Session expired")
    
    return SessionStatus(
        session_code=session_code,
        status=session["status"],
        person_a_uploaded=session["person_a"] is not None,
        person_b_uploaded=session["person_b"] is not None,
        result_ready=session["result"] is not None
    )


@app.post("/api/sessions/{session_code}/upload")
async def upload_data(
    session_code: str,
    file: UploadFile = File(...),
    person: str = Form(...)
):
    """Upload Instagram data export for a person."""
    session_code = session_code.upper()
    
    if session_code not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_code]
    
    if session["expires_at"] < datetime.utcnow():
        del sessions[session_code]
        raise HTTPException(status_code=404, detail="Session expired")
    
    if person not in ["a", "b"]:
        raise HTTPException(status_code=400, detail="Person must be 'a' or 'b'")
    
    person_key = f"person_{person}"
    
    if session[person_key] is not None:
        raise HTTPException(status_code=400, detail=f"Person {person.upper()} has already uploaded data")
    
    # Validate file type
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    
    # Read and parse the ZIP file
    try:
        content = await file.read()
        
        # Limit file size (50MB)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Parse the Instagram export
        parsed_data = parse_instagram_export(content)
        
        # Store parsed data (not raw file)
        session[person_key] = parsed_data
        
        # Check if both people have uploaded
        if session["person_a"] is not None and session["person_b"] is not None:
            # Calculate compatibility
            session["status"] = "analyzing"
            
            try:
                # Basic analysis
                result = analyze_compatibility(
                    session["person_a"],
                    session["person_b"]
                )
                
                # Try to enhance with Gemini
                gemini = create_gemini_client()
                if gemini:
                    try:
                        result = gemini.enhance_compatibility_result(
                            result,
                            session["person_a"],
                            session["person_b"]
                        )
                        result["summary"] = gemini.generate_compatibility_summary(result)
                    except Exception as e:
                        print(f"Gemini enhancement failed: {e}")
                        result["conversation_starters"] = []
                        result["summary"] = ""
                else:
                    result["conversation_starters"] = []
                    result["summary"] = ""
                
                session["result"] = result
                session["status"] = "completed"
                
            except Exception as e:
                session["status"] = "error"
                session["error"] = str(e)
                raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        else:
            session["status"] = "waiting_for_partner"
        
        return {
            "success": True,
            "person": person.upper(),
            "files_processed": len(parsed_data.get("_metadata", {}).get("files_processed", [])),
            "status": session["status"],
            "result_ready": session["result"] is not None
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/sessions/{session_code}/result")
async def get_result(session_code: str):
    """Get the compatibility result for a session."""
    session_code = session_code.upper()
    
    if session_code not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_code]
    
    if session["expires_at"] < datetime.utcnow():
        del sessions[session_code]
        raise HTTPException(status_code=404, detail="Session expired")
    
    if session["result"] is None:
        if session["status"] == "error":
            raise HTTPException(status_code=500, detail=session.get("error", "Analysis failed"))
        raise HTTPException(status_code=400, detail="Result not ready yet")
    
    return session["result"]


@app.delete("/api/sessions/{session_code}")
async def delete_session(session_code: str):
    """Delete a session and all its data."""
    session_code = session_code.upper()
    
    if session_code not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_code]
    
    return {"success": True, "message": "Session deleted"}


@app.get("/api/config")
async def get_config():
    """Get the current scoring configuration (for transparency)."""
    return {
        "weights": SCORING_CONFIG["weights"],
        "labels": SCORING_CONFIG["labels"],
        "max_bonus": SCORING_CONFIG["max_bonus"],
    }


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
