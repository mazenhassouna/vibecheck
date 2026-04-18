"""
Scoring Configuration for Instagram Compatibility Analysis

All weights and bonuses are easily adjustable in this file.
Weights must sum to 1.0 for accurate percentage-based scoring.
"""

SCORING_CONFIG = {
    # ===========================================
    # CATEGORY WEIGHTS (must sum to 1.0)
    # Simplified to core engagement signals
    # ===========================================
    "weights": {
        "likes": 0.33,       # Content they actively like
        "saved": 0.33,       # Content they intentionally save
        "following": 0.34,   # Accounts they follow
    },
    
    # ===========================================
    # BONUS POINTS (added to final score)
    # ===========================================
    "bonuses": {
        "same_niche_account": 3,      # Per shared niche/small account
        "same_exact_saved_post": 2,   # Per exact same saved post
        "same_interest_category": 2,  # Per shared interest category
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
]


# ===========================================
# INTEREST CATEGORIES
# Keywords to categorize accounts into interest themes
# ===========================================
INTEREST_CATEGORIES = {
    "Photography": ["photo", "camera", "lens", "capture", "visuals", "portrait", "landscape", "natgeo", "chrisburkard"],
    "Fitness & Gym": ["gym", "lift", "fitness", "bodybuilding", "workout", "gains", "muscle", "cbum", "noeldeyzel", "moreplatesmoredates"],
    "Sports": ["boxing", "cricket", "basketball", "football", "soccer", "mma", "ufc", "makhachev", "sports"],
    "Tech & Coding": ["dev", "code", "tech", "programming", "software", "engineer", "hacker", "cyber"],
    "Food & Cooking": ["cook", "chef", "food", "recipe", "kitchen", "bake", "eat", "foodie"],
    "Travel & Adventure": ["travel", "wander", "explore", "adventure", "hiking", "backpack", "nomad", "wanderlust"],
    "Islam & Religion": ["islamic", "mufti", "mosque", "imam", "muslim", "quran", "deen", "halal", "bukhari", "menkofficial"],
    "Anime & Manga": ["anime", "manga", "otaku", "weeb", "japan", "cosplay"],
    "Memes & Comedy": ["meme", "funny", "comedy", "humor", "lol", "shitpost", "dank"],
    "Art & Design": ["art", "design", "draw", "paint", "creative", "illustration", "artist"],
    "Music": ["music", "song", "dj", "producer", "beats", "spotify", "playlist"],
    "Gaming": ["game", "gaming", "esport", "twitch", "stream", "gamer", "playstation", "xbox"],
    "Fashion & Style": ["fashion", "style", "outfit", "clothing", "drip", "sneaker", "streetwear"],
    "Cars & Motors": ["car", "auto", "motor", "drift", "racing", "bike", "wheelie"],
    "Nature & Animals": ["nature", "animal", "wildlife", "dog", "cat", "pet", "outdoor"],
    "Self-Improvement": ["motivation", "mindset", "success", "grind", "hustle", "entrepreneur", "growth"],
}


# ===========================================
# WAYS TO CONNECT
# Suggestions for activities based on shared interests
# ===========================================
WAYS_TO_CONNECT = {
    "Photography": ["Go on a photo walk together", "Share your favorite shots", "Visit a scenic spot to shoot"],
    "Fitness & Gym": ["Hit the gym together", "Share workout routines", "Try a new fitness class"],
    "Sports": ["Watch a game together", "Play a pickup game", "Discuss your favorite athletes"],
    "Tech & Coding": ["Work on a project together", "Share coding tips", "Attend a hackathon"],
    "Food & Cooking": ["Cook a meal together", "Try a new restaurant", "Share recipes"],
    "Travel & Adventure": ["Plan a trip together", "Share travel stories", "Explore a new place locally"],
    "Islam & Religion": ["Attend Jummah together", "Discuss your favorite lectures", "Study Quran together"],
    "Anime & Manga": ["Watch a series together", "Discuss your favorite manga", "Attend an anime convention"],
    "Memes & Comedy": ["Share memes", "Watch comedy specials together", "Create content together"],
    "Art & Design": ["Visit an art gallery", "Do a drawing session", "Share creative projects"],
    "Music": ["Share playlists", "Go to a concert", "Discover new artists together"],
    "Gaming": ["Play games together", "Discuss favorite games", "Watch esports together"],
    "Fashion & Style": ["Go shopping together", "Share outfit ideas", "Discuss fashion trends"],
    "Cars & Motors": ["Go to a car meet", "Discuss modifications", "Take a road trip"],
    "Nature & Animals": ["Go hiking", "Visit a park", "Share pet photos"],
    "Self-Improvement": ["Share book recommendations", "Discuss goals", "Motivate each other"],
}


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
