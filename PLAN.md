# Steam Game Recommendation System - Implementation Plan

## 📋 Project Overview
Build a **hybrid ML + content-based recommendation system** that recommends Steam games based on your gaming library, playtime data, and game metadata from Steam's public APIs.

**Current Status**: Content-based system ✅ working | ML layer 🚧 in development

**Goal**: 
- **Phase 1**: Single-user hybrid system (ML + content-based + user preferences)
- **Phase 2**: Deploy web app for multi-user data collection
- **Phase 3**: Add collaborative filtering once we have 100+ users

**Approach**: 100% API-based, no scraping, no ToS violations.

---

## 🏗️ System Architecture (Current Design)

### **Hybrid Recommendation Pipeline**

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: UNIVERSAL FILTERS (Quality & Appropriateness)     │
│ Applied to ALL candidates before any scoring               │
├─────────────────────────────────────────────────────────────┤
│ ✓ NSFW filter (sfw_only=True)                              │
│ ✓ Early Access filter (exclude_early_access=True)          │
│ ✓ Minimum review count (min_reviews=5000)                  │
│ ✓ Minimum review score (min_review_score=70%)              │
│ ✓ Meta genre filter (exclude Utilities, Software, etc.)    │
│ ✓ Already owned games (exclude from recommendations)       │
│                                                             │
│ Result: ~10k filtered candidates (from 80k+ catalog)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: ML PREDICTION (Tag-Weighted Learning)             │
│ Learns patterns from YOUR playtime behavior                │
├─────────────────────────────────────────────────────────────┤
│ Training:                                                   │
│   • Features: Tag vote vectors, genre overlap, etc.        │
│   • Target: Your engagement_score (0-1)                    │
│   • Model: Random Forest / XGBoost                         │
│   • Trained on: ALL your owned games (no filtering)        │
│                                                             │
│ Prediction:                                                 │
│   • Predicts: "Will user play this 50+ hours?"            │
│   • Score: 0-1 (engagement probability)                    │
│   • Weight: 35% of final score                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: CONTENT-BASED SCORING (Similarity Matching)       │
│ Matches games to your "loved" games profile                │
├─────────────────────────────────────────────────────────────┤
│ • Tag matching (45%): Weighted by your playtime           │
│ • Genre matching (20%): Broad category preferences         │
│ • Median playtime (20%): Community engagement signal       │
│ • Review quality (15%): Community sentiment                │
│   • Weight: 35% of final score                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: PREFERENCE ADJUSTMENTS (User Overrides)           │
│ Soft boosts/penalties based on explicit preferences        │
├─────────────────────────────────────────────────────────────┤
│ • Boost preferred genres/tags (0 to +20 points)          │
│ • Penalize disliked genres/tags (0 to -20 points)        │
│ • User can adjust these values individually to fine-tune │
│ • Weight: 20% of final score                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: COMBINE & RANK                                    │
│ Final Score = weighted sum of all components               │
├─────────────────────────────────────────────────────────────┤
│ final_score = 0.35*ML + 0.35*Content + 0.20*Prefs + 0.10*Reviews
│                                                             │
│ Sort by final_score descending → Top N candidates          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 6: HARD EXCLUSIONS (Last Filter - User Constraints)  │
│ Applied AFTER scoring - these are absolute no-gos          │
├─────────────────────────────────────────────────────────────┤
│ • hard_exclude_genres: ['Sports', 'Racing']                │
│ • hard_exclude_tags: ['Horror', 'Survival Horror']         │
│                                                             │
│ These OVERRIDE all scores - even if ML/Content say "yes"   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                  TOP 20 RECOMMENDATIONS
```

### **Why This Order?**

**Universal Filters (Stage 1) - EARLY:**
- ✅ **Efficiency**: Don't score 80k games, score 10k filtered games
- ✅ **Objective quality gates**: NSFW, Early Access, review minimums
- ✅ **Not learned preferences**: These are universal appropriateness checks
- ✅ **Clean training data**: Ensures ML sees representative candidates

**ML + Content Scoring (Stages 2-3) - MIDDLE:**
- ✅ **Learn from clean data**: ML predicts engagement on quality candidates
- ✅ **Content matches taste**: Genre/tag similarity to loved games
- ✅ **Both inform each other**: ML might find non-obvious patterns

**User Preferences (Stage 4) - BEFORE FINAL RANKING:**
- ✅ **Nuanced adjustments**: Boost certain genres/tags, penalize certain genres/tags
- ✅ **Soft signals**: Influence ranking without eliminating
- ✅ **Tunable by user**: Can adjust weights to preference

**Hard Exclusions (Stage 6) - LAST:**
- ✅ **Absolute constraints**: "Never show me Horror games, period"
- ✅ **Override ML**: Even if ML predicts 95% engagement, exclude it
- ✅ **Preserve scoring**: Can see what WOULD have been recommended
- ✅ **User control**: Final say in what they want to see

---

## 🎯 Phase 1: Foundation (MVP - Core Recommendation System)

### 1.1 Data Collection (Confirmed Working APIs ✅)
**User Data** (Steam Web API - requires API key):
- [x] Set up Steam API integration
- [x] Collect user's owned games library (`GetOwnedGames`)
- [x] Get playtime data (total hours per game)
- [ ] Get recently played games (last 2 weeks)

**Game Catalog** (No API key needed):
- [x] Get list of all Steam games (~50-70k games)
  - Use SteamSpy API: `https://steamspy.com/api.php`
  - Or use community-maintained dataset
- [x] Fetch game metadata for each game (Store API):
  - Name, description
  - Genres & categories
  - Developers/publishers
  - Release date, price
  - Metacritic score
- [x] Get review sentiment per game:
  - API: `https://store.steampowered.com/appreviews/{appid}?json=1`
  - Returns: "Overwhelmingly Positive", "Mostly Positive", "Mixed", etc.
  - Total positive/negative counts

**Status**: All APIs confirmed working (tested Dec 2025)

### 1.2 Data Analysis & Exploration
- [x] Load user's library with playtime
- [x] Identify engagement levels:
  - **Loved**: 50+ hours
  - **Played**: 5-50 hours
  - **Tried**: 0-5 hours
  - **Unplayed**: 0 hours
- [x] Analyze user's top games (loved category)
- [x] Extract preference patterns:
  - Most-played genres
  - Preferred categories (single-player, multiplayer, etc.)
  - Review sentiment preferences (do they like highly-rated games?)
  - Release date preferences (new vs old games)
- [x] Visualize gaming profile in Jupyter notebook

**Approach**: Use Jupyter notebook for exploratory analysis

### 1.3 Build Recommendation Model - CURRENT STATUS ✅

**Current Implementation**: Hybrid Content-Based + Tag-Weighted System

**What's Working Now**:
- [x] Content-based filtering using genres and tags
- [x] Tag-weighted user profile (playtime * tag votes)
- [x] Multi-stage filtering pipeline (see architecture diagram above)
- [x] Soft exclusions (penalties for disliked tags/genres)
- [x] Hard exclusions (absolute filters for unwanted content)
- [x] Diagnostic tools to debug recommendations

**Content-Based Scoring** (35% weight):
1. **Tag Matching (45%)**: Weighted by user's playtime on each tag
   - Uses SteamSpy community tags + vote counts
   - Example: If you played 300h of "Open World" games, that tag gets high weight
   - Filters out NSFW tags and meta tags (Indie, Casual, etc.)

2. **Genre Matching (20%)**: Broad category preferences
   - Action, RPG, Strategy, etc.
   - Weighted by playtime in each genre

3. **Median Playtime (20%)**: How long players actually engage
   - Games with 50+ hour median = deep, engaging games
   - Signals quality beyond just reviews

4. **Review Quality (15%)**: Community rating + volume
   - Positive percentage + logarithmic volume boost
   - Prevents popularity bias (not 50% of score)

**Next: Add ML Layer** 🚧 (see Phase 2 below)

**Output**: 
- Top 20 recommended games
- Match scores with explanations
- Price, reviews, developer info
- Steam store links

---

## 🎯 Phase 2: Machine Learning Layer (IN PROGRESS 🚧)

### 2.1 Tag-Weighted ML System (Current Goal)
**Objective**: Let ML learn patterns from YOUR playtime that might not be obvious

**Implementation Plan** (Weeks 1-2):

#### **Week 1: Feature Engineering & Model Training**
- [ ] **Extract tag features from owned games**:
  - Tag vote counts (e.g., {"FPS": 12000, "Open World": 8000})
  - Your playtime weights (e.g., {"FPS": 500h, "Open World": 300h})
  - Interaction features: tag_vote × user_playtime_weight
  - Genre overlap scores
  - Review quality metrics
  
- [ ] **Prepare training data**:
  - X = Feature vectors for each owned game
  - y = Engagement score (0-1) OR playtime category (0-3)
  - Train/test split: 80/20
  - NO filtering of training data - use ALL owned games

- [ ] **Train ML model**:
  - Start with Random Forest Regressor
  - Try XGBoost if Random Forest underperforms
  - Hyperparameter tuning with cross-validation
  - Feature importance analysis

- [ ] **Evaluation metrics**:
  - RMSE (Root Mean Square Error) for engagement prediction
  - Accuracy for category prediction (loved/played/tried)
  - Precision@K (of top 20 recommendations, how many are relevant?)
  - Compare ML vs. Content-Based vs. Hybrid

#### **Week 2: Integration & Hybrid System**
- [ ] **Integrate ML into recommendation pipeline**:
  - Add ML prediction layer (Stage 2 in architecture)
  - Normalize ML scores to 0-1 range
  - Combine with content-based scores:
    - `final_score = 0.35*ML + 0.35*Content + 0.20*Prefs + 0.10*Reviews`

- [ ] **A/B Testing Framework**:
  - Generate recommendations with 3 approaches:
    - Pure content-based (current system)
    - Pure ML
    - Hybrid (combined)
  - Compare results manually
  - Tune weights based on what works best

- [ ] **Validation**:
  - Test on held-out games (games you own but didn't train on)
  - Can the model predict which games you played 50+ hours?
  - Does hybrid beat content-based alone?

**Expected Outcome**:
- ML model that predicts engagement score with 70-80% accuracy
- Hybrid system that gives better recommendations than content-based alone
- Feature importance analysis showing what patterns ML found

---

### 2.2 User Preference System (Future Enhancement)
Once ML is working, add explicit user preferences:

- [ ] **Preference configuration**:
  ```python
  user_preferences = {
      # Soft boosts/penalties (adjust scores)
      'boost_genres': {'Action': +10, 'RPG': +15},
      'boost_tags': {'Open World': +20, 'Multiplayer': +15},
      'penalty_genres': {'Strategy': -15, 'Turn-Based': -20},
      'penalty_tags': {'2D Platformer': -10, 'Pixel Graphics': -10},
      
      # Hard exclusions (applied LAST, absolute filters)
      'hard_exclude_genres': ['Sports', 'Racing'],
      'hard_exclude_tags': ['Horror', 'Survival Horror'],
      
      # Tunable weights (how much each layer matters)
      'weights': {
          'ml': 0.35,
          'content': 0.35,
          'preferences': 0.20,
          'reviews': 0.10
      }
  }
  ```

- [ ] **Implement preference scoring layer** (Stage 4)
- [ ] **Add UI for preference management** (when building web app)
- [ ] **Allow users to tune weights** (advanced mode)

---

### 2.3 Future: Collaborative Filtering (Phase 3 - Multi-User)
**Only after deploying web app and collecting 100+ users**:

- [ ] **User-User Collaborative Filtering**:
  - Find users with similar playtime patterns
  - Recommend games they loved that you haven't played

- [ ] **Matrix Factorization**:
  - Build user-item matrix (users × games)
  - Apply ALS or SVD to find latent features
  - Predict missing ratings

- [ ] **Neural Collaborative Filtering** (optional):
  - Deep learning for user/game embeddings
  - More complex patterns than matrix factorization

- [ ] **Final Hybrid System**:
  ```
  final_score = 0.25*ML + 0.25*Content + 0.25*Collaborative + 0.15*Prefs + 0.10*Reviews
  ```

**Libraries to use**:
- scikit-learn (Random Forest, preprocessing)
- XGBoost (gradient boosting)
- Surprise (collaborative filtering)
- Implicit (implicit feedback models)
- TensorFlow/PyTorch (neural CF - optional)

---

## 🎯 Phase 3: Web Application (Weeks 3-6)

**Goal**: Deploy MVP to collect multi-user data for collaborative filtering

### 3.1 Backend API (Week 3-4)
**Framework**: Flask or FastAPI

**Core Endpoints**:
- `POST /api/auth/steam` - Steam OAuth login
- `GET /api/profile/{steam_id}` - User's gaming profile
- `GET /api/recommendations/{steam_id}` - Get personalized recommendations
  - Query params: `?n=20&min_reviews=5000&sfw_only=true`
- `POST /api/feedback` - User feedback (clicked/dismissed/wishlisted)
- `GET /api/stats` - System stats (total users, games analyzed, etc.)

**Database Schema** (PostgreSQL or SQLite):
```sql
users (steam_id, username, created_at, last_sync)
user_games (user_id, appid, playtime_hours, playtime_category, last_played)
recommendations (user_id, appid, score, method, created_at)
feedback (user_id, appid, action, timestamp)  -- CRITICAL for learning!
```

**Key Features**:
- Steam OAuth authentication (users log in with Steam)
- Automatic library sync via Steam API
- Background job to refresh user data periodically
- Cache recommendations (refresh daily)
- Track user feedback (clicks, wishlist adds, dismissals)

### 3.2 Frontend (Week 4-5)
**Tech Stack Options**:
1. **Streamlit** (fastest, Python-only) - Good for MVP
2. **React + Flask API** (more professional, scalable)
3. **Next.js** (full-stack, modern)

**Recommended**: Start with Streamlit, migrate to React if needed

**Core Pages**:
1. **Landing Page**:
   - "Login with Steam" button
   - Example recommendations
   - How it works

2. **Profile Page**:
   - Your gaming stats (playtime, top genres, top tags)
   - Loved games showcase
   - User preference settings

3. **Recommendations Page**:
   - Top 20 recommended games (with images)
   - Filter controls (genres, tags, price)
   - "Why recommended?" explanations
   - Quick actions: 👍 Interested / 👎 Not interested / ➕ Add to wishlist
   - Direct Steam store links

4. **Settings Page**:
   - Adjust recommendation weights
   - Set hard exclusions (Horror, Sports, etc.)
   - Set soft preferences (boost/penalty)
   - Privacy controls

### 3.3 Deployment (Week 5-6)
**Platform Options**:
1. **Railway.app** ⭐ (Recommended - easy, free tier)
2. **Render** (free tier, auto-deploy from GitHub)
3. **Heroku** (easy but paid now)
4. **AWS/Azure** (more control, more complex)

**Deployment Checklist**:
- [ ] Set up GitHub repo with CI/CD
- [ ] Configure environment variables (Steam API key, DB connection)
- [ ] Set up database (PostgreSQL on Railway/Render)
- [ ] Deploy backend API
- [ ] Deploy frontend (static hosting or same platform)
- [ ] Set up monitoring (error tracking, performance)
- [ ] Add analytics (user behavior, recommendation performance)

**MVP Success Criteria**:
- ✅ Users can log in with Steam
- ✅ System fetches their library automatically
- ✅ Recommendations generate in <5 seconds
- ✅ Users can provide feedback (like/dislike)
- ✅ Feedback is stored for future ML improvements

---

## 🎯 Phase 4: Multi-User Enhancements (After 100+ Users)

### 4.1 User Feedback Learning
- [ ] **Click-Through Rate (CTR) Prediction**:
  - Train model: Did user click on recommended game?
  - Features: User profile + game features + context
  - Improve ranking based on what users actually engage with

- [ ] **Reinforcement Learning** (optional):
  - Recommendations = actions
  - User engagement = rewards
  - Learn policy to maximize user satisfaction

### 4.2 Collaborative Filtering Layer
- [ ] **Build user-item matrix** from all users' playtime
- [ ] **Find similar users** based on playtime patterns
- [ ] **Recommend games** that similar users loved
- [ ] **Integrate into hybrid system**:
  ```
  final_score = 0.25*ML + 0.25*Content + 0.25*Collaborative + 0.15*Prefs + 0.10*Reviews
  ```

### 4.3 Social Features
- [ ] Compare your gaming profile with friends
- [ ] "Users like you also play..." section
- [ ] Gaming style badges (e.g., "RPG Enthusiast", "Indie Explorer")
- [ ] Share recommendations via link

### 4.4 Advanced Features
- [ ] Price tracking and sale notifications
- [ ] "Games you might have missed" (older hidden gems)
- [ ] Bundle recommendations (games that go well together)
- [ ] Integration with other platforms (Epic, GOG)

---

## 📊 Updated Implementation Timeline

### **Phase 1: Single-User ML System** (Weeks 1-2) ← YOU ARE HERE
- Week 1: Tag-weighted ML feature engineering + training
- Week 2: Hybrid system integration + evaluation
- **Goal**: Validate ML improves recommendations

### **Phase 2: Refinement** (Weeks 3-4)
- Add user preference system (soft boosts/penalties, hard exclusions)
- Build evaluation framework (compare content vs ML vs hybrid)
- Document findings and model performance
- **Goal**: Finalize single-user recommendation algorithm

### **Phase 3: Web Application MVP** (Weeks 5-8)
- Weeks 5-6: Backend API (Flask/FastAPI) + Database
- Weeks 7-8: Frontend UI (Streamlit or React)
- Week 8: Deploy to Railway/Render
- **Goal**: Launch publicly, start collecting user data

### **Phase 4: Multi-User ML** (Weeks 9-12)
- Gather 10-20 beta users (friends, Reddit, etc.)
- Collect feedback data (clicks, wishlists, dismissals)
- Implement collaborative filtering layer
- Tune hybrid system with multi-user data
- **Goal**: 100+ active users, collaborative filtering working

### **Phase 5: Scale & Polish** (Weeks 13+)
- Public launch (Reddit, Twitter, gaming forums)
- Performance optimization (caching, CDN)
- Advanced features (price tracking, social features)
- Mobile responsive design
- **Goal**: 1000+ users, production-ready system

---

## 🛠️ Technical Stack Summary

| Component | Current | Future (Multi-User) |
|-----------|---------|---------------------|
| **Data Collection** | Python + requests | Same + background jobs |
| **Data Processing** | pandas, numpy | Same + Apache Spark (if needed) |
| **ML - Content** | Custom algorithm | Same (optimized) |
| **ML - Single User** | Random Forest / XGBoost | Same |
| **ML - Multi User** | N/A | Matrix Factorization (Surprise) |
| **Visualization** | matplotlib, seaborn | Same + web charts |
| **Web Framework** | N/A | Flask/FastAPI |
| **Frontend** | N/A | Streamlit → React (later) |
| **Database** | CSV files | PostgreSQL |
| **Caching** | N/A | Redis |
| **Deployment** | Local | Railway / Render |
| **Monitoring** | N/A | Sentry + Analytics |

---

## 🎮 Success Criteria

**Phase 1 Complete (ML Working)**:
- ✅ ML model trained on your library (700+ games)
- ✅ Achieves 70%+ accuracy predicting engagement
- ✅ Hybrid system beats content-based alone
- ✅ Feature importance analysis complete
- ✅ Documented in Jupyter notebook

**Phase 2 Complete (System Polished)**:
- ✅ User preference system implemented
- ✅ Evaluation framework comparing all approaches
- ✅ Code refactored into clean modules
- ✅ Documentation written
- ✅ Ready for web deployment

**Phase 3 Complete (MVP Deployed)**:
- ✅ Web app live and publicly accessible
- ✅ Users can log in with Steam
- ✅ Recommendations generate automatically
- ✅ Feedback system capturing user actions
- ✅ 10-20 beta users testing

**Phase 4 Complete (Multi-User ML)**:
- ✅ 100+ active users
- ✅ Collaborative filtering layer working
- ✅ User feedback improving recommendations
- ✅ Performance optimized (<3 second load times)
- ✅ Mobile responsive

**Phase 5 Complete (Production Ready)**:
- ✅ 1000+ active users
- ✅ Sub-second recommendation generation
- ✅ A/B testing framework for algorithm improvements
- ✅ Blog post / case study written
- ✅ Strong portfolio piece for job applications

---

## 🚀 Immediate Next Steps (Week 1)

### **Day 1-2: Feature Engineering**
1. [ ] Create new notebook section for ML
2. [ ] Extract tag vote features from owned_games
3. [ ] Create interaction features (tag_vote × playtime_weight)
4. [ ] Prepare X (features) and y (engagement_score) matrices
5. [ ] Split into train/test sets (80/20)

### **Day 3-4: Model Training**
1. [ ] Train Random Forest Regressor
2. [ ] Evaluate with RMSE, MAE, R²
3. [ ] Analyze feature importance
4. [ ] Compare predictions to actual playtime
5. [ ] Tune hyperparameters if needed

### **Day 5-7: Integration & Testing**
1. [ ] Create `EngagementPredictor` class
2. [ ] Integrate into `HybridRecommender` system
3. [ ] Generate recommendations with ML layer
4. [ ] Compare: Content-only vs ML-only vs Hybrid
5. [ ] Document findings and performance metrics

**Goal for Week 1**: Have working ML model that beats content-based system

---

## 📝 Technical Notes & Design Decisions

### **Filter Order Rationale**

**Q: Should filters happen before or after ML scoring?**

**A: EARLY filtering is correct! Here's why:**

#### **Universal Filters (EARLY - Stage 1)**
These are applied **BEFORE any scoring**:
- ✅ **Efficiency**: Don't score 80k games, score 10k filtered candidates
- ✅ **Objective criteria**: NSFW, Early Access, minimum reviews are quality gates
- ✅ **Not preferences**: These aren't learned from data, they're universal appropriateness
- ✅ **Cleaner ML input**: ML sees realistic candidate pool, not noise

**Examples:**
```python
# Applied FIRST (reduce 80k → 10k candidates)
- sfw_only=True  # Filter NSFW
- exclude_early_access=True  # Filter unfinished games
- min_reviews=5000  # Quality threshold
- min_review_score=70%  # Positive reception
- exclude meta_genres  # Filter Utilities, Software (non-games)
```

#### **User-Specific Hard Exclusions (LATE - Stage 6)**
These are applied **AFTER all scoring**:
- ✅ **Personal constraints**: "I hate Horror" overrides even 95% ML prediction
- ✅ **Preserve scoring**: Can see what WOULD have been recommended
- ✅ **User control**: Final say in what appears in their feed
- ✅ **Debugging**: Can toggle exclusions to test recommendation quality

**Examples:**
```python
# Applied LAST (after scoring is complete)
hard_exclude_genres = ['Sports', 'Racing']  # Absolute no-gos, examples
hard_exclude_tags = ['Horror', 'Survival Horror']  # Never show me these, examples
```

#### **Why ML Trains on ALL Owned Games (No Filtering)**
**Training data**: Use ALL your owned games, even NSFW/Early Access
- ✅ **Unbiased learning**: ML sees your actual behavior patterns
- ✅ **Better generalization**: Learns what YOU like, not what filters allow
- ✅ **Separation of concerns**: ML learns patterns, filters enforce constraints

**Recommendation data**: Apply filters to catalog before scoring
- ✅ **Realistic candidates**: ML only scores games that pass quality gates
- ✅ **Computational efficiency**: Don't waste time scoring filtered-out games
- ✅ **Clean recommendations**: Users only see appropriate, quality games

---

## 📝 Limitations & Known Issues

**✅ What We Have**:
- [x] Complete Steam library data (700+ games, playtime)
- [x] Steam catalog with 81k+ games (genres, tags, reviews)
- [x] SteamSpy tags with vote counts (community-curated)
- [x] Working content-based system (tag-weighted)
- [x] Diagnostic tools to debug recommendations

**⚠️ Current Limitations**:
- **Single-user only**: No collaborative filtering yet (need 100+ users)
- **No user reviews text**: API doesn't provide review content (only counts)
- **Wishlist API deprecated**: Can't check user's wishlist automatically
- **Rate limits**: Steam API throttles requests (we cache to avoid)
- **Private profiles**: User must have public profile for data collection

**🚧 In Progress**:
- [ ] ML prediction layer (tag-weighted learning)
- [ ] User preference system (soft boosts/penalties)
- [ ] Evaluation metrics (precision@K, RMSE)
- [ ] Web application for deployment

**🔮 Future Enhancements** (after web deployment):
- Collaborative filtering (100+ users needed)
- Price tracking and sale notifications
- Integration with other platforms (Epic, GOG)
- Social features (compare profiles with friends)
- Game bundle recommendations
- "Hidden gems you missed" feature
- A/B testing framework for algorithm tuning

---

## 🎯 Design Philosophy

**Keep it Simple & Effective**:
- ✅ Start with data-driven approaches (playtime = ground truth)
- ✅ Use community tags (better than Steam's sparse genres)
- ✅ Validate each layer independently before combining
- ✅ Deploy early, iterate based on real user feedback
- ✅ No scraping, no ToS violations, all legal APIs
- ✅ Prioritize accuracy over fancy algorithms
- ✅ Make it explainable (users understand WHY a game was recommended)

**For Job Applications**:
- 📊 Real ML (supervised learning, feature engineering, evaluation)
- 🏗️ System design (multi-stage pipeline, filters, scoring)
- 🚀 Deployable (web app, database, user feedback loop)
- 📈 Scalable (ready for multi-user collaborative filtering)
- 📝 Well-documented (plan, notebook, code comments)

---

## 🚀 LET'S BUILD THE ML LAYER!


---

## ✅ Status: APIs & Data Collection COMPLETE

**Working Data Sources** (December 2025):
- ✅ Steam Web API (GetOwnedGames) - User library + playtime
- ✅ Store API (appdetails) - Game metadata (genres, developers, prices)
- ✅ Store API (appreviews) - Review counts and sentiment
- ✅ SteamSpy API - Complete catalog (81k+ games) + community tags with vote counts

**Current Dataset**:
- ✅ 60+ owned games with playtime categories
- ✅ 81k+ Steam catalog with genres, tags, reviews
- ✅ Tag vote counts (community-curated, better than Steam's genres)
- ✅ All data cached locally in CSV files

**Content-Based System** ✅ **COMPLETE**:
- ✅ Tag-weighted similarity scoring
- ✅ Multi-stage filtering pipeline
- ✅ Soft/hard exclusions
- ✅ Diagnostic tools
- ✅ Working recommendations in Jupyter notebook

---

## 🚧 Current Focus: Building ML Layer (Week 1-2)

**This Week**: 
- Implement tag-weighted ML prediction (Random Forest/XGBoost)
- Train on YOUR playtime patterns
- Evaluate against content-based system

**Next Week**: 
- Integrate hybrid system (ML + content-based + preferences)
- A/B test different approaches
- Finalize single-user recommendation algorithm

**After ML is Working**: 
- Build web application (Flask/Streamlit)
- Deploy for multi-user data collection
- Add collaborative filtering (100+ users)

---

## 🎯 Decisions Made

✅ **Recommendation focus**: Tag-weighted hybrid (content + ML + preferences)
✅ **Tag usage**: Using SteamSpy tags (proven to work well)
✅ **Caching**: All data cached locally in CSV, refresh on-demand
✅ **Filter order**: Universal filters → ML/Content scoring → User exclusions
✅ **Web framework**: Streamlit for MVP, migrate to Flask/React later

---

**Let's build the ML layer! 🚀**
