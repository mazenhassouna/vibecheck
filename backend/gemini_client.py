"""
Gemini API Client for Enhanced Compatibility Analysis

Uses Google Gemini to:
1. Categorize accounts into themes
2. Generate conversation starters
3. Provide deeper semantic analysis
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class GeminiClient:
    """
    Client for Google Gemini API (AI Studio).
    Handles theme extraction and conversation generation.
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL = "gemini-2.0-flash"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
    
    def _make_request(self, prompt: str, max_tokens: int = 1024) -> str:
        """Make a request to the Gemini API."""
        url = f"{self.BASE_URL}/{self.MODEL}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            return ""
            
        except requests.exceptions.RequestException as e:
            print(f"Gemini API error: {e}")
            return ""
    
    def categorize_accounts(self, accounts: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of Instagram accounts into themes.
        
        Args:
            accounts: List of Instagram usernames
            
        Returns:
            Dictionary mapping categories to accounts
        """
        if not accounts:
            return {}
        
        # Limit to first 50 accounts for API efficiency
        sample_accounts = accounts[:50]
        
        prompt = f"""Categorize these Instagram accounts into broad interest categories.
Return ONLY a valid JSON object with category names as keys and arrays of usernames as values.

Categories to use: travel, food, fitness, fashion, photography, music, art, tech, nature, sports, comedy, lifestyle, education, gaming, other

Accounts: {json.dumps(sample_accounts)}

Example output format:
{{"travel": ["natgeo", "beautiful_destinations"], "food": ["foodnetwork"]}}

Return ONLY the JSON, no other text:"""

        response = self._make_request(prompt)
        
        try:
            # Clean response and parse JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {"uncategorized": sample_accounts}
    
    def generate_conversation_starters(
        self,
        shared_interests: List[Dict],
        shared_following: List[str],
        shared_topics: List[str]
    ) -> List[str]:
        """
        Generate natural conversation starters based on shared interests.
        
        Args:
            shared_interests: List of shared interest objects
            shared_following: List of shared account usernames
            shared_topics: List of shared topic names
            
        Returns:
            List of conversation starter suggestions
        """
        prompt = f"""Generate 5 natural, friendly conversation starters for two people who just discovered they have these things in common on Instagram:

Shared accounts they follow: {json.dumps(shared_following[:10])}
Shared interests/topics: {json.dumps(shared_topics[:10])}

Rules:
1. Be casual and natural, like how young adults actually talk
2. Reference specific shared interests when possible
3. Don't be cringey or overly enthusiastic
4. Vary the style (questions, observations, suggestions)
5. Keep each one under 100 characters

Return ONLY a JSON array of 5 strings, no other text:"""

        response = self._make_request(prompt)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            starters = json.loads(response.strip())
            if isinstance(starters, list):
                return starters[:5]
        except json.JSONDecodeError:
            pass
        
        # Fallback conversation starters
        return self._generate_fallback_starters(shared_following, shared_topics)
    
    def _generate_fallback_starters(
        self,
        shared_following: List[str],
        shared_topics: List[str]
    ) -> List[str]:
        """Generate fallback conversation starters without API."""
        starters = []
        
        if shared_following:
            starters.append(f"I noticed we both follow @{shared_following[0]}! How'd you find them?")
        
        if shared_topics:
            topic = shared_topics[0]
            starters.append(f"So you're into {topic} too? What got you interested?")
        
        if len(shared_following) > 1:
            starters.append(f"We follow a lot of the same accounts - any favorites?")
        
        if len(shared_topics) > 1:
            starters.append(f"We have similar interests! What's something you're really into lately?")
        
        starters.append("Your Instagram taste is pretty similar to mine - good vibes!")
        
        return starters[:5]
    
    def enhance_compatibility_result(
        self,
        basic_result: Dict,
        person_a_data: Dict,
        person_b_data: Dict
    ) -> Dict:
        """
        Enhance a basic compatibility result with Gemini-powered insights.
        
        Args:
            basic_result: The basic compatibility analysis result
            person_a_data: Parsed Instagram data for person A
            person_b_data: Parsed Instagram data for person B
            
        Returns:
            Enhanced result with conversation starters and categorized interests
        """
        enhanced = basic_result.copy()
        
        # Extract shared data
        shared_following = [
            item["value"] for item in basic_result.get("shared_interests", [])
            if item["type"] == "following"
        ]
        shared_topics = [
            item["value"] for item in basic_result.get("shared_interests", [])
            if item["type"] == "topic"
        ]
        
        # Generate conversation starters
        try:
            enhanced["conversation_starters"] = self.generate_conversation_starters(
                basic_result.get("shared_interests", []),
                shared_following,
                shared_topics
            )
        except Exception as e:
            print(f"Error generating conversation starters: {e}")
            enhanced["conversation_starters"] = self._generate_fallback_starters(
                shared_following, shared_topics
            )
        
        # Categorize shared following for better display
        if shared_following:
            try:
                enhanced["categorized_interests"] = self.categorize_accounts(shared_following)
            except Exception as e:
                print(f"Error categorizing accounts: {e}")
                enhanced["categorized_interests"] = {}
        
        return enhanced
    
    def generate_compatibility_summary(self, result: Dict) -> str:
        """
        Generate a natural language summary of the compatibility result.
        
        Args:
            result: The compatibility analysis result
            
        Returns:
            Human-readable summary string
        """
        score = result.get("score", 0)
        label = result.get("label", {})
        shared = result.get("shared_interests", [])
        
        prompt = f"""Write a brief, friendly 2-3 sentence summary of this Instagram compatibility result:

Score: {score}% ({label.get('text', 'Unknown')})
Number of shared interests: {len(shared)}
Top shared interests: {json.dumps([s['description'] for s in shared[:5]])}

Rules:
1. Be positive but honest
2. Mention specific shared interests if available
3. Keep it casual and friendly
4. No emojis
5. Under 200 characters total

Return ONLY the summary text, no quotes or formatting:"""

        response = self._make_request(prompt, max_tokens=256)
        
        if response:
            return response.strip().strip('"')
        
        # Fallback summary
        if score >= 70:
            return f"You two have a lot in common! With {len(shared)} shared interests, you'll have plenty to talk about."
        elif score >= 50:
            return f"You share some common ground with {len(shared)} overlapping interests. A good foundation for connection."
        else:
            return f"You have different vibes, but that's not a bad thing! You might introduce each other to new things."


# Convenience function for creating client
def create_gemini_client(api_key: Optional[str] = None) -> Optional[GeminiClient]:
    """Create a Gemini client if API key is available."""
    try:
        return GeminiClient(api_key)
    except ValueError:
        return None
