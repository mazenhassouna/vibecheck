"""
Scoring Configuration for Instagram Compatibility Analysis

All weights and bonuses are easily adjustable in this file.
Weights must sum to 1.0 for accurate percentage-based scoring.
"""

SCORING_CONFIG = {
    # ===========================================
    # CATEGORY WEIGHTS (must sum to 1.0)
    # ===========================================
    "weights": {
        "likes": 0.25,       # Content they actively like
        "saved": 0.25,       # Content they intentionally save
        "following": 0.25,   # Accounts they follow
        "topics": 0.15,      # Instagram's inferred interests
        "comments": 0.10,    # Engagement style similarity
    },
    
    # ===========================================
    # FOLLOWING SUB-WEIGHTS
    # ===========================================
    "following_weights": {
        "direct_overlap": 0.4,      # Same exact accounts
        "category_similarity": 0.6,  # Similar account types
    },
    
    # ===========================================
    # BONUS POINTS (added to final score)
    # ===========================================
    "bonuses": {
        "same_niche_account": 3,      # Per shared niche/small account
        "same_exact_saved_post": 2,   # Per exact same saved post
        "mutual_follow": 5,           # If they follow each other
        "same_top_topics": 5,         # If top 3 topics match
    },
    
    # Maximum bonus points allowed (prevents over-inflation)
    "max_bonus": 15,
    
    # ===========================================
    # SCORE LABELS (thresholds)
    # ===========================================
    "labels": {
        85: {"emoji": "🔥", "text": "Highly Compatible"},
        70: {"emoji": "💚", "text": "Compatible"},
        50: {"emoji": "🤝", "text": "Some Common Ground"},
        30: {"emoji": "🌱", "text": "Potential"},
        0:  {"emoji": "🔍", "text": "Different Vibes"},
    },
}


# ===========================================
# PRIVACY ALLOWLIST
# Only these files will be processed from the Instagram export
# Paths based on actual Instagram export structure (2024-2026)
# ===========================================
ALLOWED_FILES = [
    # Likes - actual paths from Instagram export
    "your_instagram_activity/likes/liked_posts.json",
    "your_instagram_activity/likes/liked_comments.json",
    "likes/liked_posts.json",
    "likes/liked_comments.json",
    "liked_posts.json",
    
    # Saved posts - actual paths
    "your_instagram_activity/saved/saved_posts.json",
    "your_instagram_activity/saved/saved_collections.json",
    "saved/saved_posts.json",
    "saved/saved_collections.json",
    "saved_posts.json",
    
    # Comments - actual paths (note: can have _1, _2 suffixes)
    "your_instagram_activity/comments/post_comments_1.json",
    "your_instagram_activity/comments/post_comments.json",
    "your_instagram_activity/comments/reels_comments.json",
    "comments/post_comments_1.json",
    "comments/post_comments.json",
    "comments/reels_comments.json",
    
    # Following - actual paths
    "connections/followers_and_following/following.json",
    "followers_and_following/following.json",
    "following.json",
    
    # Topics - actual paths
    "preferences/your_topics/recommended_topics.json",
    "your_topics/recommended_topics.json",
    "your_topics/your_topics.json",
    "recommended_topics.json",
]


def get_score_label(score: int) -> dict:
    """Get the label and emoji for a given score."""
    for threshold in sorted(SCORING_CONFIG["labels"].keys(), reverse=True):
        if score >= threshold:
            return SCORING_CONFIG["labels"][threshold]
    return SCORING_CONFIG["labels"][0]


def validate_config():
    """Validate that weights sum to 1.0"""
    weights_sum = sum(SCORING_CONFIG["weights"].values())
    if abs(weights_sum - 1.0) > 0.001:
        raise ValueError(f"Weights must sum to 1.0, got {weights_sum}")
    return True
