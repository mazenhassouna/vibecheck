"""LLM-powered interest analysis using Google Gemini."""

import json
import asyncio
import logging
from typing import Any
import google.generativeai as genai
from config import config

# Set up logging
logger = logging.getLogger(__name__)

# Configure Gemini
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    logger.info("Gemini API configured")
else:
    logger.warning("GEMINI_API_KEY not set")


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    logger.debug(f"Attempting to extract JSON from response ({len(text)} chars)")
    
    # Try direct JSON parse first
    try:
        result = json.loads(text)
        logger.debug("Direct JSON parse successful")
        return result
    except json.JSONDecodeError:
        logger.debug("Direct JSON parse failed, trying other methods")
    
    # Try to extract from markdown code blocks
    import re
    
    # Pattern for ```json ... ``` or ``` ... ```
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                result = json.loads(match.group(1))
                logger.debug("Extracted JSON from code block")
                return result
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON object in the text
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(text[start:end + 1])
            logger.debug("Extracted JSON from text substring")
            return result
        except json.JSONDecodeError:
            pass
    
    logger.error(f"Could not extract JSON. Response preview: {text[:500]}...")
    raise json.JSONDecodeError("Could not extract JSON from response", text, 0)


# Vibe score tiers
VIBE_TIERS = {
    (90, 100): {"label": "🔥 Soulmates", "description": "Practically the same person"},
    (75, 89): {"label": "💜 Best Friends Energy", "description": "Strong alignment across interests"},
    (60, 74): {"label": "🤝 Solid Match", "description": "Clear common ground"},
    (45, 59): {"label": "🌱 Some Overlap", "description": "A few shared interests"},
    (30, 44): {"label": "🔍 Room to Explore", "description": "Minimal overlap, could discover new things"},
    (0, 29): {"label": "🌍 Different Worlds", "description": "Very different interests"},
}


def get_vibe_tier(score: int) -> dict[str, str]:
    """Get the vibe tier label and description for a score."""
    for (low, high), tier_info in VIBE_TIERS.items():
        if low <= score <= high:
            return tier_info
    return VIBE_TIERS[(0, 29)]


class InterestAnalyzer:
    """Two-stage LLM analyzer for interest extraction and comparison."""
    
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        self.model = genai.GenerativeModel(
            config.LLM_MODEL,
            generation_config=genai.GenerationConfig(
                temperature=config.LLM_TEMPERATURE,
            )
        )
    
    async def analyze_user_interests(
        self,
        profiles: list[dict[str, Any]],
        reels: list[dict[str, Any]],
        comments: list[dict[str, Any]],
        user_label: str = "User"
    ) -> dict[str, Any]:
        """
        Stage 1: Analyze a user's data to extract weighted interest taxonomy.
        
        Args:
            profiles: List of scraped profile data (accounts they follow)
            reels: List of scraped reel data (liked/saved content)
            comments: List of user's comments
            user_label: Label for the user (e.g., "User A")
            
        Returns:
            Structured interest taxonomy with weights
        """
        logger.info(f"[Stage 1] Analyzing {user_label} interests")
        logger.info(f"  - Profiles: {len(profiles)}")
        logger.info(f"  - Reels: {len(reels)}")
        logger.info(f"  - Comments: {len(comments)}")
        
        # Prepare the data summary for the LLM
        data_summary = self._prepare_user_data_summary(profiles, reels, comments)
        logger.debug(f"Data summary prepared for {user_label}")
        
        prompt = f"""Analyze this Instagram user's data and create a weighted interest taxonomy.

## {user_label}'s Instagram Data:

### Accounts They Follow (filtered to 5000+ followers):
{data_summary['following_summary']}

### Content They've Engaged With (likes, saves):
{data_summary['content_summary']}

### Comments They've Made:
{data_summary['comments_summary']}

## Instructions:
1. Identify specific interests (entities like artists, athletes, shows, brands)
2. Categorize each interest hierarchically (e.g., "Music > Hip-Hop > Artists")
3. Assign a weight from 1-10 based on engagement intensity:
   - 10: Obsessed (multiple signals: follows + likes + saves + comments)
   - 7-9: Very interested (strong engagement, multiple interactions)
   - 4-6: Interested (follows or occasional engagement)
   - 1-3: Mild interest (single weak signal)
4. Provide concrete evidence for each interest

## Output Format (JSON):
{{
    "interests": [
        {{
            "entity": "Travis Scott",
            "category": "Music > Hip-Hop > Artists",
            "weight": 9,
            "evidence": [
                "Follows @travisscott (verified, 50M followers)",
                "Liked 12 reels featuring his music",
                "Saved 3 Astroworld-related posts"
            ]
        }}
    ],
    "top_categories": [
        {{
            "category": "Music",
            "total_weight": 25,
            "subcategories": ["Hip-Hop", "Pop"]
        }}
    ],
    "summary": "Brief 1-2 sentence summary of this user's main interests"
}}

Be thorough but focus on the strongest signals. Limit to top 20 interests."""

        # Run the LLM call
        logger.info(f"[Stage 1] Calling Gemini for {user_label}...")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        logger.info(f"[Stage 1] Gemini response received for {user_label} ({len(response.text)} chars)")
        
        try:
            result = extract_json_from_response(response.text)
            result["user_label"] = user_label
            logger.info(f"[Stage 1] {user_label} analysis complete: {len(result.get('interests', []))} interests found")
            logger.debug(f"[Stage 1] {user_label} summary: {result.get('summary', 'N/A')}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[Stage 1] Failed to parse {user_label} response: {e}")
            # If JSON parsing fails, return a minimal structure
            return {
                "user_label": user_label,
                "interests": [],
                "top_categories": [],
                "summary": "Unable to analyze interests",
                "error": "Failed to parse LLM response"
            }
    
    async def compare_users(
        self,
        user_a_profile: dict[str, Any],
        user_b_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Stage 2: Compare two user profiles and generate vibe score.
        
        Args:
            user_a_profile: Interest taxonomy from Stage 1 for User A
            user_b_profile: Interest taxonomy from Stage 1 for User B
            
        Returns:
            Comparison result with score, matches, and narrative
        """
        logger.info("[Stage 2] Comparing user profiles")
        logger.info(f"  - User A interests: {len(user_a_profile.get('interests', []))}")
        logger.info(f"  - User B interests: {len(user_b_profile.get('interests', []))}")
        
        prompt = f"""Compare these two Instagram users' interest profiles and calculate their vibe compatibility.

## User A's Interests:
{json.dumps(user_a_profile.get('interests', []), indent=2)}

Summary: {user_a_profile.get('summary', 'N/A')}

## User B's Interests:
{json.dumps(user_b_profile.get('interests', []), indent=2)}

Summary: {user_b_profile.get('summary', 'N/A')}

## Scoring Rules:
1. **Exact Entity Matches** (same artist/team/show): High value
   - Weight contribution = min(weight_A, weight_B) * 2
2. **Category Matches** (same category, different entities): Medium value  
   - Weight contribution = min(weight_A, weight_B) * 1
3. **Broad Category Overlap** (e.g., both into Sports): Low value
   - Weight contribution = 0.5 per overlapping category

## Calculate:
- Find all exact entity matches
- Find category-level matches (e.g., both into NBA but different teams)
- Find broad category overlaps
- Calculate raw score (sum of weighted matches)
- Normalize to 0-100 scale

## Output Format (JSON):
{{
    "vibe_score": 78,
    "exact_matches": [
        {{
            "entity": "Travis Scott",
            "user_a_weight": 9,
            "user_b_weight": 7,
            "contribution": 14
        }}
    ],
    "category_matches": [
        {{
            "category": "Sports > Basketball",
            "user_a_entities": ["Lakers", "LeBron"],
            "user_b_entities": ["Warriors", "Steph Curry"],
            "note": "Same sport, rival teams - great debate material!",
            "contribution": 6
        }}
    ],
    "broad_overlaps": [
        {{
            "category": "Music",
            "note": "Both are music lovers"
        }}
    ],
    "unique_to_a": ["Photography", "Hiking"],
    "unique_to_b": ["Gaming", "Anime"],
    "narrative": "A 2-3 sentence engaging summary of what these users have in common and what makes their connection interesting. Be specific about shared interests."
}}

Be accurate and specific. The narrative should feel personal and insightful."""

        # Run the LLM call
        logger.info("[Stage 2] Calling Gemini for comparison...")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        logger.info(f"[Stage 2] Gemini response received ({len(response.text)} chars)")
        
        try:
            result = extract_json_from_response(response.text)
            # Add tier information
            score = result.get("vibe_score", 0)
            tier = get_vibe_tier(score)
            result["tier"] = tier["label"]
            result["tier_description"] = tier["description"]
            logger.info(f"[Stage 2] Comparison complete - Vibe Score: {score}, Tier: {tier['label']}")
            logger.info(f"[Stage 2] Exact matches: {len(result.get('exact_matches', []))}")
            logger.info(f"[Stage 2] Category matches: {len(result.get('category_matches', []))}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[Stage 2] Failed to parse comparison response: {e}")
            return {
                "vibe_score": 0,
                "tier": "❓ Unknown",
                "tier_description": "Could not analyze",
                "exact_matches": [],
                "category_matches": [],
                "broad_overlaps": [],
                "unique_to_a": [],
                "unique_to_b": [],
                "narrative": "Unable to compare users due to analysis error.",
                "error": "Failed to parse LLM response"
            }
    
    def _prepare_user_data_summary(
        self,
        profiles: list[dict[str, Any]],
        reels: list[dict[str, Any]],
        comments: list[dict[str, Any]]
    ) -> dict[str, str]:
        """Prepare a text summary of user data for the LLM."""
        
        # Summarize following
        following_lines = []
        for p in profiles[:50]:  # Limit to 50 for context length
            username = p.get("username", "unknown")
            full_name = p.get("fullName", "")
            bio = p.get("biography", "")[:100]  # Truncate bio
            followers = p.get("followersCount", 0)
            category = p.get("businessCategoryName", "")
            verified = "✓" if p.get("verified") else ""
            
            line = f"- @{username} {verified} ({followers:,} followers)"
            if category:
                line += f" [{category}]"
            if full_name:
                line += f" - {full_name}"
            if bio:
                line += f": {bio}..."
            following_lines.append(line)
        
        # Summarize reels/content
        content_lines = []
        for r in reels[:30]:  # Limit to 30
            caption = r.get("caption", "")[:150]
            hashtags = r.get("hashtags", [])[:5]
            transcript = r.get("transcript", "")[:100]
            owner = r.get("ownerUsername", "unknown")
            
            line = f"- Reel by @{owner}"
            if hashtags:
                line += f" #{' #'.join(hashtags)}"
            if caption:
                line += f": {caption}..."
            if transcript:
                line += f" [Transcript: {transcript}...]"
            content_lines.append(line)
        
        # Summarize comments
        comment_lines = []
        for c in comments[:20]:  # Limit to 20
            text = c.get("text", "")[:100]
            post_owner = c.get("post_owner", "unknown")
            if text:
                comment_lines.append(f"- On @{post_owner}'s post: \"{text}\"")
        
        return {
            "following_summary": "\n".join(following_lines) if following_lines else "No following data available",
            "content_summary": "\n".join(content_lines) if content_lines else "No content engagement data available",
            "comments_summary": "\n".join(comment_lines) if comment_lines else "No comments available",
        }


async def analyze_and_compare(
    user_a_data: dict[str, Any],
    user_b_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Complete two-stage analysis pipeline.
    
    Args:
        user_a_data: Dict with 'profiles', 'reels', 'comments' for User A
        user_b_data: Dict with 'profiles', 'reels', 'comments' for User B
        
    Returns:
        Complete comparison result
    """
    analyzer = InterestAnalyzer()
    
    # Stage 1: Analyze both users in parallel
    user_a_task = analyzer.analyze_user_interests(
        profiles=user_a_data.get("profiles", []),
        reels=user_a_data.get("reels", []),
        comments=user_a_data.get("comments", []),
        user_label="User A"
    )
    
    user_b_task = analyzer.analyze_user_interests(
        profiles=user_b_data.get("profiles", []),
        reels=user_b_data.get("reels", []),
        comments=user_b_data.get("comments", []),
        user_label="User B"
    )
    
    user_a_profile, user_b_profile = await asyncio.gather(user_a_task, user_b_task)
    
    # Stage 2: Compare users
    comparison = await analyzer.compare_users(user_a_profile, user_b_profile)
    
    # Combine all results
    return {
        "user_a_profile": user_a_profile,
        "user_b_profile": user_b_profile,
        "comparison": comparison,
    }
