"""
Compatibility Analyzer

Theme-based scoring that focuses on shared interests rather than exact account matches.
Provides sentence-form examples and ways to connect for strong matches.

SCORING PRINCIPLE: Identical data should ALWAYS yield 100% compatibility.
"""

from typing import Dict, List, Any, Set
from collections import defaultdict
from scoring_config import SCORING_CONFIG, INTEREST_CATEGORIES, WAYS_TO_CONNECT, get_score_label


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
        self.ways_to_connect = WAYS_TO_CONNECT
    
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
        shared_themes = self._find_shared_themes(themes_a, themes_b)
        
        # Calculate theme-based score
        theme_score = self._calculate_theme_score(themes_a, themes_b)
        
        # Calculate individual category scores for breakdown (without comments)
        scores = {
            "likes": self._score_category(person_a.get("likes", []), person_b.get("likes", []), "account"),
            "saved": self._score_category(person_a.get("saved", []), person_b.get("saved", []), "account"),
            "following": self._score_category(person_a.get("following", []), person_b.get("following", []), "username"),
        }
        
        # Calculate blended score
        base_score = self._calculate_blended_score(scores, theme_score, weights)
        
        # Calculate bonuses
        bonus_result = self._calculate_bonuses(scores, shared_themes)
        bonus_points = min(bonus_result["total"], self.config["max_bonus"])
        
        # Final score (rounded to whole number, capped at 100)
        final_score = min(round(base_score + bonus_points), 100)
        
        # Get label
        label = get_score_label(final_score)
        
        # Format shared themes with examples and ways to connect
        shared_interests = self._format_shared_themes_with_examples(shared_themes)
        
        # Generate holistic relationship summary
        relationship_summary = self._generate_relationship_summary(
            final_score, shared_themes, scores
        )
        
        return {
            "score": final_score,
            "label": label,
            "relationship_summary": relationship_summary,
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
            "theme_score": round(theme_score, 1),
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
        """Categorize accounts into interest themes based on keywords."""
        theme_accounts = defaultdict(set)
        
        for account in accounts:
            for theme, keywords in self.interest_categories.items():
                for keyword in keywords:
                    if keyword.lower() in account:
                        theme_accounts[theme].add(account)
                        break
        
        return dict(theme_accounts)
    
    def _find_shared_themes(
        self, 
        themes_a: Dict[str, Set[str]], 
        themes_b: Dict[str, Set[str]]
    ) -> List[Dict]:
        """Find themes that both users engage with substantially."""
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
                
                # Calculate theme strength
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
                    "exact_matches": list(exact_matches),
                    "combined_strength": combined_strength,
                    "quality": quality,
                })
        
        # Sort by combined strength, then by exact matches
        shared.sort(key=lambda x: (x["combined_strength"], len(x["exact_matches"])), reverse=True)
        
        return shared[:self.MAX_THEMES]
    
    def _calculate_theme_score(
        self,
        themes_a: Dict[str, Set[str]],
        themes_b: Dict[str, Set[str]]
    ) -> float:
        """Calculate theme-based similarity score."""
        if not themes_a and not themes_b:
            return 100.0
        
        if not themes_a or not themes_b:
            return 25.0
        
        all_themes = set(themes_a.keys()) | set(themes_b.keys())
        shared_theme_count = 0
        exact_match_bonus = 0
        
        for theme in all_themes:
            accounts_in_a = themes_a.get(theme, set())
            accounts_in_b = themes_b.get(theme, set())
            
            if accounts_in_a and accounts_in_b:
                shared_theme_count += 1
                exact = len(accounts_in_a & accounts_in_b)
                exact_match_bonus += min(exact * 2, 10)
        
        if len(all_themes) > 0:
            theme_overlap = shared_theme_count / len(all_themes)
        else:
            theme_overlap = 0
        
        theme_score = (theme_overlap * 70) + min(exact_match_bonus, 30)
        
        return min(theme_score, 100)
    
    def _calculate_blended_score(
        self, 
        scores: Dict[str, Dict],
        theme_score: float,
        weights: Dict[str, float]
    ) -> float:
        """Blend exact match scores with theme-based similarity."""
        exact_score = sum(weights[cat] * scores[cat]["score"] for cat in weights)
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
    
    def _generate_relationship_summary(
        self, 
        score: int, 
        shared_themes: List[Dict],
        scores: Dict[str, Dict]
    ) -> Dict[str, str]:
        """Generate a holistic relationship summary."""
        strong_themes = [t for t in shared_themes if t["quality"] == "Strong match"]
        good_themes = [t for t in shared_themes if t["quality"] == "Good match"]
        
        # Get theme names
        strong_names = [t["theme"] for t in strong_themes]
        all_shared_names = [t["theme"] for t in shared_themes]
        
        # Build headline based on score
        if score >= 85:
            headline = "You two are a fantastic match! 🎉"
            vibe = "highly compatible"
        elif score >= 70:
            headline = "You have a lot in common! 💚"
            vibe = "quite compatible"
        elif score >= 50:
            headline = "You share some common ground 🤝"
            vibe = "somewhat compatible"
        elif score >= 30:
            headline = "There's potential here 🌱"
            vibe = "different but with some overlap"
        else:
            headline = "You have different vibes 🔍"
            vibe = "quite different"
        
        # Build description
        if strong_themes:
            themes_text = " and ".join(strong_names[:2])
            description = f"You both share a strong interest in {themes_text}, "
            description += "which suggests you could bond quickly over shared passions. "
        elif good_themes:
            themes_text = " and ".join([t["theme"] for t in good_themes[:2]])
            description = f"You both engage with {themes_text} content, "
            description += "which gives you common ground to start from. "
        elif shared_themes:
            description = "While you don't follow the exact same accounts, "
            description += "you do share similar interest areas. "
        else:
            description = "Your Instagram activity shows different interests, "
            description += "but that doesn't mean you can't connect! "
        
        # Add relationship dynamic
        if score >= 70:
            dynamic = "You're likely to find common ground quickly and have plenty to talk about from day one."
        elif score >= 50:
            dynamic = "You may need to explore a bit to find your connection points, but they're there."
        else:
            dynamic = "You might bring different perspectives to the table, which can lead to interesting conversations."
        
        return {
            "headline": headline,
            "description": description,
            "dynamic": dynamic,
            "vibe": vibe,
        }
    
    def _format_shared_themes_with_examples(self, shared_themes: List[Dict]) -> List[Dict]:
        """Format shared themes with sentence examples. Ways to connect only for Strong matches."""
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
            exact_matches = theme_data["exact_matches"]
            
            # Create sentence-form examples for exact matches
            examples = []
            for account in exact_matches[:3]:
                examples.append(self._create_example_sentence(theme, account))
            
            # ONLY get ways to connect for Strong matches
            connect_ideas = []
            if quality == "Strong match":
                connect_ideas = self.ways_to_connect.get(theme, [])[:2]
            
            formatted.append({
                "type": "interest",
                "theme": theme,
                "emoji": emoji,
                "quality": quality,
                "examples": examples,
                "ways_to_connect": connect_ideas,
                "description": f"{emoji} {theme}",
            })
        
        return formatted
    
    def _create_example_sentence(self, theme: str, account: str) -> str:
        """Create a natural sentence describing the shared account."""
        # Clean up account name for display
        display_name = account.replace("_", " ").replace(".", " ").title()
        
        # Theme-specific sentence templates
        templates = {
            "Photography": f"You both enjoy {display_name}'s photography",
            "Fitness & Gym": f"You both follow {display_name} for fitness content",
            "Sports": f"You both follow {display_name} for sports content",
            "Tech & Coding": f"You both follow {display_name} for tech content",
            "Food & Cooking": f"You both follow {display_name} for food content",
            "Travel & Adventure": f"You both follow {display_name} for travel inspiration",
            "Islam & Religion": f"You both follow {display_name} for Islamic content",
            "Anime & Manga": f"You both enjoy {display_name}'s anime content",
            "Memes & Comedy": f"You both find {display_name} funny",
            "Art & Design": f"You both appreciate {display_name}'s art",
            "Music": f"You both enjoy {display_name}'s music",
            "Gaming": f"You both follow {display_name} for gaming",
            "Fashion & Style": f"You both follow {display_name} for style inspiration",
            "Cars & Motors": f"You both follow {display_name} for car content",
            "Nature & Animals": f"You both enjoy {display_name}'s nature content",
            "Self-Improvement": f"You both follow {display_name} for motivation",
        }
        
        return templates.get(theme, f"You both follow @{account}")


# Convenience function
def analyze_compatibility(person_a: Dict, person_b: Dict, config: Dict = None) -> Dict:
    """Analyze compatibility between two Instagram profiles."""
    analyzer = CompatibilityAnalyzer(config)
    return analyzer.analyze(person_a, person_b)
