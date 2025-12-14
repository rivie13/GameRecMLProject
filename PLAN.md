# Steam Game Recommendation System - Implementation Plan

## 📋 Project Overview
Build a machine learning system that recommends Steam games based on your gaming library, playtime data, and game metadata from Steam's public APIs.

**Goal**: Keep it simple, focused, and deployable for others to use.

**Approach**: 100% API-based, no scraping, no ToS violations.

---

## 🎯 Phase 1: Foundation (MVP - Core Recommendation System)

### 1.1 Data Collection (Confirmed Working APIs ✅)
**User Data** (Steam Web API - requires API key):
- [ ] Set up Steam API integration
- [ ] Collect user's owned games library (`GetOwnedGames`)
- [ ] Get playtime data (total hours per game)
- [ ] Get recently played games (last 2 weeks)

**Game Catalog** (No API key needed):
- [ ] Get list of all Steam games (~50-70k games)
  - Use SteamSpy API: `https://steamspy.com/api.php`
  - Or use community-maintained dataset
- [ ] Fetch game metadata for each game (Store API):
  - Name, description
  - Genres & categories
  - Developers/publishers
  - Release date, price
  - Metacritic score
- [ ] Get review sentiment per game:
  - API: `https://store.steampowered.com/appreviews/{appid}?json=1`
  - Returns: "Overwhelmingly Positive", "Mostly Positive", "Mixed", etc.
  - Total positive/negative counts

**Status**: All APIs confirmed working (tested Dec 2025)

### 1.2 Data Analysis & Exploration
- [ ] Load user's library with playtime
- [ ] Identify engagement levels:
  - **Loved**: 50+ hours
  - **Played**: 5-50 hours
  - **Tried**: 0-5 hours
  - **Unplayed**: 0 hours
- [ ] Analyze user's top games (loved category)
- [ ] Extract preference patterns:
  - Most-played genres
  - Preferred categories (single-player, multiplayer, etc.)
  - Review sentiment preferences (do they like highly-rated games?)
  - Release date preferences (new vs old games)
- [ ] Visualize gaming profile in Jupyter notebook

**Approach**: Use Jupyter notebook for exploratory analysis

### 1.3 Build Recommendation Model (MVP)
**Algorithm**: Content-based filtering with weighted similarity scoring

**Features to use**:
1. **Playtime** (implicit preference signal)
   - 50+ hours = strong like
   - 5-50 hours = moderate like
   - 0-5 hours = weak signal

2. **Game metadata** (from Store API):
   - Genres (Action, RPG, Strategy, etc.)
   - Categories (Single-player, Multiplayer, Co-op, etc.)
   - Review sentiment (Positive/Mixed/Negative)
   - Metacritic score
   - Release year

**Recommendation logic**:
1. Identify user's "loved" games (50+ hours played)
2. Extract features from loved games (genres, categories, sentiment)
3. Calculate user preference vector:
   - Weighted genre scores
   - Weighted category scores
   - Average review sentiment preference
4. For each game in catalog (that user doesn't own):
   - Calculate similarity to user's loved games
   - Weight by: Genre match (30%), Category match (20%), Review sentiment (20%), Metacritic (20%), Recency (10%)
5. Rank games by similarity score
6. Return top 10-20 recommendations

**Output**: 
- Top 10 recommended games
- Similarity scores
- Reason for recommendation (matched genres/categories)

---

## 🎯 Phase 2: Enhanced Model (Better Recommendations)

### 2.1 Advanced Features
- [ ] **Add user tags** (optional - from SteamSpy):
  - Tags like "FPS", "Zombies", "Open World", "Horror"
  - Analyze tag preferences from loved games
  - Include tag similarity in scoring
  
- [ ] **Text analysis on descriptions**:
  - Use TF-IDF on game descriptions
  - Find semantic similarity between games
  - Supplement genre/category matching

- [ ] **Price-aware recommendations**:
  - Analyze user's typical price range
  - Filter/prioritize based on budget
  - Highlight games on sale

- [ ] **Developer/publisher preferences**:
  - Track favorite developers
  - Recommend other games by same developers

### 2.2 Improved Similarity Algorithm
- [ ] **Multi-vector similarity**:
  - Genre vector (one-hot encoded)
  - Category vector (one-hot encoded)
  - Tag vector (if using tags)
  - Description vector (TF-IDF)
  - Combine using weighted cosine similarity

- [ ] **Playtime-weighted preferences**:
  - More weight to games with 100+ hours
  - Less weight to games with 5-10 hours
  - Ignore games with <2 hours (maybe didn't like)

- [ ] **Review quality filter**:
  - Prioritize games with positive sentiment
  - Consider review count (popularity indicator)
  - Balance between "hidden gems" and popular titles

### 2.3 Collaborative Filtering (Multi-User Phase)
**If we expand to multiple users**:
- [ ] Collect anonymous playtime patterns from multiple users
- [ ] Build user-item matrix (users × games)
- [ ] Apply matrix factorization (ALS or SVD)
- [ ] Generate "users like you also enjoyed..." recommendations
- [ ] Hybrid: Combine content-based + collaborative

**Libraries to use**:
- scikit-learn (content-based, TF-IDF)
- Surprise (collaborative filtering)
- Implicit (implicit feedback models)

---

## 🎯 Phase 3: Web Application (Make it Accessible)

### 3.1 Backend API
**Framework**: Flask (lightweight, easy to deploy)

**Endpoints**:
- `POST /api/analyze` - Upload Steam data or provide Steam ID
- `GET /api/recommendations` - Get personalized recommendations
- `GET /api/profile` - View gaming profile analysis

### 3.2 Frontend (Simple Web Interface)
**Tech**: HTML + CSS + JavaScript (vanilla or lightweight framework)

**Features**:
- Input Steam ID or API key
- Display gaming profile stats
- Show recommended games with:
  - Game cover images
  - Why it's recommended
  - Steam store links
  - Price information

### 3.3 Deployment Options
**Simple deployment paths**:
1. **Streamlit** (fastest): Python-only, auto-generates UI
2. **Flask + Simple HTML**: More control, still easy
3. **Heroku/Railway/Render**: Free tier hosting

**Recommendation**: Start with Streamlit for quick prototype.

---

## 🎯 Phase 4: Multi-User Support (Scale for Others)

### 4.1 Database Setup
- [ ] Add user accounts (optional - can just use Steam ID)
- [ ] Cache API responses (avoid rate limits)
- [ ] Store processed recommendations

**Database**: SQLite (simple) or PostgreSQL (if scaling)

### 4.2 Features
- [ ] User authentication (optional)
- [ ] Periodic data refresh
- [ ] Save favorite recommendations
- [ ] Compare gaming profiles with friends

---

## 📊 Implementation Timeline

### Week 1-2: Core ML System
- Set up data collection with your Steam account
- Run data analysis and exploration
- Build and test basic recommendation model
- Validate recommendations make sense

### Week 3: Web Application
- Create Flask API
- Build simple frontend (or use Streamlit)
- Local testing and refinement

### Week 4: Deployment
- Choose hosting platform
- Deploy application
- Add documentation for others to use
- Test with your Steam account

---

## 🛠️ Technical Stack Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| Data Collection | Python + requests | Steam API access |
| Data Processing | pandas, numpy | Data manipulation |
| ML Model | scikit-learn | Simple, reliable |
| Visualization | matplotlib, seaborn | Data exploration |
| Web Framework | Flask or Streamlit | Lightweight deployment |
| Deployment | Render/Railway | Free tier available |

---

## 🎮 Success Criteria

**MVP (Minimum Viable Product)**:
- ✅ Collects your Steam library data
- ✅ Analyzes your gaming preferences
- ✅ Generates 10 personalized recommendations
- ✅ Recommendations actually match your taste

**Full Version**:
- ✅ Web interface anyone can use
- ✅ Enter Steam ID and get recommendations
- ✅ Nice visual presentation
- ✅ Deployed and accessible online

---

## 🚀 Next Steps

1. **Review this plan** - Adjust based on your preferences
2. **Set up Steam API** - Get your API key and Steam ID
3. **Run data collection** - Test with your account
4. **Start with Phase 1** - Build MVP recommendation system
5. **Iterate based on results** - Refine model as needed

---

## 📝 Notes & Considerations

**✅ What We CAN Do** (Confirmed with APIs):
- Get user's complete game library + playtime
- Get ALL Steam games catalog (~50-70k games)
- Get comprehensive game metadata (genres, categories, descriptions)
- Get review sentiment (Positive/Mixed/Negative) and scores
- Get Metacritic scores, release dates, prices
- NO API KEY needed for game metadata (public Store API)

**⚠️ Limitations**:
- **User reviews**: No API for user-written reviews (would need scraping - NOT doing this)
- **Wishlist**: API deprecated as of Nov 2024 (unreliable)
- **Rate limits**: Steam API has rate limits, need to cache responses
- **Private profiles**: User must have public profile for GetOwnedGames to work

**🔮 Future Enhancements**:
- Add SteamSpy tags for better classification
- Price tracking and sale notifications
- Integration with other platforms (Epic, GOG)
- Social features (compare with friends)
- Game bundle recommendations
- "Games you might have missed" feature

**🎯 Keep it Simple Philosophy**:
- Start with playtime + genres + categories
- Add tags/descriptions if needed for better accuracy
- Focus on accuracy over complexity
- Deploy MVP early, iterate based on real usage
- No scraping, no ToS violations, all legal APIs

---

## 🚀 READY TO BUILD!

### ✅ Research Complete
All APIs tested and confirmed working (December 2025):
- ✅ Steam Web API (GetOwnedGames)
- ✅ Store API (appdetails) - game metadata
- ✅ Store API (appreviews) - review sentiment
- ✅ SteamSpy API - game catalog & tags (optional)

### 📊 Data Sources Confirmed
1. **User data**: Library + playtime (Steam Web API)
2. **Game catalog**: ~50-70k games (SteamSpy or community dataset)
3. **Game metadata**: Genres, categories, descriptions (Store API)
4. **Review sentiment**: Positive/Mixed/Negative + scores (Store API)
5. **Optional tags**: User tags from SteamSpy

### 🎯 Next Implementation Steps

**Step 1: Refactor data_collection.py**
- Update to use confirmed APIs
- Add Store API calls for game metadata
- Add review sentiment fetching
- Add caching to avoid rate limits

**Step 2: Build initial model in Jupyter**
- Load user's library
- Fetch metadata for top games
- Build similarity scoring algorithm
- Test recommendations manually

**Step 3: Create simple Flask app**
- Input: Steam ID
- Process: Fetch data + generate recommendations
- Output: Top 10 recommended games

**Step 4: Deploy MVP**
- Choose hosting (Render/Railway)
- Deploy and test with real users
- Iterate based on feedback

---

## ❓ Decisions Still Needed

1. **Recommendation focus**: 
   - Similar to favorites (safe picks)?
   - Discover new genres (more adventurous)?
   - **Suggested**: Start with similar, add "discovery mode" later

2. **Tag usage**:
   - Include SteamSpy tags? (better accuracy, more API calls)
   - Just use genres/categories? (simpler, faster)
   - **Suggested**: Start without tags, add if accuracy isn't good enough

3. **Caching strategy**:
   - Cache game metadata locally (SQLite)?
   - Fresh API calls each time?
   - **Suggested**: Cache metadata, refresh weekly

4. **Web framework**:
   - Streamlit (fastest, auto-UI)?
   - Flask (more control)?
   - **Suggested**: Streamlit for MVP, migrate to Flask if needed

---

**Ready to proceed? Let me know and I'll start refactoring the code!**
