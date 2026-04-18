# 📱 Instagram Compatibility - Vibe Check

A privacy-first web application that analyzes Instagram data exports to find compatibility and shared interests between two people. Perfect for breaking the ice without oversharing!

## 🎯 Features

- **Privacy-First**: Only analyzes 5 specific data categories (likes, saved, comments, following, topics)
- **Configurable Scoring**: Easily adjustable weights and bonus system
- **AI-Enhanced**: Uses Google Gemini for conversation starters and semantic analysis
- **Beautiful UI**: Modern, responsive design with Instagram-inspired gradients
- **Session-Based**: Share a code with your friend to match

## 🔒 Privacy

We take privacy seriously. The app **ONLY** processes:

| ✅ Allowed | ❌ Never Accessed |
|-----------|-------------------|
| Likes | Messages/DMs |
| Saved Posts | Search History |
| Comments (style only) | Personal Info |
| Following | Login Activity |
| Topics | Story Interactions |

Data is processed in memory and deleted immediately after analysis.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  - Session management (create/join)                         │
│  - ZIP file upload with privacy disclosure                  │
│  - Results visualization                                    │
├─────────────────────────────────────────────────────────────┤
│                     BACKEND (FastAPI)                       │
│  - Session management API                                   │
│  - Instagram data parser (privacy allowlist)                │
│  - Compatibility analyzer (Jaccard similarity)              │
│  - Gemini AI integration (conversation starters)            │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Scoring Algorithm

```
COMPATIBILITY_SCORE = 
    0.25 × Likes_Score +
    0.25 × Saved_Score +
    0.25 × Following_Score +
    0.15 × Topics_Score +
    0.10 × Comments_Style_Score +
    Bonus_Points (max 15)
```

### Weights (configurable in `backend/scoring_config.py`)

| Category | Weight | Method |
|----------|--------|--------|
| Likes | 25% | Jaccard similarity of liked accounts |
| Saved | 25% | Jaccard similarity of saved content |
| Following | 25% | Direct overlap + category similarity |
| Topics | 15% | Jaccard similarity of Instagram topics |
| Comments | 10% | Engagement style comparison |

### Bonus Points

- **+3** per shared niche account (following)
- **+2** per exact same saved post
- **+5** if top 3 topics match
- **Max bonus**: 15 points

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google AI Studio API key (for Gemini features)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable (optional, for Gemini features)
export GEMINI_API_KEY="your-api-key-here"

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
hackmsa/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── parser.py            # Instagram data parser
│   ├── analyzer.py          # Compatibility analyzer
│   ├── gemini_client.py     # Gemini AI integration
│   ├── scoring_config.py    # Configurable weights
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── api.js           # API client
│   │   └── components/
│   │       ├── HomePage.jsx      # Create/join session
│   │       ├── UploadPage.jsx    # File upload + privacy info
│   │       ├── WaitingRoom.jsx   # Waiting for partner
│   │       └── ResultsPage.jsx   # Compatibility results
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/privacy-info` | Get privacy information |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{code}` | Get session status |
| POST | `/api/sessions/{code}/upload` | Upload Instagram data |
| GET | `/api/sessions/{code}/result` | Get compatibility result |
| DELETE | `/api/sessions/{code}` | Delete session |

## 📱 How to Get Instagram Data

1. Open Instagram app → Settings
2. Tap "Accounts Center" → "Your information and permissions"
3. Tap "Download your information"
4. Select your Instagram account
5. Choose "Download or transfer information" → "Some of your information"
6. Select: Followers, Following, Likes, Saved, Comments, Topics
7. Choose JSON format
8. Download the ZIP file

## 🎨 Customization

### Adjust Scoring Weights

Edit `backend/scoring_config.py`:

```python
SCORING_CONFIG = {
    "weights": {
        "likes": 0.25,       # Adjust these values
        "saved": 0.25,       # Must sum to 1.0
        "following": 0.25,
        "topics": 0.15,
        "comments": 0.10,
    },
    "bonuses": {
        "same_niche_account": 3,    # Points per shared account
        "same_exact_saved_post": 2, # Points per exact match
        "same_top_topics": 5,       # If top topics match
    },
    "max_bonus": 15,
}
```

### Add More Data Categories

1. Add file patterns to `ALLOWED_FILES` in `scoring_config.py`
2. Add extraction method in `parser.py`
3. Add scoring method in `analyzer.py`
4. Update weights (must sum to 1.0)

## 🛡️ Security Considerations

- Data is processed in memory only
- Sessions expire after 24 hours
- File size limited to 50MB
- Only allowlisted JSON files are parsed
- No personal information is stored

## 📄 License

MIT License - feel free to use for your hackathon!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🐛 Known Limitations

- Instagram export format may vary; parser handles common formats
- Gemini API requires internet connection
- In-memory sessions don't persist across server restarts

---

Built with ❤️ for HackMSA
