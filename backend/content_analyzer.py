"""
Content Analyzer using Gemini AI

Analyzes reel captions, transcripts, and hashtags to extract
meaningful themes and interests for compatibility matching.
"""

import os
import json
from typing import List, Dict, Any, Optional
from gemini_client import GeminiClient


class ContentAnalyzer:
    """
    Analyzes Instagram reel content using Gemini AI.
    Extracts themes, interests, and personality traits from content.
    """
    
    # Categories we want to identify
    CATEGORIES = [
        "Fitness & Gym", "Calisthenics", "Running & Cardio", "Yoga & Wellness", "Nutrition & Diet",
        "MMA & Combat Sports", "Soccer/Football", "Basketball", "Cricket", "Tennis", "F1 & Motorsport",
        "Islam & Muslim Life", "Christianity", "Hinduism", "Spirituality",
        "Anime & Manga", "Movies & Cinema", "TV Shows & Series", "K-Pop & K-Drama", "Memes & Comedy",
        "Photography", "Art & Illustration", "Graphic Design", "Music Production", "Content Creation",
        "Tech & Coding", "Gaming", "PC Building",
        "Fashion & Style", "Fragrance & Grooming", "Food & Cooking", "Coffee & Tea",
        "Travel & Adventure", "Nature & Wildlife", "Camping & Survival", "Pets & Animals",
        "Self-Improvement", "Finance & Investing", "Business & Startups", "Education & Learning",
        "Cars & Supercars", "JDM & Tuning", "Motorcycles",
        "Middle Eastern Culture", "South Asian Culture", "African Culture", "Latino Culture",
        "Internet Culture", "Dark Humor", "Mental Health", "Positivity & Quotes"
    ]
    
    def __init__(self):
        self.gemini = GeminiClient()
    
    def analyze_reels(self, reel_content: List[Dict]) -> Dict[str, Any]:
        """
        Analyze a collection of reels to extract user interests and themes.
        
        Args:
            reel_content: List of reel data with captions, transcripts, hashtags
            
        Returns:
            Analysis result with themes, interests, and insights
        """
        if not reel_content:
            return {
                "themes": [],
                "interests": [],
                "personality_traits": [],
                "content_summary": "No reel content available for analysis."
            }
        
        # Prepare content for analysis
        content_text = self._prepare_content_for_analysis(reel_content)
        
        # Use Gemini to analyze
        prompt = self._build_analysis_prompt(content_text)
        
        try:
            response = self.gemini.generate(prompt)
            analysis = self._parse_analysis_response(response)
            return analysis
        except Exception as e:
            print(f"[Content Analyzer] Error: {e}")
            # Fallback to basic analysis
            return self._basic_analysis(reel_content)
    
    def _prepare_content_for_analysis(self, reel_content: List[Dict]) -> str:
        """Prepare reel content as text for Gemini analysis."""
        content_parts = []
        
        for i, reel in enumerate(reel_content[:30], 1):  # Limit to 30 reels
            parts = []
            
            caption = reel.get("caption", "").strip()
            transcript = reel.get("transcript", "").strip()
            hashtags = reel.get("hashtags", [])
            audio = reel.get("audio_name", "").strip()
            creator = reel.get("creator", "").strip()
            
            if caption:
                parts.append(f"Caption: {caption[:500]}")  # Limit caption length
            if transcript:
                parts.append(f"Transcript: {transcript[:500]}")
            if hashtags:
                parts.append(f"Hashtags: #{' #'.join(hashtags[:10])}")
            if audio:
                parts.append(f"Audio: {audio}")
            if creator:
                parts.append(f"Creator: @{creator}")
            
            if parts:
                content_parts.append(f"Reel {i}:\n" + "\n".join(parts))
        
        return "\n\n".join(content_parts)
    
    def _build_analysis_prompt(self, content_text: str) -> str:
        """Build the Gemini prompt for content analysis."""
        categories_str = ", ".join(self.CATEGORIES)
        
        return f"""Analyze this Instagram user's liked/saved reels content and identify their interests, themes, and personality traits.

CONTENT:
{content_text}

AVAILABLE CATEGORIES:
{categories_str}

Respond with a JSON object containing:
1. "themes": List of top 5 themes/categories from the available categories that best match this user's interests (must be from the list above)
2. "interests": List of 3-5 specific interests you can identify (e.g., "Watching MMA fights", "Islamic lectures", "Anime AMVs")
3. "personality_traits": List of 2-3 personality traits you can infer (e.g., "Fitness-oriented", "Spiritually inclined", "Tech enthusiast")
4. "content_summary": A 2-3 sentence summary of what this user seems to enjoy

Return ONLY valid JSON, no other text."""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini's response into structured data."""
        try:
            # Clean up the response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            data = json.loads(response)
            
            return {
                "themes": data.get("themes", [])[:5],
                "interests": data.get("interests", [])[:5],
                "personality_traits": data.get("personality_traits", [])[:3],
                "content_summary": data.get("content_summary", ""),
            }
        except json.JSONDecodeError:
            print(f"[Content Analyzer] Failed to parse JSON response")
            return self._extract_themes_manually(response)
    
    def _extract_themes_manually(self, text: str) -> Dict[str, Any]:
        """Manually extract themes if JSON parsing fails."""
        themes = []
        text_lower = text.lower()
        
        for category in self.CATEGORIES:
            if category.lower() in text_lower:
                themes.append(category)
        
        return {
            "themes": themes[:5],
            "interests": [],
            "personality_traits": [],
            "content_summary": "Analysis completed with limited extraction.",
        }
    
    def _basic_analysis(self, reel_content: List[Dict]) -> Dict[str, Any]:
        """Fallback basic analysis using hashtags and keywords."""
        all_hashtags = []
        all_captions = []
        
        for reel in reel_content:
            all_hashtags.extend(reel.get("hashtags", []))
            caption = reel.get("caption", "")
            if caption:
                all_captions.append(caption)
        
        # Count hashtag frequency
        hashtag_counts = {}
        for tag in all_hashtags:
            tag_lower = tag.lower()
            hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
        
        # Match to categories based on hashtags
        themes = []
        combined_text = " ".join([h.lower() for h in all_hashtags] + [c.lower() for c in all_captions])
        
        category_keywords = {
            "Fitness & Gym": ["gym", "fitness", "workout", "gains", "lift", "muscle"],
            "Anime & Manga": ["anime", "manga", "otaku", "weeb", "naruto", "onepiece"],
            "Islam & Muslim Life": ["islam", "muslim", "quran", "deen", "halal", "ramadan"],
            "Memes & Comedy": ["meme", "funny", "comedy", "humor", "lol"],
            "Gaming": ["gaming", "gamer", "game", "playstation", "xbox", "pc"],
            "Tech & Coding": ["tech", "code", "programming", "developer", "software"],
            "Travel & Adventure": ["travel", "adventure", "explore", "wanderlust"],
            "Self-Improvement": ["motivation", "mindset", "success", "grind", "hustle"],
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    if category not in themes:
                        themes.append(category)
                    break
        
        return {
            "themes": themes[:5],
            "interests": list(hashtag_counts.keys())[:5],
            "personality_traits": [],
            "content_summary": f"User engages with content related to: {', '.join(themes[:3]) if themes else 'various topics'}",
        }
    
    def compare_users(self, analysis_a: Dict, analysis_b: Dict) -> Dict[str, Any]:
        """
        Compare two users based on their content analysis.
        
        Args:
            analysis_a: Content analysis for user A
            analysis_b: Content analysis for user B
            
        Returns:
            Comparison result with shared themes and compatibility insights
        """
        themes_a = set(analysis_a.get("themes", []))
        themes_b = set(analysis_b.get("themes", []))
        
        shared_themes = list(themes_a & themes_b)
        unique_a = list(themes_a - themes_b)
        unique_b = list(themes_b - themes_a)
        
        # Calculate theme-based similarity
        if themes_a or themes_b:
            jaccard = len(shared_themes) / len(themes_a | themes_b)
        else:
            jaccard = 0
        
        # Find shared interests (more specific than themes)
        interests_a = set(analysis_a.get("interests", []))
        interests_b = set(analysis_b.get("interests", []))
        shared_interests = list(interests_a & interests_b)
        
        return {
            "shared_themes": shared_themes,
            "shared_interests": shared_interests,
            "unique_to_a": unique_a,
            "unique_to_b": unique_b,
            "theme_similarity": round(jaccard * 100, 1),
            "personality_a": analysis_a.get("personality_traits", []),
            "personality_b": analysis_b.get("personality_traits", []),
        }


def analyze_user_themes(reel_content: List[Dict]) -> Dict[str, Any]:
    """Convenience function to analyze a user's content."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_reels(reel_content)


def compare_user_content(analysis_a: Dict, analysis_b: Dict) -> Dict[str, Any]:
    """Convenience function to compare two users' content."""
    analyzer = ContentAnalyzer()
    return analyzer.compare_users(analysis_a, analysis_b)
