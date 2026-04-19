"""Session management for vibecheck pairing system."""

import asyncio
import logging
import random
import string
import time
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT = 30 * 60

# Max file size (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


@dataclass
class SessionUser:
    """Represents a user in a session."""
    user_id: str  # "user_a" or "user_b"
    uploaded: bool = False
    parsed_data: Optional[dict[str, Any]] = None
    upload_time: Optional[float] = None


@dataclass
class Session:
    """Represents a vibecheck session."""
    code: str
    created_at: float
    user_a: SessionUser = field(default_factory=lambda: SessionUser(user_id="user_a"))
    user_b: Optional[SessionUser] = None
    status: str = "waiting_for_partner"  # waiting_for_partner, waiting_for_uploads, analyzing, complete, error
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return time.time() - self.created_at > SESSION_TIMEOUT
    
    def both_uploaded(self) -> bool:
        """Check if both users have uploaded their data."""
        return (
            self.user_a.uploaded and 
            self.user_b is not None and 
            self.user_b.uploaded
        )
    
    def to_status_dict(self, for_user: str) -> dict[str, Any]:
        """Get session status for a specific user."""
        return {
            "code": self.code,
            "status": self.status,
            "user_a_uploaded": self.user_a.uploaded,
            "user_b_joined": self.user_b is not None,
            "user_b_uploaded": self.user_b.uploaded if self.user_b else False,
            "your_role": for_user,
            "result": self.result if self.status == "complete" else None,
            "error": self.error,
        }


class SessionManager:
    """Manages vibecheck sessions."""
    
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def generate_code(self, length: int = 6) -> str:
        """Generate a unique session code."""
        chars = string.ascii_uppercase + string.digits
        # Remove confusing characters
        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        
        while True:
            code = ''.join(random.choices(chars, k=length))
            if code not in self.sessions:
                return code
    
    def create_session(self) -> Session:
        """Create a new session."""
        code = self.generate_code()
        session = Session(
            code=code,
            created_at=time.time(),
        )
        self.sessions[code] = session
        logger.info(f"Session created: {code}")
        return session
    
    def get_session(self, code: str) -> Optional[Session]:
        """Get a session by code."""
        code = code.upper()
        session = self.sessions.get(code)
        
        if session and session.is_expired():
            logger.info(f"Session expired: {code}")
            del self.sessions[code]
            return None
        
        return session
    
    def join_session(self, code: str) -> tuple[Optional[Session], str]:
        """
        Join an existing session.
        
        Returns:
            (session, role) or (None, error_message)
        """
        code = code.upper()
        session = self.get_session(code)
        
        if not session:
            return None, "Session not found or expired"
        
        if session.user_b is not None:
            return None, "Session is full"
        
        session.user_b = SessionUser(user_id="user_b")
        session.status = "waiting_for_uploads"
        logger.info(f"User B joined session: {code}")
        
        return session, "user_b"
    
    def upload_data(self, code: str, user_role: str, parsed_data: dict[str, Any]) -> tuple[bool, str]:
        """
        Upload parsed data for a user.
        
        Returns:
            (success, message)
        """
        code = code.upper()
        session = self.get_session(code)
        
        if not session:
            return False, "Session not found or expired"
        
        if user_role == "user_a":
            session.user_a.uploaded = True
            session.user_a.parsed_data = parsed_data
            session.user_a.upload_time = time.time()
            logger.info(f"User A uploaded data to session {code}")
        elif user_role == "user_b":
            if session.user_b is None:
                return False, "User B has not joined the session"
            session.user_b.uploaded = True
            session.user_b.parsed_data = parsed_data
            session.user_b.upload_time = time.time()
            logger.info(f"User B uploaded data to session {code}")
        else:
            return False, "Invalid user role"
        
        return True, "Upload successful"
    
    def set_analyzing(self, code: str) -> None:
        """Set session status to analyzing."""
        code = code.upper()
        session = self.get_session(code)
        if session:
            session.status = "analyzing"
            logger.info(f"Session {code} is now analyzing")
    
    def set_complete(self, code: str, result: dict[str, Any]) -> None:
        """Set session as complete with results."""
        code = code.upper()
        session = self.get_session(code)
        if session:
            session.status = "complete"
            session.result = result
            logger.info(f"Session {code} analysis complete")
    
    def set_error(self, code: str, error: str) -> None:
        """Set session as errored."""
        code = code.upper()
        session = self.get_session(code)
        if session:
            session.status = "error"
            session.error = error
            logger.error(f"Session {code} error: {error}")
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        expired_codes = [
            code for code, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for code in expired_codes:
            del self.sessions[code]
        
        if expired_codes:
            logger.info(f"Cleaned up {len(expired_codes)} expired sessions")
        
        return len(expired_codes)
    
    async def start_cleanup_task(self, interval: int = 60) -> None:
        """Start background task to clean up expired sessions."""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(interval)
                self.cleanup_expired()
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("Session cleanup task started")
    
    def stop_cleanup_task(self) -> None:
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None


# Global session manager instance
session_manager = SessionManager()
