"""Instagram JSON data parser for Meta's data export format."""

import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class ParsedInstagramData:
    """Structured representation of parsed Instagram data."""
    
    # Accounts the user follows
    following: list[str] = field(default_factory=list)
    
    # Liked posts/reels (URLs or media IDs)
    liked_posts: list[dict[str, Any]] = field(default_factory=list)
    
    # Saved posts/reels
    saved_posts: list[dict[str, Any]] = field(default_factory=list)
    
    # Comments made by the user
    comments: list[dict[str, Any]] = field(default_factory=list)
    
    # Raw data for additional context
    raw_data: dict[str, Any] = field(default_factory=dict)
    
    def summary(self) -> dict[str, int]:
        """Return a summary of parsed data counts."""
        return {
            "following_count": len(self.following),
            "liked_posts_count": len(self.liked_posts),
            "saved_posts_count": len(self.saved_posts),
            "comments_count": len(self.comments),
        }


class InstagramParser:
    """Parser for Instagram's JSON data export from Meta."""
    
    def __init__(self):
        self.data = ParsedInstagramData()
    
    def parse_file(self, file_path: Path | str) -> ParsedInstagramData:
        """Parse a single JSON file from Instagram export."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        return self._parse_content(content, str(file_path))
    
    def parse_json_content(self, content: dict[str, Any], filename: str = "") -> ParsedInstagramData:
        """Parse JSON content directly."""
        return self._parse_content(content, filename)
    
    def _parse_content(self, content: dict[str, Any], source: str = "") -> ParsedInstagramData:
        """Internal method to parse content based on its structure."""
        
        # Store raw data
        self.data.raw_data[source] = content
        
        # Try to detect the type of data and parse accordingly
        self._parse_following(content)
        self._parse_likes(content)
        self._parse_saved(content)
        self._parse_comments(content)
        
        return self.data
    
    def _parse_following(self, content: dict[str, Any]) -> None:
        """Extract following list from various possible structures."""
        
        # Structure 1: relationships_following format
        if "relationships_following" in content:
            for item in content["relationships_following"]:
                if "string_list_data" in item:
                    for string_data in item["string_list_data"]:
                        if "value" in string_data:
                            self.data.following.append(string_data["value"])
        
        # Structure 2: Direct following array
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "string_list_data" in item:
                    for string_data in item["string_list_data"]:
                        if "value" in string_data:
                            self.data.following.append(string_data["value"])
        
        # Structure 3: followers_and_following folder format
        if "following" in content:
            following_data = content["following"]
            if isinstance(following_data, list):
                for item in following_data:
                    if isinstance(item, str):
                        self.data.following.append(item)
                    elif isinstance(item, dict):
                        username = item.get("username") or item.get("value") or item.get("name")
                        if username:
                            self.data.following.append(username)
    
    def _parse_likes(self, content: dict[str, Any]) -> None:
        """Extract liked posts from various possible structures."""
        
        # Structure 1: likes_media_likes format
        if "likes_media_likes" in content:
            for item in content["likes_media_likes"]:
                like_data = self._extract_media_data(item)
                if like_data:
                    self.data.liked_posts.append(like_data)
        
        # Structure 2: Direct likes array
        if "likes" in content:
            likes_data = content["likes"]
            if isinstance(likes_data, list):
                for item in likes_data:
                    like_data = self._extract_media_data(item)
                    if like_data:
                        self.data.liked_posts.append(like_data)
        
        # Structure 3: liked_posts key
        if "liked_posts" in content:
            for item in content["liked_posts"]:
                like_data = self._extract_media_data(item)
                if like_data:
                    self.data.liked_posts.append(like_data)
    
    def _parse_saved(self, content: dict[str, Any]) -> None:
        """Extract saved posts from various possible structures."""
        
        # Structure 1: saved_saved_media format
        if "saved_saved_media" in content:
            for item in content["saved_saved_media"]:
                saved_data = self._extract_media_data(item)
                if saved_data:
                    self.data.saved_posts.append(saved_data)
        
        # Structure 2: Direct saved_media array
        if "saved_media" in content:
            for item in content["saved_media"]:
                saved_data = self._extract_media_data(item)
                if saved_data:
                    self.data.saved_posts.append(saved_data)
        
        # Structure 3: saved_posts key
        if "saved_posts" in content:
            for item in content["saved_posts"]:
                saved_data = self._extract_media_data(item)
                if saved_data:
                    self.data.saved_posts.append(saved_data)
    
    def _parse_comments(self, content: dict[str, Any]) -> None:
        """Extract comments from various possible structures."""
        
        # Structure 1: comments_media_comments format
        if "comments_media_comments" in content:
            for item in content["comments_media_comments"]:
                comment_data = self._extract_comment_data(item)
                if comment_data:
                    self.data.comments.append(comment_data)
        
        # Structure 2: Direct comments array
        if "comments" in content:
            for item in content["comments"]:
                comment_data = self._extract_comment_data(item)
                if comment_data:
                    self.data.comments.append(comment_data)
    
    def _extract_media_data(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Extract relevant data from a media item."""
        result = {}
        
        # Extract title/caption
        if "title" in item:
            result["title"] = item["title"]
        
        # Extract from string_list_data (common Meta format)
        if "string_list_data" in item:
            for string_data in item["string_list_data"]:
                if "href" in string_data:
                    result["url"] = string_data["href"]
                if "value" in string_data:
                    result["value"] = string_data["value"]
                if "timestamp" in string_data:
                    result["timestamp"] = string_data["timestamp"]
        
        # Direct URL
        if "href" in item:
            result["url"] = item["href"]
        
        # Media owner
        if "media_owner" in item:
            result["owner"] = item["media_owner"]
        elif "owner" in item:
            result["owner"] = item["owner"]
        
        # Timestamp
        if "timestamp" in item and "timestamp" not in result:
            result["timestamp"] = item["timestamp"]
        
        return result if result else None
    
    def _extract_comment_data(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Extract relevant data from a comment item."""
        result = {}
        
        # Extract title (usually the comment text)
        if "title" in item:
            result["text"] = item["title"]
        
        # Extract from string_list_data
        if "string_list_data" in item:
            for string_data in item["string_list_data"]:
                if "value" in string_data:
                    result["text"] = string_data.get("value", result.get("text", ""))
                if "href" in string_data:
                    result["post_url"] = string_data["href"]
                if "timestamp" in string_data:
                    result["timestamp"] = string_data["timestamp"]
        
        # Media owner (who the comment was on)
        if "media_owner" in item:
            result["post_owner"] = item["media_owner"]
        
        # Timestamp
        if "timestamp" in item and "timestamp" not in result:
            result["timestamp"] = item["timestamp"]
        
        return result if result else None
    
    def merge_data(self, other: ParsedInstagramData) -> None:
        """Merge another ParsedInstagramData into this one."""
        self.data.following.extend(other.following)
        self.data.liked_posts.extend(other.liked_posts)
        self.data.saved_posts.extend(other.saved_posts)
        self.data.comments.extend(other.comments)
        self.data.raw_data.update(other.raw_data)
        
        # Remove duplicates from following
        self.data.following = list(set(self.data.following))


def parse_instagram_export(json_data: dict[str, Any]) -> ParsedInstagramData:
    """Convenience function to parse Instagram export data."""
    parser = InstagramParser()
    return parser.parse_json_content(json_data)


def parse_multiple_files(file_contents: list[tuple[str, dict[str, Any]]]) -> ParsedInstagramData:
    """Parse multiple JSON files and merge the results."""
    parser = InstagramParser()
    
    for filename, content in file_contents:
        parser.parse_json_content(content, filename)
    
    return parser.data
