"""Instagram scraper using Apify."""

import asyncio
from typing import Any
import apify_client as apify_lib
from config import config


class InstagramScraper:
    """Client for scraping Instagram data using Apify actors."""
    
    def __init__(self):
        if not config.APIFY_API_KEY:
            raise ValueError("APIFY_API_KEY is required")
        self.client = apify_lib.ApifyClient(config.APIFY_API_KEY)
    
    async def scrape_profiles(
        self, 
        usernames: list[str],
        max_profiles: int = 100
    ) -> list[dict[str, Any]]:
        """
        Scrape Instagram profile data for given usernames.
        
        Args:
            usernames: List of Instagram usernames to scrape
            max_profiles: Maximum number of profiles to scrape
            
        Returns:
            List of profile data dictionaries
        """
        if not usernames:
            return []
        
        # Limit the number of profiles
        usernames = usernames[:max_profiles]
        
        # Prepare input for the actor
        run_input = {
            "usernames": usernames,
        }
        
        # Run the actor synchronously (wrapped in async)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self._run_profile_scraper(run_input)
        )
        
        return result
    
    def _run_profile_scraper(self, run_input: dict[str, Any]) -> list[dict[str, Any]]:
        """Run the profile scraper actor synchronously."""
        try:
            # Run the actor and wait for it to finish
            run = self.client.actor(config.APIFY_PROFILE_SCRAPER).call(run_input=run_input)
            
            # Fetch results from the dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            return items
        except Exception as e:
            print(f"Error scraping profiles: {e}")
            return []
    
    async def scrape_reels(
        self,
        reel_urls: list[str],
        max_reels: int = 50
    ) -> list[dict[str, Any]]:
        """
        Scrape Instagram reel data for given reel URLs.
        
        Args:
            reel_urls: List of Instagram reel URLs to scrape
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of reel data dictionaries
        """
        if not reel_urls:
            return []
        
        # Limit the number of reels
        reel_urls = reel_urls[:max_reels]
        
        # Prepare input for the actor
        run_input = {
            "directUrls": reel_urls,
        }
        
        # Run the actor synchronously (wrapped in async)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._run_reel_scraper(run_input)
        )
        
        return result
    
    def _run_reel_scraper(self, run_input: dict[str, Any]) -> list[dict[str, Any]]:
        """Run the reel scraper actor synchronously."""
        try:
            # Run the actor and wait for it to finish
            run = self.client.actor(config.APIFY_REEL_SCRAPER).call(run_input=run_input)
            
            # Fetch results from the dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            return items
        except Exception as e:
            print(f"Error scraping reels: {e}")
            return []
    
    def filter_by_followers(
        self, 
        profiles: list[dict[str, Any]], 
        min_followers: int = None
    ) -> list[dict[str, Any]]:
        """
        Filter profiles by minimum follower count.
        
        Args:
            profiles: List of profile data
            min_followers: Minimum follower count (default from config)
            
        Returns:
            Filtered list of profiles
        """
        if min_followers is None:
            min_followers = config.MIN_FOLLOWER_COUNT
        
        filtered = []
        for profile in profiles:
            followers = profile.get("followersCount", 0)
            if followers >= min_followers:
                filtered.append(profile)
        
        return filtered


class EnrichedUserData:
    """Container for enriched user data from scraping."""
    
    def __init__(self):
        self.profiles: list[dict[str, Any]] = []
        self.reels: list[dict[str, Any]] = []
        self.filtered_profiles: list[dict[str, Any]] = []
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "profiles": self.profiles,
            "reels": self.reels,
            "filtered_profiles": self.filtered_profiles,
            "stats": {
                "total_profiles": len(self.profiles),
                "filtered_profiles": len(self.filtered_profiles),
                "total_reels": len(self.reels),
            }
        }


async def enrich_user_data(
    following: list[str],
    liked_post_urls: list[str],
    saved_post_urls: list[str],
    max_profiles: int = 100,
    max_reels: int = 50
) -> EnrichedUserData:
    """
    Enrich user data by scraping Instagram profiles and reels.
    
    Args:
        following: List of usernames the user follows
        liked_post_urls: URLs of liked posts/reels
        saved_post_urls: URLs of saved posts/reels
        max_profiles: Maximum profiles to scrape
        max_reels: Maximum reels to scrape
        
    Returns:
        EnrichedUserData with scraped and filtered data
    """
    scraper = InstagramScraper()
    enriched = EnrichedUserData()
    
    # Combine liked and saved URLs, filter for reels
    all_urls = liked_post_urls + saved_post_urls
    reel_urls = [url for url in all_urls if "reel" in url.lower() or "/p/" in url]
    
    # Scrape profiles and reels in parallel
    profiles_task = scraper.scrape_profiles(following, max_profiles)
    reels_task = scraper.scrape_reels(reel_urls, max_reels)
    
    profiles, reels = await asyncio.gather(profiles_task, reels_task)
    
    enriched.profiles = profiles
    enriched.reels = reels
    enriched.filtered_profiles = scraper.filter_by_followers(profiles)
    
    return enriched


def extract_profile_info(profile: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant info from a scraped profile."""
    return {
        "username": profile.get("username", ""),
        "fullName": profile.get("fullName", ""),
        "biography": profile.get("biography", ""),
        "followersCount": profile.get("followersCount", 0),
        "isVerified": profile.get("verified", False),
        "isBusinessAccount": profile.get("isBusinessAccount", False),
        "businessCategory": profile.get("businessCategoryName", ""),
        "externalUrl": profile.get("externalUrl", ""),
    }


def extract_reel_info(reel: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant info from a scraped reel."""
    return {
        "id": reel.get("id", ""),
        "caption": reel.get("caption", ""),
        "hashtags": reel.get("hashtags", []),
        "mentions": reel.get("mentions", []),
        "transcript": reel.get("transcript", ""),
        "ownerUsername": reel.get("ownerUsername", ""),
        "likesCount": reel.get("likesCount", 0),
        "commentsCount": reel.get("commentsCount", 0),
        "viewsCount": reel.get("videoViewCount", 0),
        "musicInfo": reel.get("musicInfo", {}),
    }
