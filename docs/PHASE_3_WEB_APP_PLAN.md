# Phase 3: Web Application MVP - Detailed Plan

**Date**: December 18, 2025  
**Status**: 🚀 Ready to Begin Implementation

---

## 🎯 MVP Goals

Build a **single-page web application** that:
1. ✅ Allows users to log in with Steam
2. ✅ Shows their gaming profile with visualizations
3. ✅ Generates personalized recommendations
4. ✅ Explains HOW the system works (educational + transparent)
5. ✅ Collects user feedback for future improvements

**Key Philosophy**: Start small, make it work, then scale.

---

## 🏗️ Tech Stack

### Backend: FastAPI ✅
**Why FastAPI?**
- Modern, fast Python framework
- Automatic API documentation (Swagger UI)
- Async support for better performance
- Type hints and validation built-in
- Easy to integrate with ML models
- Great for MVP → Production path

### Frontend: React ✅
**Why React?**
- Modern, component-based UI
- Rich ecosystem for charts/visualizations
- Professional look and feel
- Easy to iterate and extend

**⚠️ CRITICAL Security: React Server Components RCE Vulnerability (CVE-2025-55182)**
**What it is**: Remote code execution vulnerability in React Server Components (RSC) discovered Dec 3, 2025. Rated CVSS 10.0 (Critical).

**Affected packages**:
- `react-server-dom-webpack`
- `react-server-dom-parcel`
- `react-server-dom-turbopack`
- Frameworks: Next.js, React Router (unstable RSC), Waku, Expo

**How we avoid it**:
1. ✅ **DO NOT use React Server Components** (no RSC features)
2. ✅ **DO NOT use Next.js** (uses RSC by default)
3. ✅ **Use Vite with client-side rendering ONLY** (no SSR, no RSC)
4. ✅ **Do not install any `react-server-dom-*` packages**
5. ✅ Keep React at latest stable (19.0.1+, 19.1.2+, or 19.2.1+)
6. ✅ Never use `eval()` or `dangerouslySetInnerHTML` with user data
7. ✅ Validate ALL user input on backend with Pydantic
8. ✅ Sanitize any dynamic content (use DOMPurify)
9. ✅ Run `npm audit` regularly to check for vulnerabilities

**Our stack is SAFE because**:
- ✅ Vite + React (client-side only) = No server components
- ✅ FastAPI backend handles all server logic
- ✅ No RSC packages in dependencies
- ✅ Clear separation: React renders UI, FastAPI serves data

### Database: PostgreSQL ✅
**Why PostgreSQL?**
- Production-ready relational database
- Great for structured data (users, games, recommendations)
- JSON support for flexible metadata
- Free tier available on most platforms
- Easy to scale

### Hosting: TBD (Railway/Render)
**Options** (evaluate later):
- **Railway**: Easy setup, PostgreSQL included, auto-deploy from GitHub
- **Render**: Similar to Railway, generous free tier
- **Fly.io**: Good for global distribution
- **Vercel** (frontend) + **Railway** (backend) split deployment

**For now**: Focus on local development, deployment comes later.

---

## 📐 Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Landing Page │  │ Profile Page │  │ Recs Page    │    │
│  │              │  │              │  │              │    │
│  │ - Login btn  │  │ - Stats viz  │  │ - Top 20     │    │
│  │ - How it     │  │ - Tag cloud  │  │ - Filters    │    │
│  │   works      │  │ - Genre dist │  │ - Explain    │    │
│  │ - Features   │  │ - Timeline   │  │ - Feedback   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          ├──────────────────┴──────────────────┘
          │           REST API (HTTPS)
          │
┌─────────▼───────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Auth Routes  │  │ Profile      │  │ Recs Engine  │    │
│  │              │  │ Routes       │  │ Routes       │    │
│  │ - Steam OAuth│  │ - Get stats  │  │ - Generate   │    │
│  │ - Login/out  │  │ - Get viz    │  │ - Explain    │    │
│  │              │  │ - Sync lib   │  │ - Filter     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                    ┌───────▼────────┐                      │
│                    │ Recommender    │                      │
│                    │ Engine         │                      │
│                    │ (from notebooks)│                     │
│                    └───────┬────────┘                      │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PostgreSQL DB  │
                    │                 │
                    │ - users         │
                    │ - user_games    │
                    │ - recommendations│
                    │ - feedback      │
                    └─────────────────┘
```

---

## 🎨 MVP Pages & Features

**Total Pages**: 3 (Landing, Profile, Recommendations)  
**Note**: Settings integrated into Recommendations page as Advanced Filters (collapsible)

### Page 1: Landing Page (Public)
**Purpose**: Explain what the app does, invite users to try it

**Components**:
- Hero section with catchy tagline
  - "Discover your next favorite Steam game using AI"
- How it works (3-step visual):
  1. Connect your Steam account (OAuth)
  2. We analyze your gaming patterns (show mini visualization)
  3. Get personalized recommendations with explanations
- Features showcase:
  - ✅ ML-powered recommendations
  - ✅ Transparent scoring (you see WHY)
  - ✅ Multiple recommendation modes
  - ✅ Visual analytics of your gaming profile
- **Login with Steam** button (prominent)
- Tech stack mention (educational for portfolio)

**Visual Style**: Modern, gaming-themed, dark mode friendly

---

### Page 2: Profile Dashboard
**Purpose**: Show user their gaming profile with rich visualizations

**Components**:

#### 1. **Gaming Stats Overview** (Top Cards)
- Total games owned
- Total hours played
- Top genre (by playtime)
- "Gaming style" badge (e.g., "RPG Enthusiast")

#### 2. **Visualizations** (Interactive Charts - Same as Notebooks!)
These are the SAME visualizations already working in your notebooks:

**Chart 1: Playtime Distribution** (Histogram)
- X-axis: Hours played (bins: 0-5, 5-50, 50+ hrs)
- Y-axis: Number of games
- Shows engagement categories (tried/played/loved)
- Already implemented in: `model_development.ipynb` & `hybrid_recommendations.ipynb`
- Libraries: Recharts (React equivalent of matplotlib)

**Chart 2: Top 10 Most Played Games** (Horizontal Bar Chart)
- Game names on Y-axis
- Hours played on X-axis
- Color-coded bars
- Already implemented in: `model_development.ipynb`
- Libraries: Recharts

**Chart 3: Genre Distribution by Game Count** (Horizontal Bar Chart)
- Top 10 genres by number of games owned
- Already implemented in: `model_development.ipynb`
- Libraries: Recharts

**Chart 4: Genre Distribution by Playtime** (Horizontal Bar Chart)
- Top 10 genres by hours played (more meaningful!)
- Already implemented in: `model_development.ipynb`
- Libraries: Recharts

**Chart 5 (BONUS): Engagement Score vs Playtime** (Scatter Plot)
- X-axis: Playtime (minutes/hours)
- Y-axis: Engagement score (0-100)
- Point size = engagement level
- Already implemented in: `feature_engineering.ipynb`
- Libraries: Recharts

**Chart 6 (BONUS): Feature Importance** (Horizontal Bar Chart)
- Shows top 15 ML features by importance
- Already implemented in: `feature_engineering.ipynb`
- Great for "how it works" explanation!
- Libraries: Recharts

**Chart 7: Release Year Timeline** (Scatter Plot)
- X-axis: Release year (2000-2025)
- Y-axis: Your playtime (hours)
- Point size: Engagement score
- Color: Genre or playtime category
- Shows if you prefer new releases vs classics
- **Note**: ~9k of 80k games have release date data (11%)
- Only display games with release dates (filter out nulls)
- Already have data from: `src/data_retrieval/get_release_dates.py`
- Libraries: Recharts

**Chart 8 (FUTURE): Tag Cloud** (Word Cloud)
- Size = playtime-weighted tag importance
- Optional enhancement (requires react-wordcloud library)
- Can add later if time permits

#### 3. **Your Gaming Profile** (Text Summary)
- "You love [genres] games with [tags]"
- "You've played games for [X] hours total"
- "You tend to finish [Y%] of games you start"

#### 4. **Actions**
- 🔄 Sync library (refresh data from Steam)
- 🎯 Get recommendations (navigate to next page)

---

### Page 3: Recommendations
**Purpose**: Show personalized game recommendations with explanations

**Components**:

#### 1. **Filter Controls** (Top Bar)
- Recommendation mode selector:
  - 🤖 Hybrid (default) - Best of all worlds
  - 🧠 ML-Powered - Learned from your behavior
  - 📊 Content-Based - Similar to games you love
  - ❤️ Preference-Tuned - Your explicit preferences

- **Basic Filters** (Always Visible):
  - Min reviews (slider: 100 - 10k)
  - Min review score (slider: 60% - 95%)
  - Price range (toggle and slider: Free - $60)
  - Exclude Early Access (toggle)
  - SFW only (toggle)

- **Advanced Filters** (Collapsible Panel - Click to Expand):
  
  **Preference Boosts** (Encourage more of these):
  - Boost genres (multiselect + slider for each: +5 to +20 points)
    - Example: RPG +15, Action +10, Strategy +5
  - Boost tags (multiselect + slider for each: +5 to +20 points)
    - Example: Open World +20, Multiplayer +15, Roguelike +10
  
  **Hard Exclusions** (Never show these):
  - Exclude genres (multiselect)
    - Example: Sports, Racing, Horror
  - Exclude tags (multiselect)
    - Example: Survival Horror, Battle Royale, Card Game
  
  **Release Year Filter** (Optional):
  - Enable filter (toggle)
  - Year range slider (2000 - 2025)
    - Example: Only show games from 2015-2023
  - **Note**: Only ~11% of games have release date data
  - Games without release dates will be INCLUDED unless filter is enabled
  - Applied AFTER scoring (hard filter, not a weight)
  
  **Weight Tuning** (Advanced Users Only):
  - ML weight (slider: 0-100%)
  - Content weight (slider: 0-100%)
  - Preference weight (slider: 0-100%)
  - Review weight (slider: 0-100%)
  - Auto-normalize to 100% with live preview
  - Preset buttons: "Balanced" (35/35/20/10), "ML Heavy" (45/25/20/10), "Content Heavy" (25/45/20/10)
  
  **Reset to Defaults** button at bottom of advanced panel

#### 2. **Recommendation Cards** (Grid Layout)
Each card shows:
- **Game image** (Steam header)
- **Game name** + developer
- **Match score** (e.g., 87/100) with visual indicator
- **Price** (with sale indicator if on sale)
- **Review score** (positive % + total reviews)
- **Genre & tags** (clickable and explained)
- **Playtime estimate** (based on median playtime)
- **Steam link** (external)
- **Why recommended?** (Expandable explanation, AI generated):
  ```
  Match Score: 87/100
  
  ML Prediction: 85/100 (35% weight)
    - Strong match for "Open World" (you've played 300hrs)
    - Genre overlap with your loved games
  
  Content Similarity: 78/100 (35% weight)
    - Similar to: Skyrim, Witcher 3, Elden Ring
    - Tags: RPG, Open World, Fantasy
  
  Your Preferences: 90/100 (20% weight)
    - Boosts: RPG (+15), Open World (+20)
    - No penalties
  
  Community Reviews: 95/100 (10% weight)
    - 95% positive (50,000 reviews)
  ```
- **Action buttons**:
  - 👍 Interested (add to wishlist tracking)
  - 👎 Not interested (provide feedback)
  - 🔗 View on Steam (external link)

#### 3. **Explanation Panel** (Sidebar - Optional)
- How scoring works (visual diagram)
- What each component means
- Link to detailed docs

#### 4. **Feedback Collection** (Subtle)
- Track which games user clicks
- Track which games user dismisses
- Store for future collaborative filtering

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    steam_id BIGINT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    profile_url VARCHAR(255),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    settings JSONB  -- Store user preferences as JSON
);

-- User's owned games
CREATE TABLE user_games (
    id SERIAL PRIMARY KEY,
    user_steam_id BIGINT REFERENCES users(steam_id) ON DELETE CASCADE,
    appid INTEGER NOT NULL,
    playtime_hours FLOAT NOT NULL,
    playtime_category VARCHAR(50),  -- 'loved', 'played', 'tried', 'unplayed'
    engagement_score FLOAT,
    last_played TIMESTAMP,
    UNIQUE(user_steam_id, appid)
);

-- Generated recommendations (cache)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_steam_id BIGINT REFERENCES users(steam_id) ON DELETE CASCADE,
    appid INTEGER NOT NULL,
    recommendation_mode VARCHAR(50),  -- 'hybrid', 'ml', 'content', 'preference'
    score FLOAT NOT NULL,
    ml_score FLOAT,
    content_score FLOAT,
    preference_score FLOAT,
    review_score FLOAT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_steam_id, recommendation_mode)
);

-- User feedback (critical for Phase 4)
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_steam_id BIGINT REFERENCES users(steam_id) ON DELETE CASCADE,
    appid INTEGER NOT NULL,
    action VARCHAR(50),  -- 'clicked', 'dismissed', 'wishlisted', 'purchased'
    recommendation_mode VARCHAR(50),
    score_at_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_steam_id, appid)
);

-- System cache (for Steam catalog)
CREATE TABLE catalog_cache (
    appid INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    release_year INTEGER,  -- NULL if not available (~89% of games)
    metadata JSONB,  -- Store all game metadata as JSON
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Backend API Endpoints

### Authentication
```
POST   /api/auth/steam/login       # Initiate Steam OAuth
GET    /api/auth/steam/callback    # OAuth callback
POST   /api/auth/logout            # Logout user
GET    /api/auth/me                # Get current user
```

### User Profile
```
GET    /api/profile/{steam_id}     # Get user's gaming profile
GET    /api/profile/{steam_id}/stats    # Get stats for visualizations
POST   /api/profile/{steam_id}/sync     # Sync library from Steam
```

### Recommendations
```
GET    /api/recommendations/{steam_id}?mode=hybrid&limit=20
       # Get recommendations
       # Query params: mode, limit, min_reviews, min_score, price_max, 
       #               release_year_min, release_year_max, etc.

GET    /api/recommendations/{steam_id}/explain/{appid}
       # Get detailed explanation for why a game was recommended
```

### Feedback
```
POST   /api/feedback
       # Body: { steam_id, appid, action, recommendation_mode }
       # Record user feedback
```

### Utilities
```
GET    /api/catalog/{appid}        # Get game metadata
GET    /api/health                 # Health check
GET    /docs                       # FastAPI auto-generated docs (Swagger)
```

---

## 📂 Project Structure

```
GameRecMLProject/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration (env vars, secrets)
│   ├── database.py              # PostgreSQL connection (SQLAlchemy)
│   ├── models.py                # Database models (SQLAlchemy ORM)
│   ├── schemas.py               # Pydantic models (request/response)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Steam OAuth routes
│   │   ├── profile.py           # User profile routes
│   │   ├── recommendations.py   # Recommendation routes
│   │   └── feedback.py          # Feedback routes
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── steam_api.py         # Steam API integration
│   │   ├── recommender.py       # Recommendation engine (from notebooks)
│   │   ├── visualizer.py        # Generate visualization data
│   │   └── cache.py             # Caching layer
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py          # Auth helpers, input validation
│   │   └── helpers.py           # Common utilities
│   │
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.js
│   │   │   ├── Footer.js
│   │   │   ├── GameCard.js
│   │   │   ├── ScoreExplanation.js
│   │   │   ├── FilterControls.js
│   │   │   └── AdvancedFilters.js     # Collapsible advanced filter panel
│   │   │
│   │   ├── pages/
│   │   │   ├── Landing.js
│   │   │   ├── Profile.js
│   │   │   ├── Recommendations.js
│   │   │   └── Settings.js
│   │   │
│   │   ├── visualizations/
│   │   │   ├── PlaytimeHistogram.js       # Chart 1: Playtime distribution
│   │   │   ├── TopGamesBar.js             # Chart 2: Top 10 most played
│   │   │   ├── GenreCountBar.js           # Chart 3: Genres by count
│   │   │   ├── GenrePlaytimeBar.js        # Chart 4: Genres by playtime
│   │   │   ├── EngagementScatter.js       # Chart 5: Engagement vs playtime
│   │   │   ├── FeatureImportanceBar.js    # Chart 6: ML feature importance (optional)
│   │   │   └── ReleaseYearTimeline.js     # Chart 7: Release year timeline (optional)
│   │   │
│   │   ├── api/
│   │   │   └── client.js        # Axios API client
│   │   │
│   │   ├── utils/
│   │   │   ├── auth.js          # Auth helpers
│   │   │   └── sanitize.js      # Input sanitization (DOMPurify)
│   │   │
│   │   └── styles/
│   │       └── main.css
│   │
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
│
├── data/                        # Existing CSV files
├── models/                      # Existing trained ML models
├── notebooks/                   # Existing Jupyter notebooks
├── docs/                        # Documentation
├── tests/                       # Unit/integration tests
└── README.md
```

---

## 🚀 Implementation Roadmap

### Week 1: Backend Foundation
**Goal**: Working FastAPI backend with auth and basic endpoints

- [x] **Day 1-2: Project Setup**
  - Initialize FastAPI project structure
  - Set up PostgreSQL locally (Docker or native)
  - Create database schema (SQLAlchemy models)
  - Set up Alembic for migrations
  - Configure environment variables (.env)

- [x] **Day 3-4: Steam OAuth** ✅ **COMPLETE**
  - Implement Steam OpenID authentication
  - Create auth routes (login, callback, logout, /me)
  - JWT token generation and validation
  - User session management
  - Security validation & testing

- [ ] **Day 5-7: Core API Endpoints**
  - Profile routes (get, sync)
  - Extract recommender logic from notebooks → `services/recommender.py`
  - Recommendation routes (generate, explain)
  - Test with Postman/Thunder Client

**Deliverable**: Working REST API that can authenticate users and generate recommendations

---

### Week 2: Frontend Foundation
**Goal**: Working React app with basic UI

- [ ] **Day 1-2: React Setup**
  - Create React app with Vite (faster than CRA)
  - Set up React Router for navigation
  - Create layout components (Navbar, Footer)
  - Set up Axios API client with auth headers

- [ ] **Day 3-4: Landing & Auth**
  - Build landing page
  - Implement "Login with Steam" flow
  - Handle OAuth callback and token storage
  - Protected routes (redirect if not authenticated)

- [ ] **Day 5-7: Profile Page**
  - Fetch user profile data from API
  - Display basic stats
  - Create placeholder for visualizations
  - Test end-to-end flow (login → profile)

**Deliverable**: Users can log in and see their basic profile

---

### Week 3: Visualizations & Recommendations
**Goal**: Rich visualizations and recommendation display

- [ ] **Day 1-3: Visualization Components** (Match notebooks!)
  - Install Recharts
  - Build playtime distribution histogram (Chart 1)
  - Build top 10 most played bar chart (Chart 2)
  - Build genre distribution by count (Chart 3)
  - Build genre distribution by playtime (Chart 4)
  - Build engagement score scatter plot (Chart 5)
  - (Optional) Build feature importance chart (Chart 6)
  - (Optional) Build release year timeline (Chart 7)
  - Connect all charts to API data
  - Make charts interactive (hover, click)

- [ ] **Day 4-5: Recommendations Page**
  - Build game card component
  - Build filter controls
  - Build score explanation component
  - Fetch recommendations from API
  - Display top 20 with filters

- [ ] **Day 6-7: Polish & Feedback**
  - Add feedback buttons (thumbs up/down)
  - Implement feedback API calls
  - Add loading states and error handling
  - Basic responsive design

**Deliverable**: Complete MVP with visualizations and recommendations

---

### Week 4: Testing, Polish & Documentation
**Goal**: Production-ready MVP

- [ ] **Day 1-2: Testing**
  - Unit tests for backend (pytest)
  - Integration tests for API endpoints
  - Frontend component tests (React Testing Library)
  - E2E tests (optional: Playwright)

- [ ] **Day 3-4: Security & Performance**
  - Input validation audit (Pydantic + DOMPurify)
  - React2Shell vulnerability check (no eval, no SSR)
  - Add rate limiting (slowapi)
  - Add CORS properly configured
  - SQL injection prevention (SQLAlchemy ORM)
  - XSS prevention (sanitize outputs)

- [ ] **Day 5-6: Polish**
  - Dark mode support
  - Loading skeletons
  - Error boundaries
  - Toast notifications (react-hot-toast)
  - Accessibility (a11y) basics

- [ ] **Day 7: Documentation**
  - Update README with setup instructions
  - API documentation (FastAPI auto-generates)
  - User guide (how to use the app)
  - Architecture diagram

**Deliverable**: Production-ready MVP ready for deployment

---

## 🔒 Security Checklist

### React Server Components RCE (CVE-2025-55182) Mitigation
- [ ] ✅ Use Vite with client-side rendering ONLY (no SSR, no RSC)
- [ ] ✅ DO NOT install Next.js or any `react-server-dom-*` packages
- [ ] ✅ Keep React at 19.0.1+, 19.1.2+, or 19.2.1+
- [ ] ✅ Verify no RSC packages in package.json: `npm ls react-server-dom-webpack react-server-dom-parcel react-server-dom-turbopack`
- [ ] ✅ No `eval()` or `Function()` with user input
- [ ] ✅ No `dangerouslySetInnerHTML` with user data
- [ ] ✅ Sanitize any dynamic content with DOMPurify
- [ ] ✅ Run `npm audit` regularly and fix all critical/high vulnerabilities

### General Web Security
- [ ] ✅ HTTPS only (force SSL in production)
- [ ] ✅ CORS properly configured (whitelist frontend domain)
- [ ] ✅ Rate limiting on API endpoints
- [ ] ✅ Input validation with Pydantic (backend)
- [ ] ✅ SQL injection prevention (use ORM, parameterized queries)
- [ ] ✅ XSS prevention (sanitize outputs, CSP headers)
- [ ] ✅ CSRF protection (SameSite cookies)
- [ ] ✅ Secure session management (JWT with short expiry)
- [ ] ✅ Environment variables for secrets (never commit .env)
- [ ] ✅ Dependency scanning (Dependabot, Snyk)

---

## 📦 Dependencies

### Backend (requirements.txt)
```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0

# Auth
pyjwt==2.8.0
python-jose[cryptography]==3.3.0

# HTTP & API
httpx==0.25.2
pydantic==2.5.2
pydantic-settings==2.1.0

# ML & Data (existing)
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
joblib==1.3.2

# Caching (optional for MVP)
redis==5.0.1

# Rate limiting
slowapi==0.1.9

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "react-wordcloud": "^1.2.7",
    "dompurify": "^3.0.6",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.7",
    "eslint": "^8.55.0",
    "@testing-library/react": "^14.1.2",
    "vitest": "^1.0.4"
  }
}
```

---

## 🎨 Design Guidelines

### Visual Style
- **Theme**: Dark mode friendly, gaming-inspired
- **Colors**: 
  - Primary: Steam blue (#1b2838)
  - Accent: Bright cyan (#66c0f4)
  - Success: Green (#4CAF50)
  - Warning: Orange (#FF9800)
  - Error: Red (#F44336)
- **Typography**: 
  - Headings: Bold, sans-serif (e.g., Inter, Roboto)
  - Body: Clean, readable (e.g., Open Sans, Lato)
- **Components**: Modern cards, smooth transitions, hover effects

### UX Principles
1. **Speed**: Fast load times, optimistic UI updates
2. **Clarity**: Clear labels, helpful tooltips
3. **Transparency**: Always explain WHY (recommendations)
4. **Feedback**: Visual feedback for all actions
5. **Education**: Teach users how the system works

---

## 📊 Success Metrics (MVP)

### Technical
- [ ] ✅ Backend API response time <200ms (avg)
- [ ] ✅ Frontend load time <3 seconds
- [ ] ✅ Zero critical security vulnerabilities
- [ ] ✅ 90%+ test coverage on backend
- [ ] ✅ Mobile responsive (works on phone)

### User Experience
- [ ] ✅ User can log in and see profile within 10 seconds
- [ ] ✅ Recommendations generate within 5 seconds
- [ ] ✅ All visualizations render correctly
- [ ] ✅ No crashes or errors during normal use
- [ ] ✅ Clear explanations for each recommendation

### Data Collection
- [ ] ✅ Track all user feedback (clicks, dismissals)
- [ ] ✅ Store recommendations with timestamps
- [ ] ✅ Log errors for debugging
- [ ] ✅ Analytics on popular genres/tags

---

## 🚧 Out of Scope for MVP

These features are **Phase 4+** and should NOT be in MVP:
- ❌ Collaborative filtering (need 100+ users first)
- ❌ Social features (compare with friends)
- ❌ Price tracking and sale notifications
- ❌ Multi-language support
- ❌ Mobile app (native iOS/Android)
- ❌ Integration with other platforms (Epic, GOG)
- ❌ Advanced user customization (too many settings)
- ❌ Real-time updates (websockets)
- ❌ A/B testing framework (wait for more users)
- ❌ Tag cloud visualization (nice-to-have, not critical for MVP)

**MVP Philosophy**: Do ONE thing really well (personalized recommendations with explanations)

---

## 🎯 Next Steps

### Immediate Actions (Start Today)
1. ✅ Create GitHub repo (if not done)
2. ✅ Set up local development environment:
   - Install PostgreSQL
   - Create virtual environment for backend
   - Install dependencies
3. ✅ Initialize backend project structure
4. ✅ Create database schema and run migrations
5. ✅ Extract recommender logic from notebooks

### Week 1 Priority
- Get Steam OAuth working
- Basic API endpoints functional
- Database connected and storing users

### Week 2 Priority
- React app connected to backend
- Landing page and login flow working
- Basic profile page displaying

### Week 3 Priority
- All visualizations implemented
- Recommendations page functional
- Feedback collection working

### Week 4 Priority
- Testing and security audit
- Polish and bug fixes
- Documentation complete

---

## 💡 Tips for Success

1. **Start Simple**: Get basic flow working first, then add visualizations
2. **Commit Often**: Small, frequent commits with clear messages
3. **Test Locally**: Don't worry about deployment until MVP is working locally
4. **Security First**: Validate inputs, sanitize outputs, keep dependencies updated
5. **User Feedback**: Share with 2-3 friends early, get feedback
6. **Document As You Go**: Update README with setup instructions
7. **Portfolio Ready**: Make it look professional, this is job application material

---

## 📅 Release Year Data: Implementation Notes

**Current Status**: ✅ Collected release dates for ~9k games (11% of catalog)

**Data Source**: Steam Store API via `src/data_retrieval/get_release_dates.py`

**Handling Missing Data**:
- ~89% of games still lack release dates (Early Access, delisted games, API limitations)
- **Timeline Visualization**: Only show games WITH release dates (filter nulls)
- **Release Year Filter**: When disabled (default), include ALL games regardless of release date
- **When enabled**: Only show games within the specified year range that HAVE release dates
- Users see a note: "Note: Only 11% of games have release date data. Games without dates may be excluded when using this filter."

**Future Improvements (Phase 4+)**:
- Background job to periodically fetch more release dates
- Manual override/correction system for inaccurate dates
- Use alternate data sources (IGDB, SteamDB) to fill gaps

**Filter Logic**:
```python
# Pseudo-code for release year filter
if release_year_filter_enabled:
    recommendations = recommendations.filter(
        release_year >= year_min AND 
        release_year <= year_max AND
        release_year IS NOT NULL
    )
else:
    # Include all games, even those without release dates
    recommendations = recommendations
```

---

## 🎉 Let's Build This!

You have:
✅ A solid recommendation engine (Phases 1 & 2)  
✅ Clear tech stack (FastAPI + React + PostgreSQL)  
✅ Detailed plan with security considerations  
✅ Week-by-week roadmap  
✅ Success criteria  

**Next action**: Initialize the backend project structure and start coding! 🚀

---

**Questions? Blockers? Let's tackle them one at a time!**
