"""
Apify Client for Instagram Content Scraping

Uses official Apify scrapers to extract content from Instagram posts and reels:
- apify/instagram-reel-scraper - for reels
- apify/instagram-post-scraper - for posts
"""

import os
import time
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    print("Warning: apify-client not installed. Run: pip install apify-client")


# Configuration
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "apify_api_IcAwOvkf2zk66h4lVuo4hEcAF23L8F1DdTOg")

# Official Apify scrapers
REEL_SCRAPER_ACTOR = "apify/instagram-reel-scraper"
POST_SCRAPER_ACTOR = "apify/instagram-post-scraper"

MAX_ITEMS_PER_USER = 30
CACHE_DIR = Path("./cache/instagram")


class InstagramScraper:
    """
    Scrapes Instagram posts and reels using official Apify actors.
    """
    
    def __init__(self, api_token: str = None):
        if not APIFY_AVAILABLE:
            raise ImportError("apify-client is required. Install with: pip install apify-client")
        
        self.token = api_token or APIFY_TOKEN
        self.client = ApifyClient(self.token)
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key from a URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cached_result(self, url: str) -> Optional[Dict]:
        """Check if we have a cached result for this URL."""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def _cache_result(self, url: str, result: Dict):
        """Cache the result for a URL."""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except:
            pass
    
    def scrape_content(self, urls: List[str], max_items: int = MAX_ITEMS_PER_USER) -> List[Dict]:
        """
        Scrape content from Instagram URLs (both posts and reels).
        
        Args:
            urls: List of Instagram URLs
            max_items: Maximum number of items to scrape
            
        Returns:
            List of scraped content with captions, hashtags, etc.
        """
        # Limit URLs
        urls = urls[:max_items]
        
        # Separate into reel and post URLs
        reel_urls, post_urls = self._separate_urls(urls)
        
        results = []
        uncached_reels = []
        uncached_posts = []
        
        # Check cache for all URLs
        for url in reel_urls:
            cached = self._get_cached_result(url)
            if cached:
                results.append(cached)
            else:
                uncached_reels.append(url)
        
        for url in post_urls:
            cached = self._get_cached_result(url)
            if cached:
                results.append(cached)
            else:
                uncached_posts.append(url)
        
        print(f"[Apify] {len(results)} items from cache")
        print(f"[Apify] {len(uncached_reels)} reels + {len(uncached_posts)} posts to fetch")
        
        # Scrape uncached reels
        if uncached_reels:
            reel_results = self._scrape_reels(uncached_reels)
            results.extend(reel_results)
        
        # Scrape uncached posts
        if uncached_posts:
            post_results = self._scrape_posts(uncached_posts)
            results.extend(post_results)
        
        return results
    
    def _separate_urls(self, urls: List[str]) -> Tuple[List[str], List[str]]:
        """Separate URLs into reels and posts."""
        reel_urls = []
        post_urls = []
        
        for url in urls:
            if "/reel/" in url or "/reels/" in url:
                reel_urls.append(url)
            elif "/p/" in url:
                post_urls.append(url)
            else:
                # Try to guess - default to post
                post_urls.append(url)
        
        return reel_urls, post_urls
    
    def _scrape_reels(self, urls: List[str]) -> List[Dict]:
        """Scrape reels using apify/instagram-reel-scraper."""
        if not urls:
            return []
        
        print(f"[Apify] Scraping {len(urls)} reels...")
        
        results = []
        
        try:
            # Run the reel scraper
            run_input = {
                "directUrls": urls,
                "resultsLimit": len(urls),
            }
            
            run = self.client.actor(REEL_SCRAPER_ACTOR).call(run_input=run_input)
            
            # Get results from dataset
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                items = list(self.client.dataset(dataset_id).iterate_items())
                
                for item in items:
                    normalized = self._normalize_reel(item)
                    if normalized:
                        results.append(normalized)
                        # Cache for future use
                        if normalized.get("url"):
                            self._cache_result(normalized["url"], normalized)
            
            print(f"[Apify] Got {len(results)} reel results")
            
        except Exception as e:
            print(f"[Apify] Error scraping reels: {e}")
        
        return results
    
    def _scrape_posts(self, urls: List[str]) -> List[Dict]:
        """Scrape posts using apify/instagram-post-scraper."""
        if not urls:
            return []
        
        print(f"[Apify] Scraping {len(urls)} posts...")
        
        results = []
        
        try:
            # Run the post scraper
            run_input = {
                "directUrls": urls,
                "resultsLimit": len(urls),
            }
            
            run = self.client.actor(POST_SCRAPER_ACTOR).call(run_input=run_input)
            
            # Get results from dataset
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                items = list(self.client.dataset(dataset_id).iterate_items())
                
                for item in items:
                    normalized = self._normalize_post(item)
                    if normalized:
                        results.append(normalized)
                        # Cache for future use
                        if normalized.get("url"):
                            self._cache_result(normalized["url"], normalized)
            
            print(f"[Apify] Got {len(results)} post results")
            
        except Exception as e:
            print(f"[Apify] Error scraping posts: {e}")
        
        return results
    
    def _normalize_reel(self, item: Dict) -> Optional[Dict]:
        """Normalize reel scraper output to standard format."""
        try:
            # Extract caption/description
            caption = (
                item.get("caption") or 
                item.get("description") or 
                item.get("text") or 
                ""
            )
            
            # Extract hashtags
            hashtags = item.get("hashtags", [])
            if not hashtags and caption:
                import re
                hashtags = re.findall(r'#(\w+)', caption)
            
            return {
                "type": "reel",
                "url": item.get("url") or item.get("inputUrl") or "",
                "caption": caption,
                "hashtags": hashtags,
                "audio_name": (
                    item.get("musicInfo", {}).get("title") or
                    item.get("audioName") or
                    item.get("audio", {}).get("title") or
                    ""
                ),
                "creator": (
                    item.get("ownerUsername") or 
                    item.get("owner", {}).get("username") or
                    ""
                ),
                "likes_count": item.get("likesCount") or item.get("likes", 0),
                "views_count": item.get("videoViewCount") or item.get("views", 0),
                "comments_count": item.get("commentsCount") or item.get("comments", 0),
                "timestamp": item.get("timestamp") or item.get("takenAt"),
            }
        except Exception as e:
            print(f"[Apify] Error normalizing reel: {e}")
            return None
    
    def _normalize_post(self, item: Dict) -> Optional[Dict]:
        """Normalize post scraper output to standard format."""
        try:
            # Extract caption
            caption = (
                item.get("caption") or 
                item.get("description") or
                item.get("text") or
                ""
            )
            
            # Extract hashtags
            hashtags = item.get("hashtags", [])
            if not hashtags and caption:
                import re
                hashtags = re.findall(r'#(\w+)', caption)
            
            return {
                "type": "post",
                "url": item.get("url") or item.get("inputUrl") or "",
                "caption": caption,
                "hashtags": hashtags,
                "creator": (
                    item.get("ownerUsername") or 
                    item.get("owner", {}).get("username") or
                    ""
                ),
                "likes_count": item.get("likesCount") or item.get("likes", 0),
                "comments_count": item.get("commentsCount") or item.get("comments", 0),
                "timestamp": item.get("timestamp") or item.get("takenAt"),
                "location": item.get("locationName") or item.get("location", {}).get("name"),
            }
        except Exception as e:
            print(f"[Apify] Error normalizing post: {e}")
            return None


def extract_reel_urls_from_export(parsed_data: Dict) -> List[str]:
    """
    Extract content URLs from parsed Instagram export data.
    
    Args:
        parsed_data: The parsed Instagram export with likes, saved, etc.
        
    Returns:
        List of unique content URLs (reels and posts)
    """
    urls = set()
    
    # Extract from likes
    for item in parsed_data.get("likes", []):
        url = item.get("url", "")
        if "/reel/" in url or "/p/" in url:
            urls.add(url)
    
    # Extract from saved
    for item in parsed_data.get("saved", []):
        url = item.get("url", "")
        if "/reel/" in url or "/p/" in url:
            urls.add(url)
    
    return list(urls)


# Keep old name for backward compatibility
class ReelAnalyzer(InstagramScraper):
    """Backward compatibility alias for InstagramScraper."""
    
    def analyze_reels(self, urls: List[str], max_reels: int = MAX_ITEMS_PER_USER) -> List[Dict]:
        """Backward compatible method name."""
        return self.scrape_content(urls, max_reels)


async def analyze_user_content(parsed_data: Dict, max_items: int = MAX_ITEMS_PER_USER) -> Dict:
    """
    Analyze a user's Instagram content by scraping posts/reels.
    
    Args:
        parsed_data: Parsed Instagram export data
        max_items: Maximum items to scrape
        
    Returns:
        Dict with original data plus scraped content
    """
    # Extract content URLs
    urls = extract_reel_urls_from_export(parsed_data)
    print(f"[Content Analysis] Found {len(urls)} content URLs")
    
    if not urls:
        return {
            **parsed_data,
            "reel_content": [],
            "content_analysis": None
        }
    
    try:
        # Scrape content with Apify
        scraper = InstagramScraper()
        scraped_content = scraper.scrape_content(urls, max_items)
        
        return {
            **parsed_data,
            "reel_content": scraped_content,
        }
    except Exception as e:
        print(f"[Content Analysis] Error: {e}")
        return {
            **parsed_data,
            "reel_content": [],
            "content_analysis_error": str(e)
        }


# Synchronous wrapper for non-async contexts
def analyze_user_content_sync(parsed_data: Dict, max_items: int = MAX_ITEMS_PER_USER) -> Dict:
    """Synchronous version of analyze_user_content."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(analyze_user_content(parsed_data, max_items))
