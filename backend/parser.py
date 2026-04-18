"""
Instagram Data Export Parser

Handles ZIP extraction and JSON parsing with strict privacy allowlist.
Only processes the 5 allowed categories: likes, saved, comments, following, topics.
"""

import json
import zipfile
import io
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from scoring_config import ALLOWED_FILES


class InstagramDataParser:
    """
    Parses Instagram data export ZIP files.
    Only extracts data from the privacy-approved allowlist.
    """
    
    def __init__(self):
        self.allowed_patterns = self._compile_allowed_patterns()
    
    def _compile_allowed_patterns(self) -> List[str]:
        """Convert allowlist to flexible matching patterns."""
        patterns = []
        for allowed_file in ALLOWED_FILES:
            # Create pattern that matches the file anywhere in the ZIP structure
            # Instagram exports can have varying directory structures
            pattern = allowed_file.replace("/", r"[/\\]")
            patterns.append(pattern)
        return patterns
    
    def _is_allowed_file(self, filepath: str) -> bool:
        """Check if a file path matches any allowed pattern."""
        filepath_normalized = filepath.replace("\\", "/").lower()
        
        for allowed in ALLOWED_FILES:
            allowed_normalized = allowed.lower()
            # Check if the filepath ends with the allowed file pattern
            if filepath_normalized.endswith(allowed_normalized):
                return True
            # Also check if the filename matches (for root-level files)
            if filepath_normalized.split("/")[-1] == allowed_normalized.split("/")[-1]:
                return True
        return False
    
    def _categorize_file(self, filepath: str) -> Optional[str]:
        """Determine which category a file belongs to."""
        filepath_lower = filepath.lower()
        
        if "like" in filepath_lower:
            return "likes"
        elif "saved" in filepath_lower:
            return "saved"
        elif "comment" in filepath_lower:
            return "comments"
        elif "following" in filepath_lower:
            return "following"
        elif "topic" in filepath_lower:
            return "topics"
        return None
    
    def parse_zip(self, zip_content: bytes) -> Dict[str, Any]:
        """
        Parse an Instagram data export ZIP file.
        
        Args:
            zip_content: Raw bytes of the ZIP file
            
        Returns:
            Dictionary with categorized data:
            {
                "likes": [...],
                "saved": [...],
                "comments": [...],
                "following": [...],
                "topics": [...]
            }
        """
        result = {
            "likes": [],
            "saved": [],
            "comments": [],
            "following": [],
            "topics": [],
            "_metadata": {
                "files_processed": [],
                "files_skipped": 0,
            }
        }
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zf:
                for filename in zf.namelist():
                    # Skip directories
                    if filename.endswith('/'):
                        continue
                    
                    # Skip non-JSON files
                    if not filename.lower().endswith('.json'):
                        result["_metadata"]["files_skipped"] += 1
                        continue
                    
                    # Check against allowlist
                    if not self._is_allowed_file(filename):
                        result["_metadata"]["files_skipped"] += 1
                        continue
                    
                    # Determine category
                    category = self._categorize_file(filename)
                    if not category:
                        result["_metadata"]["files_skipped"] += 1
                        continue
                    
                    # Parse JSON content
                    try:
                        content = zf.read(filename)
                        data = json.loads(content.decode('utf-8'))
                        
                        # Extract and normalize data based on category
                        extracted = self._extract_data(data, category)
                        result[category].extend(extracted)
                        result["_metadata"]["files_processed"].append(filename)
                        
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        # Skip malformed files
                        result["_metadata"]["files_skipped"] += 1
                        continue
                        
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file provided")
        
        return result
    
    def _extract_data(self, data: Any, category: str) -> List[Dict]:
        """
        Extract relevant data from parsed JSON based on category.
        Normalizes different Instagram export formats.
        """
        extracted = []
        
        if category == "likes":
            extracted = self._extract_likes(data)
        elif category == "saved":
            extracted = self._extract_saved(data)
        elif category == "comments":
            extracted = self._extract_comments(data)
        elif category == "following":
            extracted = self._extract_following(data)
        elif category == "topics":
            extracted = self._extract_topics(data)
        
        return extracted
    
    def _extract_likes(self, data: Any) -> List[Dict]:
        """Extract liked posts data.
        
        Actual Instagram format:
        {
            "likes_media_likes": [
                {
                    "title": "account_name",
                    "string_list_data": [{"href": "...", "timestamp": 123}]
                }
            ]
        }
        """
        likes = []
        
        # Handle different Instagram export formats
        if isinstance(data, dict):
            if "likes_media_likes" in data:
                data = data["likes_media_likes"]
            elif "likes_comment_likes" in data:
                data = data["likes_comment_likes"]
            else:
                data = list(data.values())[0] if data else []
        
        if isinstance(data, list):
            for item in data:
                like_entry = {}
                
                if isinstance(item, dict):
                    # PRIMARY: Account name is in the "title" field
                    if "title" in item and item["title"]:
                        like_entry["account"] = item["title"]
                        like_entry["content"] = item["title"]
                    
                    # Get URL and timestamp from string_list_data
                    if "string_list_data" in item:
                        for sld in item["string_list_data"]:
                            if "href" in sld:
                                like_entry["url"] = sld["href"]
                            if "value" in sld and "account" not in like_entry:
                                like_entry["account"] = sld["value"]
                            if "timestamp" in sld:
                                like_entry["timestamp"] = sld["timestamp"]
                
                if like_entry and "account" in like_entry:
                    likes.append(like_entry)
        
        return likes
    
    def _extract_saved(self, data: Any) -> List[Dict]:
        """Extract saved posts data.
        
        Actual Instagram format:
        {
            "saved_saved_media": [
                {
                    "title": "account_name",
                    "string_list_data": [{"href": "...", "timestamp": 123}]
                }
            ]
        }
        """
        saved = []
        
        if isinstance(data, dict):
            if "saved_saved_media" in data:
                data = data["saved_saved_media"]
            elif "saved_saved_collections" in data:
                data = data["saved_saved_collections"]
            else:
                data = list(data.values())[0] if data else []
        
        if isinstance(data, list):
            for item in data:
                saved_entry = {}
                
                if isinstance(item, dict):
                    # PRIMARY: Account name is in the "title" field
                    if "title" in item and item["title"]:
                        saved_entry["account"] = item["title"]
                        saved_entry["content"] = item["title"]
                    
                    # Get URL from string_map_data or string_list_data
                    if "string_map_data" in item:
                        for key, val in item["string_map_data"].items():
                            if isinstance(val, dict) and "href" in val:
                                saved_entry["url"] = val["href"]
                    
                    if "string_list_data" in item:
                        for sld in item["string_list_data"]:
                            if "href" in sld:
                                saved_entry["url"] = sld["href"]
                            if "value" in sld and "account" not in saved_entry:
                                saved_entry["account"] = sld["value"]
                            if "timestamp" in sld:
                                saved_entry["timestamp"] = sld["timestamp"]
                
                if saved_entry and "account" in saved_entry:
                    saved.append(saved_entry)
        
        return saved
    
    def _extract_comments(self, data: Any) -> List[Dict]:
        """Extract comments data (style analysis, not content exposure)."""
        comments = []
        
        if isinstance(data, dict):
            if "comments_media_comments" in data:
                data = data["comments_media_comments"]
            else:
                data = list(data.values())[0] if data else []
        
        if isinstance(data, list):
            for item in data:
                comment_entry = {}
                
                if isinstance(item, dict):
                    # We extract metadata for style analysis, not the actual comment text
                    if "string_map_data" in item:
                        comment_data = item["string_map_data"]
                        if "Comment" in comment_data:
                            text = comment_data["Comment"].get("value", "")
                            # Store style metrics, not the actual text
                            comment_entry["length"] = len(text)
                            comment_entry["has_emoji"] = bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
                            comment_entry["has_question"] = "?" in text
                            comment_entry["word_count"] = len(text.split())
                    
                    if "timestamp" in item:
                        comment_entry["timestamp"] = item["timestamp"]
                
                if comment_entry:
                    comments.append(comment_entry)
        
        return comments
    
    def _extract_following(self, data: Any) -> List[Dict]:
        """Extract following list data.
        
        Actual Instagram format:
        {
            "relationships_following": [
                {
                    "title": "username_here",
                    "string_list_data": [{"href": "...", "timestamp": 123}]
                }
            ]
        }
        """
        following = []
        
        if isinstance(data, dict):
            if "relationships_following" in data:
                data = data["relationships_following"]
            else:
                # Try first value if it's a dict
                data = list(data.values())[0] if data else []
        
        if isinstance(data, list):
            for item in data:
                follow_entry = {}
                
                if isinstance(item, dict):
                    # PRIMARY: Username is in the "title" field
                    if "title" in item and item["title"]:
                        follow_entry["username"] = item["title"]
                    
                    # Get URL from string_list_data
                    if "string_list_data" in item:
                        for sld in item["string_list_data"]:
                            if "href" in sld:
                                follow_entry["url"] = sld["href"]
                            if "timestamp" in sld:
                                follow_entry["timestamp"] = sld["timestamp"]
                    
                    # Fallback: check value field
                    if "username" not in follow_entry and "value" in item:
                        follow_entry["username"] = item["value"]
                
                if follow_entry and "username" in follow_entry:
                    following.append(follow_entry)
        
        return following
    
    def _extract_topics(self, data: Any) -> List[Dict]:
        """Extract Instagram's inferred topics/interests."""
        topics = []
        
        if isinstance(data, dict):
            if "topics_your_topics" in data:
                data = data["topics_your_topics"]
            else:
                data = list(data.values())[0] if data else []
        
        if isinstance(data, list):
            for item in data:
                topic_entry = {}
                
                if isinstance(item, dict):
                    if "string_map_data" in item:
                        topic_data = item["string_map_data"]
                        if "Name" in topic_data:
                            topic_entry["name"] = topic_data["Name"].get("value", "")
                    if "value" in item:
                        topic_entry["name"] = item["value"]
                    if "title" in item:
                        topic_entry["name"] = item["title"]
                
                elif isinstance(item, str):
                    topic_entry["name"] = item
                
                if topic_entry and topic_entry.get("name"):
                    topics.append(topic_entry)
        
        return topics


# Convenience function
def parse_instagram_export(zip_content: bytes) -> Dict[str, Any]:
    """Parse an Instagram data export ZIP file."""
    parser = InstagramDataParser()
    return parser.parse_zip(zip_content)
