"""
Compatibility Analyzer

Theme-based scoring that focuses on shared interests rather than exact account matches.
More relaxed similarity - if both engage with the same theme, that counts!
Exact matches within themes provide bonus points.

SCORING PRINCIPLE: Identical data should ALWAYS yield 100% compatibility.
"""

from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from scoring_config import SCORING_CONFIG, INTEREST_CATEGORIES, get_score_label


class CompatibilityAnalyzer:
    """
    Analyzes compatibility between two Instagram profiles.
    Uses theme-based scoring for more meaningful results.
    """
    
    # Minimum accounts needed in a theme for it to count
    THEME_THRESHOLD = 2
    # Maximum themes to display
    MAX_THEMES = 5
    
    def __init__(self, config: Dict = None):
        self.config = config or SCORING_CONFIG
        self.interest_categories = INTEREST_CATEGORIES
    
    def analyze(self, person_a: Dict, person_b: Dict) -> Dict[str, Any]:
        """
        Calculate compatibility between two people using theme-based scoring.
        """
        weights = self.config["weights"]
        
        # Extract all accounts for each person
        accounts_a = self._get_all_accounts(person_a)
        accounts_b = self._get_all_accounts(person_b)
        
        # Categorize accounts into themes
        themes_a = self._categorize_accounts_to_themes(accounts_a)
        themes_b = self._categorize_accounts_to_themes(accounts_b)
        
        # Find shared themes (both have substantial engagement)
        shared_themes = self._find_shared_themes(themes_a, themes_b, accounts_a, accounts_b)
        
        # Calculate theme-based score
        theme_score = self._calculate_theme_score(themes_a, themes_b, accounts_a, accounts_b)
        
        # Calculate individual category scores for breakdown
        scores = {
            "likes": self._score_category(person_a.get("likes", []), person_b.get("likes", []), "account"),
            "saved": self._score_category(person_a.get("saved", []), person_b.get("saved", []), "account"),
            "following": self._score_category(person_a.get("following", []), person_b.get("following", []), "username"),
            "comments": self._score_comments(person_a.get("comments", []), person_b.get("comments", [])),
        }
        
        # Weighted base score using RELAXED theme-aware scoring
        # Instead of pure Jaccard, blend theme similarity with exact matches
        base_score = self._calculate_blended_score(scores, theme_score, weights)
        
        # Calculate bonuses
        bonus_result = self._calculate_bonuses(scores, shared_themes)
        bonus_points = min(bonus_result["total"], self.config["max_bonus"])
        
        # Final score (rounded to whole number, capped at 100)
        final_score = min(round(base_score + bonus_points), 100)
        
        # Get label
        label = get_score_label(final_score)
        
        # Collect top shared themes as interests
        shared_interests = self._format_shared_themes(shared_themes)
        
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
    
    def _get_all_accounts(self, person_data: Dict) -> Set[str]:
        """Extract all account names from all categories."""
        accounts = set()
        
        for item in person_data.get("following", []):
            if item.get("username"):
                accounts.add(item["username"].lower().strip())
        
        for item in person_data.get("likes", []):
            if item.get("account"):
                accounts.add(item["account"].lower().strip())
        
        for item in person_data.get("saved", []):
            if item.get("account"):
                accounts.add(item["account"].lower().strip())
        
        return accounts
    
    def _categorize_accounts_to_themes(self, accounts: Set[str]) -> Dict[str, Set[str]]:
        """
        Categorize accounts into interest themes based on keywords.
        Returns dict of {theme_name: set of accounts in that theme}
        """
        theme_accounts = defaultdict(set)
        
        for account in accounts:
            for theme, keywords in self.interest_categories.items():
                for keyword in keywords:
                    if keyword.lower() in account:
                        theme_accounts[theme].add(account)
                        break  # Only match first keyword per theme
        
        return dict(theme_accounts)
    
    def _find_shared_themes(
        self, 
        themes_a: Dict[str, Set[str]], 
        themes_b: Dict[str, Set[str]],
        accounts_a: Set[str],
        accounts_b: Set[str]
    ) -> List[Dict]:
        """
        Find themes that both users engage with substantially.
        Returns top 5 themes sorted by combined strength.
        """
        shared = []
        
        all_themes = set(themes_a.keys()) | set(themes_b.keys())
        
        for theme in all_themes:
            accounts_in_a = themes_a.get(theme, set())
            accounts_in_b = themes_b.get(theme, set())
            
            count_a = len(accounts_in_a)
            count_b = len(accounts_in_b)
            
            # Both must have at least threshold accounts in this theme
            if count_a >= self.THEME_THRESHOLD and count_b >= self.THEME_THRESHOLD:
                # Find exact matches within this theme
                exact_matches = accounts_in_a & accounts_in_b
                
                # Calculate theme strength (geometric mean to balance both sides)
                combined_strength = (count_a * count_b) ** 0.5
                
                # Determine match quality
                if len(exact_matches) >= 3:
                    quality = "Strong match"
                elif len(exact_matches) >= 1:
                    quality = "Good match"
                else:
                    quality = "Shared interest"
                
                shared.append({
                    "theme": theme,
                    "count_a": count_a,
                    "count_b": count_b,
                    "exact_matches": len(exact_matches),
                    "combined_strength": combined_strength,
                    "quality": quality,
                })
        
        # Sort by combined strength, then by exact matches
        shared.sort(key=lambda x: (x["combined_strength"], x["exact_matches"]), reverse=True)
        
        # Return top 5
        return shared[:self.MAX_THEMES]
    
    def _calculate_theme_score(
        self,
        themes_a: Dict[str, Set[str]],
        themes_b: Dict[str, Set[str]],
        accounts_a: Set[str],
        accounts_b: Set[str]
    ) -> float:
        """
        Calculate theme-based similarity score.
        More relaxed than Jaccard - shared themes contribute to score.
        """
        if not themes_a and not themes_b:
            return 100.0  # Both have no categorized accounts = identical
        
        if not themes_a or not themes_b:
            return 25.0  # One has themes, other doesn't
        
        all_themes = set(themes_a.keys()) | set(themes_b.keys())
        shared_theme_count = 0
        exact_match_bonus = 0
        
        for theme in all_themes:
            accounts_in_a = themes_a.get(theme, set())
            accounts_in_b = themes_b.get(theme, set())
            
            # Theme counts as shared if both have accounts in it
            if accounts_in_a and accounts_in_b:
                shared_theme_count += 1
                
                # Exact matches within theme give bonus
                exact = len(accounts_in_a & accounts_in_b)
                exact_match_bonus += min(exact * 2, 10)  # Cap at 10 per theme
        
        # Base score: percentage of themes that are shared
        if len(all_themes) > 0:
            theme_overlap = shared_theme_count / len(all_themes)
        else:
            theme_overlap = 0
        
        # Score: 70% theme overlap + 30% exact match bonus (scaled)
        theme_score = (theme_overlap * 70) + min(exact_match_bonus, 30)
        
        return min(theme_score, 100)
    
    def _calculate_blended_score(
        self, 
        scores: Dict[str, Dict],
        theme_score: float,
        weights: Dict[str, float]
    ) -> float:
        """
        Blend exact match scores with theme-based similarity.
        This makes the scoring more relaxed while still rewarding exact matches.
        """
        # Traditional weighted score from exact matches
        exact_score = sum(weights[cat] * scores[cat]["score"] for cat in weights)
        
        # Blend: 40% exact matches + 60% theme similarity
        # This relaxes the scoring significantly
        blended = (exact_score * 0.4) + (theme_score * 0.6)
        
        return blended
    
    def _score_category(self, items_a: List[Dict], items_b: List[Dict], key: str) -> Dict:
        """Score a category using Jaccard similarity on exact matches."""
        set_a = set(
            item.get(key, "").lower().strip() 
            for item in items_a 
            if item.get(key)
        )
        set_b = set(
            item.get(key, "").lower().strip() 
            for item in items_b 
            if item.get(key)
        )
        
        # Jaccard similarity
        if not set_a and not set_b:
            similarity = 1.0
        elif not set_a or not set_b:
            similarity = 0.0
        else:
            intersection = set_a & set_b
            union = set_a | set_b
            similarity = len(intersection) / len(union) if union else 1.0
        
        overlap = set_a & set_b
        
        return {
            "score": round(similarity * 100, 1),
            "overlap_count": len(overlap),
            "overlap_items": list(overlap)[:20],
            "total_a": len(set_a),
            "total_b": len(set_b),
        }
    
    def _score_comments(self, comments_a: List[Dict], comments_b: List[Dict]) -> Dict:
        """Score comments based on engagement style similarity."""
        if not comments_a and not comments_b:
            return {"score": 100.0, "style_matches": ["Both have no comment history"]}
        
        if not comments_a or not comments_b:
            return {"score": 50.0, "style_matches": []}
        
        style_a = self._analyze_comment_style(comments_a)
        style_b = self._analyze_comment_style(comments_b)
        
        matches = []
        total_attributes = 4
        
        if style_a["length_category"] == style_b["length_category"]:
            matches.append(f"Similar comment length ({style_a['length_category']})")
        
        if style_a["emoji_heavy"] == style_b["emoji_heavy"]:
            desc = "emoji enthusiasts" if style_a["emoji_heavy"] else "minimal emoji users"
            matches.append(f"Both are {desc}")
        
        if style_a["asks_questions"] == style_b["asks_questions"]:
            desc = "curious (ask questions)" if style_a["asks_questions"] else "statement-makers"
            matches.append(f"Both are {desc}")
        
        if style_a["engagement_level"] == style_b["engagement_level"]:
            matches.append(f"Similar engagement level ({style_a['engagement_level']})")
        
        score = (len(matches) / total_attributes) * 100
        
        return {"score": round(score, 1), "style_matches": matches}
    
    def _analyze_comment_style(self, comments: List[Dict]) -> Dict:
        """Analyze commenting style."""
        if not comments:
            return {"length_category": "unknown", "emoji_heavy": False, "asks_questions": False, "engagement_level": "unknown"}
        
        total = len(comments)
        avg_length = sum(c.get("length", 0) for c in comments) / total if total else 0
        emoji_count = sum(1 for c in comments if c.get("has_emoji", False))
        question_count = sum(1 for c in comments if c.get("has_question", False))
        
        length_category = "short" if avg_length < 20 else "medium" if avg_length < 50 else "long"
        emoji_heavy = (emoji_count / total) > 0.3 if total else False
        asks_questions = (question_count / total) > 0.2 if total else False
        engagement_level = "casual" if total < 50 else "moderate" if total < 200 else "active"
        
        return {
            "length_category": length_category,
            "emoji_heavy": emoji_heavy,
            "asks_questions": asks_questions,
            "engagement_level": engagement_level,
        }
    
    def _calculate_bonuses(self, scores: Dict, shared_themes: List[Dict]) -> Dict:
        """Calculate bonus points."""
        bonuses = self.config["bonuses"]
        details = []
        total = 0
        
        # Bonus for following exact same accounts
        following_overlap = scores["following"].get("overlap_count", 0)
        if following_overlap >= 3:
            niche_bonus = min(following_overlap - 2, 5) * bonuses["same_niche_account"]
            total += niche_bonus
            details.append({
                "type": "same_niche_account",
                "description": f"Follow {following_overlap} of the same accounts",
                "points": niche_bonus,
            })
        
        # Bonus for shared theme categories
        strong_themes = [t for t in shared_themes if t["quality"] == "Strong match"]
        if len(strong_themes) >= 1:
            theme_bonus = min(len(strong_themes), 5) * bonuses["same_interest_category"]
            total += theme_bonus
            details.append({
                "type": "same_interest_category",
                "description": f"{len(strong_themes)} strong theme matches",
                "points": theme_bonus,
            })
        
        return {"total": total, "details": details}
    
    def _format_shared_themes(self, shared_themes: List[Dict]) -> List[Dict]:
        """Format shared themes for display."""
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
        
        formatted = []
        for theme_data in shared_themes:
            theme = theme_data["theme"]
            emoji = emoji_map.get(theme, "🎯")
            quality = theme_data["quality"]
            exact = theme_data["exact_matches"]
            
            if exact > 0:
                desc = f"{emoji} {theme} — {quality} ({exact} exact)"
            else:
                desc = f"{emoji} {theme} — {quality}"
            
            formatted.append({
                "type": "interest",
                "value": theme,
                "description": desc,
                "quality": quality,
            })
        
        return formatted


# Convenience function
def analyze_compatibility(person_a: Dict, person_b: Dict, config: Dict = None) -> Dict:
    """Analyze compatibility between two Instagram profiles."""
    analyzer = CompatibilityAnalyzer(config)
    return analyzer.analyze(person_a, person_b)
