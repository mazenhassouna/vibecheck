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
    username: str = ""  # Instagram username (extracted from filename)
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
            "user_a_username": self.user_a.username or "Person A",
            "user_b_joined": self.user_b is not None,
            "user_b_uploaded": self.user_b.uploaded if self.user_b else False,
            "user_b_username": self.user_b.username if self.user_b else "Person B",
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
