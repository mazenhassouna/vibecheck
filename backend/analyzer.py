"""
Compatibility Analyzer

Handles feature extraction and scoring algorithm with configurable weights and bonuses.
Uses Jaccard similarity for category comparisons.
Derives interest categories from account names to show meaningful shared interests.

SCORING PRINCIPLE: Identical data should ALWAYS yield 100% compatibility.
"""

from typing import Dict, List, Any, Set, Tuple
from scoring_config import SCORING_CONFIG, INTEREST_CATEGORIES, get_score_label


class CompatibilityAnalyzer:
    """
    Analyzes compatibility between two Instagram profiles.
    Uses configurable weights and Jaccard similarity.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or SCORING_CONFIG
        self.interest_categories = INTEREST_CATEGORIES
    
    def analyze(self, person_a: Dict, person_b: Dict) -> Dict[str, Any]:
        """
        Calculate compatibility between two people.
        
        Args:
            person_a: Parsed Instagram data for person A
            person_b: Parsed Instagram data for person B
            
        Returns:
            Compatibility result with score, breakdown, and shared interests
        """
        weights = self.config["weights"]
        
        # Calculate individual category scores
        scores = {
            "likes": self._score_likes(person_a.get("likes", []), person_b.get("likes", [])),
            "saved": self._score_saved(person_a.get("saved", []), person_b.get("saved", [])),
            "following": self._score_following(person_a.get("following", []), person_b.get("following", [])),
            "comments": self._score_comments(person_a.get("comments", []), person_b.get("comments", [])),
        }
        
        # Calculate weighted base score
        base_score = sum(weights[cat] * scores[cat]["score"] for cat in weights)
        
        # Derive interest categories from all accounts
        interests_a = self._derive_interests(person_a)
        interests_b = self._derive_interests(person_b)
        shared_interest_categories = interests_a & interests_b
        
        # Calculate bonuses
        bonus_result = self._calculate_bonuses(person_a, person_b, scores, shared_interest_categories)
        bonus_points = min(bonus_result["total"], self.config["max_bonus"])
        
        # Final score (rounded to whole number, capped at 100)
        final_score = min(round(base_score + bonus_points), 100)
        
        # Get label
        label = get_score_label(final_score)
        
        # Collect shared interests (themes, not just account names)
        shared_interests = self._collect_shared_interests(scores, shared_interest_categories)
        
        return {
            "score": final_score,
            "label": label,
            "breakdown": {
                cat: {
                    "score": scores[cat]["score"],
                    "weight": weights[cat],
                    "weighted_contribution": round(weights[cat] * scores[cat]["score"], 1),
                }
                for cat in scores
            },
            "bonus_points": bonus_points,
            "bonus_details": bonus_result["details"],
            "shared_interests": shared_interests,
            "base_score": round(base_score, 1),
        }
    
    def _derive_interests(self, person_data: Dict) -> Set[str]:
        """
        Derive interest categories from all account names.
        Looks at following, likes, and saved to build interest profile.
        """
        all_accounts = set()
        
        # Collect all account names
        for item in person_data.get("following", []):
            if "username" in item:
                all_accounts.add(item["username"].lower())
        
        for item in person_data.get("likes", []):
            if "account" in item:
                all_accounts.add(item["account"].lower())
        
        for item in person_data.get("saved", []):
            if "account" in item:
                all_accounts.add(item["account"].lower())
        
        # Match accounts to interest categories
        matched_interests = set()
        for account in all_accounts:
            for category, keywords in self.interest_categories.items():
                for keyword in keywords:
                    if keyword.lower() in account:
                        matched_interests.add(category)
                        break
        
        return matched_interests
    
    def _jaccard_similarity(self, set_a: Set, set_b: Set) -> float:
        """
        Calculate Jaccard similarity between two sets.
        
        IMPORTANT: If both sets are empty OR identical, this returns 1.0 (100% match).
        """
        if not set_a and not set_b:
            return 1.0
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = set_a & set_b
        union = set_a | set_b
        
        if not union:
            return 1.0
        
        return len(intersection) / len(union)
    
    def _extract_accounts(self, likes_or_saved: List[Dict]) -> Set[str]:
        """Extract account names from likes or saved data."""
        accounts = set()
        for item in likes_or_saved:
            if "account" in item and item["account"]:
                accounts.add(item["account"].lower().strip())
            elif "username" in item and item["username"]:
                accounts.add(item["username"].lower().strip())
            elif "content" in item and item["content"]:
                accounts.add(item["content"].lower().strip()[:50])
            elif "url" in item and item["url"]:
                accounts.add(item["url"].lower().strip())
        return accounts
    
    def _extract_urls(self, data: List[Dict]) -> Set[str]:
        """Extract URLs from data for exact matching."""
        urls = set()
        for item in data:
            if "url" in item and item["url"]:
                urls.add(item["url"].lower().strip())
        return urls
    
    def _score_likes(self, likes_a: List[Dict], likes_b: List[Dict]) -> Dict:
        """Score likes category using Jaccard similarity."""
        accounts_a = self._extract_accounts(likes_a)
        accounts_b = self._extract_accounts(likes_b)
        
        similarity = self._jaccard_similarity(accounts_a, accounts_b)
        overlap = accounts_a & accounts_b
        
        return {
            "score": round(similarity * 100, 1),
            "overlap_count": len(overlap),
            "overlap_items": list(overlap)[:20],
            "total_a": len(accounts_a),
            "total_b": len(accounts_b),
        }
    
    def _score_saved(self, saved_a: List[Dict], saved_b: List[Dict]) -> Dict:
        """Score saved posts category using Jaccard similarity."""
        accounts_a = self._extract_accounts(saved_a)
        accounts_b = self._extract_accounts(saved_b)
        
        urls_a = self._extract_urls(saved_a)
        urls_b = self._extract_urls(saved_b)
        exact_matches = urls_a & urls_b
        
        similarity = self._jaccard_similarity(accounts_a, accounts_b)
        overlap = accounts_a & accounts_b
        
        return {
            "score": round(similarity * 100, 1),
            "overlap_count": len(overlap),
            "overlap_items": list(overlap)[:20],
            "exact_post_matches": len(exact_matches),
            "total_a": len(accounts_a),
            "total_b": len(accounts_b),
        }
    
    def _score_following(self, following_a: List[Dict], following_b: List[Dict]) -> Dict:
        """Score following category using Jaccard similarity."""
        usernames_a = set(
            item.get("username", "").lower().strip() 
            for item in following_a 
            if item.get("username")
        )
        usernames_b = set(
            item.get("username", "").lower().strip() 
            for item in following_b 
            if item.get("username")
        )
        
        direct_overlap = usernames_a & usernames_b
        jaccard_score = self._jaccard_similarity(usernames_a, usernames_b) * 100
        
        return {
            "score": round(jaccard_score, 1),
            "direct_overlap_count": len(direct_overlap),
            "direct_overlap_items": list(direct_overlap)[:20],
            "total_a": len(usernames_a),
            "total_b": len(usernames_b),
        }
    
    def _score_comments(self, comments_a: List[Dict], comments_b: List[Dict]) -> Dict:
        """Score comments based on engagement style similarity."""
        if not comments_a and not comments_b:
            return {
                "score": 100.0,
                "style_matches": ["Both have no comment history"],
                "style_a": {},
                "style_b": {},
            }
        
        if not comments_a or not comments_b:
            return {
                "score": 50.0,
                "style_matches": [],
                "style_a": self._analyze_comment_style(comments_a) if comments_a else {},
                "style_b": self._analyze_comment_style(comments_b) if comments_b else {},
            }
        
        style_a = self._analyze_comment_style(comments_a)
        style_b = self._analyze_comment_style(comments_b)
        
        matches = []
        total_attributes = 4
        
        if style_a["length_category"] == style_b["length_category"]:
            matches.append(f"Similar comment length ({style_a['length_category']})")
        
        if style_a["emoji_heavy"] == style_b["emoji_heavy"]:
            emoji_desc = "emoji enthusiasts" if style_a["emoji_heavy"] else "minimal emoji users"
            matches.append(f"Both are {emoji_desc}")
        
        if style_a["asks_questions"] == style_b["asks_questions"]:
            q_desc = "curious (ask questions)" if style_a["asks_questions"] else "statement-makers"
            matches.append(f"Both are {q_desc}")
        
        if style_a["engagement_level"] == style_b["engagement_level"]:
            matches.append(f"Similar engagement level ({style_a['engagement_level']})")
        
        score = (len(matches) / total_attributes) * 100
        
        return {
            "score": round(score, 1),
            "style_matches": matches,
            "style_a": style_a,
            "style_b": style_b,
        }
    
    def _analyze_comment_style(self, comments: List[Dict]) -> Dict:
        """Analyze the commenting style of a user."""
        if not comments:
            return {
                "length_category": "unknown",
                "emoji_heavy": False,
                "asks_questions": False,
                "engagement_level": "unknown",
            }
        
        total = len(comments)
        avg_length = sum(c.get("length", 0) for c in comments) / total if total > 0 else 0
        emoji_count = sum(1 for c in comments if c.get("has_emoji", False))
        question_count = sum(1 for c in comments if c.get("has_question", False))
        
        if avg_length < 20:
            length_category = "short"
        elif avg_length < 50:
            length_category = "medium"
        else:
            length_category = "long"
        
        emoji_heavy = (emoji_count / total) > 0.3 if total > 0 else False
        asks_questions = (question_count / total) > 0.2 if total > 0 else False
        
        if total < 50:
            engagement_level = "casual"
        elif total < 200:
            engagement_level = "moderate"
        else:
            engagement_level = "active"
        
        return {
            "length_category": length_category,
            "emoji_heavy": emoji_heavy,
            "asks_questions": asks_questions,
            "engagement_level": engagement_level,
            "total_comments": total,
            "avg_length": round(avg_length, 1),
        }
    
    def _calculate_bonuses(self, person_a: Dict, person_b: Dict, scores: Dict, shared_interest_categories: Set[str]) -> Dict:
        """Calculate bonus points based on special matches."""
        bonuses = self.config["bonuses"]
        details = []
        total = 0
        
        # Bonus for niche account overlap in following
        following_overlap = scores["following"].get("direct_overlap_count", 0)
        if following_overlap >= 3:
            niche_bonus = min(following_overlap - 2, 5) * bonuses["same_niche_account"]
            total += niche_bonus
            details.append({
                "type": "same_niche_account",
                "description": f"Follow {following_overlap} of the same accounts",
                "points": niche_bonus,
            })
        
        # Bonus for exact same saved posts
        exact_saved = scores["saved"].get("exact_post_matches", 0)
        if exact_saved > 0:
            saved_bonus = min(exact_saved, 5) * bonuses["same_exact_saved_post"]
            total += saved_bonus
            details.append({
                "type": "same_exact_saved_post",
                "description": f"Saved {exact_saved} of the exact same posts",
                "points": saved_bonus,
            })
        
        # Bonus for shared interest categories
        if len(shared_interest_categories) >= 2:
            interest_bonus = min(len(shared_interest_categories), 5) * bonuses["same_interest_category"]
            total += interest_bonus
            details.append({
                "type": "same_interest_category",
                "description": f"Share {len(shared_interest_categories)} interest categories",
                "points": interest_bonus,
            })
        
        return {
            "total": total,
            "details": details,
        }
    
    def _collect_shared_interests(self, scores: Dict, shared_interest_categories: Set[str]) -> List[Dict]:
        """
        Collect shared interests focusing on THEMES not just account names.
        Shows interest categories first, then some specific examples.
        """
        shared = []
        
        # PRIMARY: Show shared interest categories (themes)
        for category in sorted(shared_interest_categories):
            emoji_map = {
                "Photography": "📷",
                "Fitness & Gym": "💪",
                "Sports": "⚽",
                "Tech & Coding": "💻",
                "Food & Cooking": "🍳",
                "Travel & Adventure": "✈️",
                "Islam & Religion": "🕌",
                "Anime & Manga": "🎌",
                "Memes & Comedy": "😂",
                "Art & Design": "🎨",
                "Music": "🎵",
                "Gaming": "🎮",
                "Fashion & Style": "👔",
                "Cars & Motors": "🚗",
                "Nature & Animals": "🌿",
                "Self-Improvement": "📈",
            }
            emoji = emoji_map.get(category, "🎯")
            shared.append({
                "type": "interest",
                "value": category,
                "description": f"{emoji} Both into {category}",
            })
        
        # SECONDARY: Show some specific account overlaps as examples
        following_overlap = scores["following"].get("direct_overlap_items", [])[:5]
        if following_overlap:
            shared.append({
                "type": "accounts",
                "value": "following",
                "description": f"📱 Both follow {len(scores['following'].get('direct_overlap_items', []))} of the same accounts",
            })
        
        likes_overlap = scores["likes"].get("overlap_items", [])[:5]
        if likes_overlap:
            shared.append({
                "type": "accounts",
                "value": "likes",
                "description": f"❤️ Both like content from {len(scores['likes'].get('overlap_items', []))} of the same creators",
            })
        
        saved_overlap = scores["saved"].get("overlap_items", [])[:5]
        if saved_overlap:
            shared.append({
                "type": "accounts",
                "value": "saved",
                "description": f"📌 Both saved posts from {len(scores['saved'].get('overlap_items', []))} of the same accounts",
            })
        
        # Comment style matches
        for match in scores["comments"].get("style_matches", [])[:2]:
            shared.append({
                "type": "style",
                "value": match,
                "description": f"💬 {match}",
            })
        
        return shared


# Convenience function
def analyze_compatibility(person_a: Dict, person_b: Dict, config: Dict = None) -> Dict:
    """Analyze compatibility between two Instagram profiles."""
    analyzer = CompatibilityAnalyzer(config)
    return analyzer.analyze(person_a, person_b)
