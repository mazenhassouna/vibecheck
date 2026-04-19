# ✨ Vibecheck

**Find what you have in common with someone based on your Instagram data.**

Vibecheck analyzes Instagram data exports from two people and uses AI to identify shared interests, from specific entities (like favorite artists or teams) to broader categories (like music or sports).

![Vibecheck Demo](https://via.placeholder.com/800x400?text=Vibecheck+Demo)

## 🚀 Features

- **Two-Stage AI Analysis**: Uses Google Gemini to create weighted interest profiles and find meaningful connections
- **Smart Filtering**: Only considers accounts with 5,000+ followers (filters out personal friends)
- **Rich Context**: Scrapes Instagram profiles and reels for additional context
- **Weighted Scoring**: Assigns importance based on engagement intensity (saves > likes > following)
- **Beautiful UI**: Modern, responsive interface for easy data upload and results viewing

## 📋 Prerequisites

- **Python 3.10, 3.11, or 3.12** (Python 3.13+ not yet supported due to pydantic-core compatibility)
- A Google Gemini API key (free tier available)
- An Apify API key (free tier with $5 credit)

## 🔧 Setup

### 1. Clone and Install

```bash
cd vibecheck

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
```

#### Getting API Keys

**Google Gemini (Free)**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file

**Apify (Free $5 credit)**
1. Create an account at [Apify](https://apify.com/)
2. Go to [Settings > Integrations](https://console.apify.com/account/integrations)
3. Copy your API token to your `.env` file

### 3. Run the Server

```bash
cd backend
python main.py
```

Open http://localhost:8000 in your browser.

## 📱 How to Get Your Instagram Data

Each person needs to download their Instagram data from Meta:

1. Go to [Instagram Data Download](https://accountscenter.instagram.com/info_and_permissions/dyi/)
2. Select "Download or transfer information"
3. Choose "Some of your information"
4. Select at least:
   - **Followers and following** → Following
   - **Your activity** → Likes, Saved, Comments
5. Choose **JSON** format (important!)
6. Submit request and wait for download (usually 1-2 days)
7. You'll receive a ZIP file - upload it directly to Vibecheck!

## 🎯 Usage

1. Open http://localhost:8000
2. Upload Person A's Instagram data ZIP file
3. Upload Person B's Instagram data ZIP file
4. Click "Analyze Compatibility"
5. View your vibe score and shared interests!

### Quick Mode

Check "Quick mode" to skip Instagram profile enrichment. This is faster but provides less detailed analysis.

## 📊 How Scoring Works

### Two-Stage Analysis

**Stage 1: Interest Taxonomy (Per User)**
- AI analyzes all accounts they follow, posts they've liked/saved, and comments
- Creates a weighted interest profile with specific entities and categories
- Assigns weights from 1-10 based on engagement intensity

**Stage 2: Comparison**
- Finds exact entity matches (both follow @travisscott)
- Finds category matches (both into basketball, different teams)
- Finds broad category overlaps (both into sports)
- Generates vibe score and narrative

### Vibe Score Tiers

| Score | Tier | Description |
|-------|------|-------------|
| 90-100 | 🔥 Soulmates | Practically the same person |
| 75-89 | 💜 Best Friends Energy | Strong alignment across interests |
| 60-74 | 🤝 Solid Match | Clear common ground |
| 45-59 | 🌱 Some Overlap | A few shared interests |
| 30-44 | 🔍 Room to Explore | Minimal overlap, could discover new things |
| 0-29 | 🌍 Different Worlds | Very different interests |

## 🛠 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend |
| `/health` | GET | Health check |
| `/api/parse` | POST | Parse single JSON file |
| `/api/parse-multiple` | POST | Parse multiple JSON files |
| `/api/analyze` | POST | Full analysis pipeline |
| `/api/analyze-json` | POST | Analyze pre-parsed JSON data |

## 📁 Project Structure

```
vibecheck/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── parser.py            # Instagram JSON parser
│   ├── apify_client.py      # Apify integration
│   ├── llm_analyzer.py      # Two-stage LLM analysis
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main UI
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

## 💰 Cost Estimate

| Service | Free Tier | Estimated Cost per Analysis |
|---------|-----------|----------------------------|
| Google Gemini | 1M tokens/day | Free |
| Apify Profile Scraper | $5 credit | ~$1-2 |
| Apify Reel Scraper | Included | ~$0.50-1 |
| **Total** | | **$1.50-3** (or free with Quick Mode) |

## 🔒 Privacy

- Your data is processed locally and never stored on any server
- API keys are stored only in your local `.env` file
- Instagram data is only used for analysis and not retained

## 🐛 Troubleshooting

### "GEMINI_API_KEY is required"
Make sure you've created a `.env` file with your API key.

### "APIFY_API_KEY is required"
Add your Apify API key to the `.env` file, or enable "Quick mode" to skip scraping.

### "Invalid JSON file"
Make sure you selected JSON format when downloading your Instagram data, not HTML.

### Analysis is slow
The full analysis with scraping can take 2-5 minutes. Use "Quick mode" for faster results.

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss changes.
