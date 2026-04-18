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
# INTEREST CATEGORIES (EXPANDED)
# Keywords to categorize accounts into interest themes
# More keywords = better detection
# ===========================================
INTEREST_CATEGORIES = {
    # ===== FITNESS & HEALTH =====
    "Fitness & Gym": [
        "gym", "lift", "fitness", "bodybuilding", "workout", "gains", "muscle", "cbum", 
        "noeldeyzel", "moreplatesmoredates", "powerlifting", "crossfit", "weightlifting",
        "deadlift", "squat", "bench", "bulk", "shred", "physique", "aesthetics",
        "bodybuilder", "fitfam", "fitlife", "strongman", "gymshark", "myprotein",
        "roidtest", "natty", "flex", "pump", "grind", "gains", "maxtaylor", "cbumfitness"
    ],
    "Calisthenics": [
        "calisthenics", "streetworkout", "pullup", "pushup", "handstand", "planche",
        "muscleup", "barbrothers", "thenx", "chrirheria", "hannibalforking"
    ],
    "Running & Cardio": [
        "running", "marathon", "cardio", "jogging", "runner", "5k", "10k", "halfmarathon",
        "strava", "nike", "adidas", "asics", "runclub", "couch2", "ultra"
    ],
    "Yoga & Wellness": [
        "yoga", "meditation", "mindfulness", "wellness", "stretching", "pilates",
        "breathwork", "chakra", "holistic", "selfcare", "mentalhealth"
    ],
    "Nutrition & Diet": [
        "nutrition", "diet", "meal", "macros", "calories", "protein", "keto",
        "vegan", "vegetarian", "paleo", "intermittentfasting", "mealprep"
    ],
    
    # ===== SPORTS =====
    "MMA & Combat Sports": [
        "mma", "ufc", "boxing", "muaythai", "bjj", "jiujitsu", "wrestling", "kickboxing",
        "makhachev", "khabib", "jones", "adesanya", "makhachev", "conor", "dana",
        "bellator", "onefc", "pfl", "tapout", "fightnight", "knockout"
    ],
    "Soccer/Football": [
        "soccer", "football", "futbol", "messi", "ronaldo", "neymar", "mbappe",
        "haaland", "premierleague", "laliga", "ucl", "fifaworldcup", "epl",
        "manchesterunited", "realmadrid", "barcelona", "chelsea", "arsenal"
    ],
    "Basketball": [
        "basketball", "nba", "hoops", "dunk", "lebron", "curry", "durant", "giannis",
        "lakers", "warriors", "celtics", "ballislife", "overtime", "slam"
    ],
    "Cricket": [
        "cricket", "ipl", "t20", "odi", "test", "kohli", "babar", "dhoni", "rohit",
        "worldcup", "ashes", "bigbash", "psl", "cricbuzz", "espncricinfo"
    ],
    "American Football": [
        "nfl", "americanfootball", "superbowl", "touchdown", "patriots", "chiefs",
        "cowboys", "packers", "mahomes", "bradynfl", "collegefootball"
    ],
    "Tennis": [
        "tennis", "atp", "wta", "wimbledon", "usopen", "rolandgarros", "australianopen",
        "djokovic", "nadal", "federer", "alcaraz", "sinner", "grandslam"
    ],
    "F1 & Motorsport": [
        "f1", "formula1", "motorsport", "verstappen", "hamilton", "leclerc", "ferrari",
        "redbullracing", "mercedes", "mclaren", "alpinef1", "indycar", "nascar"
    ],
    "Golf": [
        "golf", "pga", "masters", "tigerwoods", "rory", "scottie", "livgolf",
        "golfer", "golfswing", "golfcourse", "pgatour"
    ],
    "Extreme Sports": [
        "skateboarding", "surfing", "snowboarding", "bmx", "parkour", "freerunning",
        "skydiving", "bungee", "climbing", "bouldering", "xgames"
    ],
    
    # ===== RELIGION & SPIRITUALITY =====
    "Islam & Muslim Life": [
        "islamic", "mufti", "mosque", "imam", "muslim", "quran", "deen", "halal",
        "bukhari", "menkofficial", "hijab", "sunnah", "hadith", "ramadan", "eid",
        "jummah", "salah", "dawah", "ummah", "masjid", "sheikh", "alhamdulillah",
        "fajr", "tawheed", "seerah", "islamicreminders", "deentour"
    ],
    "Christianity": [
        "christian", "church", "jesus", "bible", "gospel", "worship", "praise",
        "pastor", "sermon", "faith", "godly", "blessed", "scripture", "proverbs"
    ],
    "Hinduism": [
        "hindu", "temple", "puja", "diwali", "mantra", "vedic", "krishna", "shiva",
        "ganesh", "yoga", "chakra", "ayurveda", "namaste"
    ],
    "Spirituality": [
        "spiritual", "meditation", "mindfulness", "consciousness", "awakening",
        "energy", "manifestation", "universe", "zen", "enlightenment"
    ],
    
    # ===== ENTERTAINMENT =====
    "Anime & Manga": [
        "anime", "manga", "otaku", "weeb", "japan", "cosplay", "naruto", "onepiece",
        "dragonball", "jujutsukaisen", "demonslayer", "attackontitan", "myheroacademia",
        "bleach", "hunterxhunter", "tokyoghoul", "deathnote", "chainsaw", "jojo",
        "animeart", "animememes", "mangapanel", "manhwa", "webtoon", "shonen"
    ],
    "Movies & Cinema": [
        "movie", "film", "cinema", "hollywood", "director", "actor", "oscar",
        "marvel", "dc", "starwars", "imdb", "rottentomatoes", "filmmaker",
        "cinematography", "screenplay", "blockbuster", "indie"
    ],
    "TV Shows & Series": [
        "tvshow", "netflix", "hbo", "disney", "streaming", "binge", "series",
        "gameofthrones", "strangerthings", "theoffice", "friends", "breakingbad"
    ],
    "K-Pop & K-Drama": [
        "kpop", "kdrama", "bts", "blackpink", "twice", "exo", "nct", "stray",
        "seventeen", "koreandrama", "hallyu", "idol", "army", "blink"
    ],
    "Memes & Comedy": [
        "meme", "funny", "comedy", "humor", "lol", "shitpost", "dank", "vine",
        "tiktok", "skit", "parody", "satire", "joke", "roast", "standup"
    ],
    
    # ===== CREATIVE =====
    "Photography": [
        "photo", "camera", "lens", "capture", "visuals", "portrait", "landscape",
        "natgeo", "chrisburkard", "photography", "canon", "sony", "nikon", "fuji",
        "lightroom", "photoshoot", "photographer", "streetphotography", "35mm"
    ],
    "Art & Illustration": [
        "art", "artist", "draw", "drawing", "paint", "painting", "illustration",
        "sketch", "watercolor", "digital", "procreate", "artoftheday", "gallery",
        "contemporary", "abstract", "realism", "portrait", "fanart"
    ],
    "Graphic Design": [
        "design", "graphic", "designer", "logo", "branding", "typography", "poster",
        "photoshop", "illustrator", "figma", "ux", "ui", "creative", "visual"
    ],
    "Music Production": [
        "producer", "beats", "music", "song", "dj", "edm", "hiphop", "trap", "rnb",
        "spotify", "soundcloud", "ableton", "flstudio", "mixing", "mastering"
    ],
    "Content Creation": [
        "creator", "youtuber", "tiktoker", "influencer", "vlog", "podcast",
        "streaming", "content", "viral", "socialmedia", "brand"
    ],
    "Videography & Film": [
        "video", "videography", "filmmaker", "cinematography", "editing", "premiere",
        "finalcut", "davinci", "shortfilm", "documentary", "drone", "gimbal"
    ],
    
    # ===== TECH & GAMING =====
    "Tech & Coding": [
        "dev", "code", "tech", "programming", "software", "engineer", "hacker",
        "cyber", "python", "javascript", "react", "web", "app", "startup",
        "ai", "machinelearning", "data", "cloud", "devops", "github"
    ],
    "Gaming": [
        "game", "gaming", "esport", "twitch", "stream", "gamer", "playstation",
        "xbox", "nintendo", "pc", "valorant", "fortnite", "minecraft", "callofduty",
        "apex", "leagueoflegends", "csgo", "dota", "roblox", "gta"
    ],
    "PC Building": [
        "pcbuild", "pcmasterrace", "gpu", "cpu", "rgb", "nvidia", "amd", "intel",
        "custompc", "battlestation", "setup", "mechanical", "keyboard"
    ],
    "Tech Reviews": [
        "techreview", "unboxing", "gadget", "smartphone", "iphone", "android",
        "samsung", "apple", "mkbhd", "linustechtips", "tech"
    ],
    
    # ===== LIFESTYLE =====
    "Fashion & Style": [
        "fashion", "style", "outfit", "clothing", "drip", "sneaker", "streetwear",
        "luxury", "designer", "ootd", "menswear", "womenswear", "vintage",
        "thrift", "hypebeast", "supreme", "nike", "adidas"
    ],
    "Fragrance & Grooming": [
        "fragrance", "perfume", "cologne", "scent", "grooming", "skincare",
        "haircare", "barber", "beard", "dior", "chanel", "tomford", "creed"
    ],
    "Watches & Accessories": [
        "watch", "rolex", "omega", "seiko", "casio", "timepiece", "horology",
        "watchcollector", "jewelry", "accessories", "luxury"
    ],
    "Food & Cooking": [
        "cook", "chef", "food", "recipe", "kitchen", "bake", "eat", "foodie",
        "restaurant", "homecook", "foodporn", "delicious", "yummy", "gourmet",
        "culinary", "masterchef", "gordonramsay"
    ],
    "Coffee & Tea": [
        "coffee", "cafe", "espresso", "latte", "barista", "coffeeshop", "brew",
        "tea", "matcha", "specialtycoffee", "coffeeaddict"
    ],
    
    # ===== TRAVEL & OUTDOORS =====
    "Travel & Adventure": [
        "travel", "wander", "explore", "adventure", "hiking", "backpack", "nomad",
        "wanderlust", "passport", "vacation", "trip", "worldtravel", "travelphotography",
        "digitalnomad", "solotravel", "roadtrip", "backpacking"
    ],
    "Nature & Wildlife": [
        "nature", "wildlife", "outdoor", "forest", "mountain", "ocean", "beach",
        "sunset", "landscape", "earthpix", "discoverearth", "natgeo", "planet"
    ],
    "Camping & Survival": [
        "camping", "camp", "tent", "survival", "bushcraft", "wilderness", "fire",
        "offgrid", "overlanding", "vanlife", "rv", "glamping"
    ],
    "Pets & Animals": [
        "dog", "cat", "pet", "puppy", "kitten", "animal", "petlover", "doggo",
        "catto", "goldenretriever", "labrador", "germanshepherd", "husky"
    ],
    
    # ===== BUSINESS & LEARNING =====
    "Self-Improvement": [
        "motivation", "mindset", "success", "grind", "hustle", "entrepreneur",
        "growth", "discipline", "focus", "productivity", "habits", "goals",
        "selfhelp", "personaldevelopment", "winning"
    ],
    "Finance & Investing": [
        "finance", "invest", "stock", "crypto", "bitcoin", "trading", "wealth",
        "money", "passive", "income", "realestate", "wallstreet", "financial"
    ],
    "Business & Startups": [
        "business", "startup", "ceo", "founder", "entrepreneur", "company",
        "marketing", "sales", "brand", "ecommerce", "saas", "venture"
    ],
    "Education & Learning": [
        "education", "learn", "student", "university", "college", "study",
        "book", "reading", "knowledge", "course", "tutorial", "skill"
    ],
    
    # ===== AUTOMOTIVE =====
    "Cars & Supercars": [
        "car", "auto", "supercar", "hypercar", "exotic", "ferrari", "lamborghini",
        "porsche", "bmw", "mercedes", "audi", "mclaren", "bugatti", "pagani",
        "carshow", "carmeet", "gtr", "jdm", "tuner", "modified"
    ],
    "JDM & Tuning": [
        "jdm", "nissan", "toyota", "honda", "mitsubishi", "subaru", "supra",
        "gtr", "civic", "wrx", "evo", "rx7", "silvia", "drifting", "boost"
    ],
    "Motorcycles": [
        "motorcycle", "bike", "rider", "bikelife", "wheelie", "motorbike",
        "sportbike", "harley", "ducati", "yamaha", "kawasaki", "cbr", "r1"
    ],
    
    # ===== CULTURE & COMMUNITY =====
    "Middle Eastern Culture": [
        "arab", "arabic", "khaleeji", "levant", "palestinian", "egyptian",
        "lebanese", "syrian", "iraqi", "saudi", "emirati", "dubai", "qatar"
    ],
    "South Asian Culture": [
        "desi", "indian", "pakistani", "bangladeshi", "punjabi", "bollywood",
        "curry", "biryani", "cricket", "lahore", "karachi", "delhi", "mumbai"
    ],
    "African Culture": [
        "african", "nigeria", "ghana", "kenya", "southafrica", "ethiopia",
        "afrobeats", "nollywood", "african", "lagos", "nairobi"
    ],
    "Latino Culture": [
        "latino", "latina", "hispanic", "mexican", "colombian", "brazilian",
        "reggaeton", "salsa", "bachata", "spanish", "latinx"
    ],
    
    # ===== HUMOR & INTERNET =====
    "Internet Culture": [
        "meme", "viral", "trending", "twitter", "reddit", "tiktok", "reels",
        "fyp", "foryou", "challenge", "trend", "internet", "stan"
    ],
    "Dark Humor": [
        "darkhumor", "edgy", "offensive", "cursed", "bruh", "sus", "based",
        "sigma", "chad", "wojak", "pepe"
    ],
    
    # ===== MENTAL HEALTH & WELLNESS =====
    "Mental Health": [
        "mentalhealth", "anxiety", "depression", "therapy", "healing", "trauma",
        "recovery", "support", "awareness", "selfcare", "mindfulness"
    ],
    "Positivity & Quotes": [
        "positivity", "quotes", "inspiration", "motivational", "wisdom",
        "positive", "vibes", "grateful", "blessed", "affirmation"
    ],
}


# ===========================================
# WAYS TO CONNECT (EXPANDED)
# Suggestions for activities based on shared interests
# ===========================================
WAYS_TO_CONNECT = {
    # Fitness
    "Fitness & Gym": ["Hit the gym together", "Share workout routines", "Try a new fitness class", "Spot each other on lifts"],
    "Calisthenics": ["Do a park workout together", "Learn a new skill together", "Film each other's progress"],
    "Running & Cardio": ["Go for a run together", "Sign up for a race", "Join a running club together"],
    "Yoga & Wellness": ["Attend a yoga class together", "Share meditation techniques", "Do a wellness retreat"],
    "Nutrition & Diet": ["Meal prep together", "Share healthy recipes", "Try a new restaurant with your diet"],
    
    # Sports
    "MMA & Combat Sports": ["Watch a fight together", "Take a martial arts class", "Discuss fight predictions"],
    "Soccer/Football": ["Watch a match together", "Play a pickup game", "Discuss transfer news"],
    "Basketball": ["Play pickup basketball", "Watch NBA games together", "Discuss player stats"],
    "Cricket": ["Watch a match together", "Play gully cricket", "Discuss team selections"],
    "American Football": ["Watch games together", "Join a fantasy league", "Discuss plays and strategy"],
    "Tennis": ["Play tennis together", "Watch Grand Slams together", "Practice your serve"],
    "F1 & Motorsport": ["Watch races together", "Play F1 video games", "Visit a race track"],
    "Golf": ["Play a round together", "Practice at the driving range", "Watch tournaments together"],
    "Extreme Sports": ["Try a new extreme sport", "Watch X Games together", "Share footage"],
    
    # Religion
    "Islam & Muslim Life": ["Attend Jummah together", "Discuss favorite lectures", "Study Quran together", "Do iftar together"],
    "Christianity": ["Attend church together", "Join a Bible study group", "Volunteer together"],
    "Hinduism": ["Visit a temple together", "Celebrate festivals together", "Discuss philosophy"],
    "Judaism": ["Attend Shabbat dinner", "Discuss traditions", "Visit historical sites"],
    "Spirituality": ["Meditate together", "Discuss spiritual journeys", "Attend workshops together"],
    
    # Entertainment
    "Anime & Manga": ["Watch a series together", "Discuss favorite manga", "Attend an anime convention", "Share recommendations"],
    "Movies & Cinema": ["Have a movie night", "Discuss film theories", "Visit a film festival"],
    "TV Shows & Series": ["Binge-watch together", "Discuss plot theories", "Share recommendations"],
    "K-Pop & K-Drama": ["Watch K-dramas together", "Learn a dance", "Discuss your bias"],
    "Memes & Comedy": ["Share memes", "Watch comedy specials together", "Create content together"],
    
    # Creative
    "Photography": ["Go on a photo walk together", "Share your favorite shots", "Visit a scenic spot to shoot"],
    "Art & Illustration": ["Visit an art gallery", "Do a drawing session", "Share creative projects"],
    "Graphic Design": ["Collaborate on a project", "Share design tips", "Critique each other's work"],
    "Music Production": ["Make a beat together", "Share production tips", "Attend a concert"],
    "Content Creation": ["Collaborate on content", "Share growth strategies", "Review each other's content"],
    "Videography & Film": ["Film a project together", "Share editing techniques", "Watch films for inspiration"],
    
    # Tech & Gaming
    "Tech & Coding": ["Work on a project together", "Share coding tips", "Attend a hackathon", "Debug code together"],
    "Gaming": ["Play games together", "Discuss favorite games", "Watch esports together", "Join a clan/guild"],
    "PC Building": ["Build a PC together", "Share setup pics", "Discuss upgrades"],
    "Tech Reviews": ["Discuss new tech", "Watch reviews together", "Compare gadgets"],
    
    # Lifestyle
    "Fashion & Style": ["Go shopping together", "Share outfit ideas", "Discuss fashion trends"],
    "Fragrance & Grooming": ["Test fragrances together", "Share grooming tips", "Visit a barbershop together"],
    "Watches & Accessories": ["Visit a watch store", "Discuss collections", "Share new pickups"],
    "Food & Cooking": ["Cook a meal together", "Try a new restaurant", "Share recipes", "Food tour together"],
    "Coffee & Tea": ["Visit coffee shops together", "Try new brewing methods", "Do a coffee/tea tasting"],
    
    # Travel & Outdoors
    "Travel & Adventure": ["Plan a trip together", "Share travel stories", "Explore a new place locally"],
    "Nature & Wildlife": ["Go hiking", "Visit a national park", "Photography expedition"],
    "Camping & Survival": ["Go camping together", "Learn survival skills", "Plan an outdoor adventure"],
    "Pets & Animals": ["Take dogs for a walk", "Visit an animal shelter", "Share pet photos"],
    
    # Business & Learning
    "Self-Improvement": ["Share book recommendations", "Discuss goals", "Motivate each other", "Accountability partnership"],
    "Finance & Investing": ["Discuss investment strategies", "Share resources", "Analyze markets together"],
    "Business & Startups": ["Brainstorm ideas", "Network together", "Share business tips"],
    "Education & Learning": ["Study together", "Share learning resources", "Discuss interesting topics"],
    
    # Automotive
    "Cars & Supercars": ["Go to a car meet", "Discuss modifications", "Take a road trip"],
    "JDM & Tuning": ["Work on cars together", "Visit car meets", "Go to a drift event"],
    "Motorcycles": ["Go for a group ride", "Discuss bike mods", "Visit a motorcycle show"],
    
    # Culture
    "Middle Eastern Culture": ["Cook Middle Eastern food together", "Discuss culture", "Attend community events"],
    "South Asian Culture": ["Cook desi food together", "Watch Bollywood together", "Attend cultural events"],
    "African Culture": ["Share music and culture", "Cook African dishes", "Attend community events"],
    "Latino Culture": ["Dance to Latin music", "Cook together", "Attend cultural festivals"],
    
    # Humor
    "Internet Culture": ["Share viral content", "Discuss internet trends", "Create content together"],
    "Dark Humor": ["Share memes", "Roast each other", "Watch dark comedy together"],
    
    # Wellness
    "Mental Health": ["Support each other", "Share resources", "Practice self-care together"],
    "Positivity & Quotes": ["Share inspiring content", "Motivate each other", "Practice gratitude together"],
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
