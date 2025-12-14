# Steam API Research - What We Can Actually Get

## ✅ WHAT WE CAN GET (Official API)

### 1. **Game Library - YES** 
**Endpoint**: `GetOwnedGames` (IPlayerService)
- ✅ List of all games you own
- ✅ Game names
- ✅ App IDs
- ✅ Playtime in minutes (total and last 2 weeks)
- ✅ Game icons/logos
- ✅ Has community stats/achievements

**Privacy Requirements**: 
- User profile must be PUBLIC (or you use your own API key for your own data)
- Returns empty if profile is private

### 2. **Playtime Data - YES**
**Endpoint**: `GetOwnedGames` / `GetRecentlyPlayedGames`
- ✅ Total playtime (all-time, tracked since ~2009)
- ✅ Recent playtime (last 2 weeks)
- ⚠️ **NO monthly breakdown** (Steam Year in Review has this but no API for it)
- ⚠️ **NO detailed session history** (when you played, how long each session)

### 3. **Game Details - YES**
**Endpoint**: `Store API` (no auth needed)
- ✅ Game description
- ✅ Genres/Categories
- ✅ Tags
- ✅ Price information
- ✅ Release date
- ✅ Developer/Publisher
- ✅ Screenshots
- ✅ Overall review scores (positive/negative percentages)

---

## ❌ WHAT WE CANNOT GET (Major Limitations)

### 1. **User Reviews - NO OFFICIAL API** ❌
- Steam does NOT have an API endpoint for user-written reviews
- **Workaround options**:
  - Web scraping Steam Community pages (against TOS, unreliable)
  - User manually exports their reviews (tedious)
  - Use third-party tools (risky, may break)
  
**Reality**: We basically can't get your review text/ratings unless you manually provide them

### 2. **Wishlist - LIMITED/DEPRECATED** ❌⚠️
- Old endpoint: `https://store.steampowered.com/wishlist/profiles/{steamID}/wishlistdata/`
- **Status**: **DEPRECATED as of November 2024** (confirmed by StackOverflow)
- New method: Requires web scraping or undocumented endpoints
- Privacy: Only works if wishlist is set to public

**Reality**: Wishlist data is NOT reliably accessible via official API anymore

### 3. **Recent Activity/Session Data - NO** ❌
- No API for detailed play sessions
- No timestamps for when games were played
- Can't see gaming patterns over time

### 4. **Game Recommendations - NO** ❌
- Steam's discovery queue is not exposed via API
- No access to Steam's internal recommendation algorithm

---

## 🤔 WHAT THIS MEANS FOR OUR PROJECT

### **Data We Can Actually Use**:
1. ✅ **Your game library** (all games owned)
2. ✅ **Total playtime per game** (hours played)
3. ✅ **Recently played games** (last 2 weeks)
4. ✅ **Game metadata** (genres, tags, descriptions, ratings)

### **Data We CANNOT Reliably Get**:
1. ❌ **Your reviews** (text, ratings, recommendations)
2. ❌ **Your wishlist** (deprecated API, unreliable)
3. ❌ **Detailed play history** (when/how you played)

---

## 💡 REVISED APPROACH OPTIONS

### **Option A: Simple Playtime-Based Recommendations (Most Realistic)**
**What we can do**:
- Get your library + playtime
- Get game metadata (genres, tags, features)
- Build recommendations based on:
  - Games you played most (50+ hours = "loved")
  - Genres/tags of those games
  - Find similar games you don't own
  
**Limitations**:
- No review sentiment (can't tell if you disliked a game you played a lot)
- No wishlist guidance
- Purely content-based filtering

**Pros**:
- ✅ Actually works with available data
- ✅ No scraping/ToS violations
- ✅ Can deploy publicly

### **Option B: Enhanced with Manual Input**
**Same as Option A, but add**:
- User manually marks games as "liked" or "disliked"
- User manually adds games to a wishlist within our app
- Improves recommendations over time

**Pros**:
- ✅ Better accuracy
- ✅ Still legal/compliant
- ⚠️ Requires user interaction

### **Option C: Web Scraping (NOT RECOMMENDED)**
**Technical approach**:
- Scrape Steam Community profile for reviews
- Scrape wishlist from store pages
- Parse HTML to extract data

**Problems**:
- ❌ **Violates Steam ToS**
- ❌ Breaks when Steam updates UI
- ❌ Rate limiting/IP bans
- ❌ Can't deploy publicly without legal risk

---

## 📊 WHAT GOOD ML CAN STILL DO

Even with limited data, we can build a solid recommender:

### **Features We Can Extract**:
1. **Engagement Score**: Normalize playtime to find your most-played games
2. **Genre Preferences**: Which genres you play most
3. **Tag Preferences**: Identify patterns in game tags
4. **Release Date Preferences**: Do you prefer new or older games?
5. **Price Range**: Games you typically buy
6. **Multiplayer vs Single Player**: Preference detection
7. **Game Similarity**: Content-based filtering using game descriptions

### **ML Approaches That Work**:
1. **Content-Based Filtering**: 
   - Find games similar to your top-played games
   - Use game metadata (genres, tags, descriptions)
   
2. **Implicit Feedback Model**:
   - Treat playtime as implicit ratings
   - High playtime = strong positive signal
   - Low/zero playtime = weak signal or not interested
   
3. **Collaborative Filtering** (if we get multiple users):
   - "Users with similar playtime patterns also enjoyed..."
   - Requires more users to work well

---

## 🎯 RECOMMENDED PATH FORWARD

### **Phase 1: MVP with Available Data**
Build a **playtime-based recommendation system**:
1. Collect your library + playtime via API ✅
2. Fetch game metadata (genres, tags, descriptions) ✅
3. Create engagement scores (loved/played/tried/unplayed) ✅
4. Build content-based recommender ✅
5. Test with your real data ✅

**This is 100% doable with official APIs**

### **Phase 2: Enhance (Optional)**
- Add manual like/dislike buttons
- Build internal wishlist feature
- Track user feedback to improve recommendations

### **Phase 3: Deploy**
- Web app where users enter Steam ID
- Get their library and generate recommendations
- No ToS violations, fully legal

---

## 🚨 CRITICAL PRIVACY/ACCESS REQUIREMENTS

For the API to work, users must:
1. **Have a Steam account** (obviously)
2. **Set profile to PUBLIC** (or use their own API key for their own data)
3. **Enable game details visibility** in privacy settings

If profile is private: **API returns empty results**

---

## 📝 FINAL VERDICT

### ✅ **Your Original Idea - Adjusted**:
> "ML program that recommends Steam games based on:
> - ✅ Games in library (YES - API available)
> - ✅ Playtime (YES - API available)
> - ❌ Reviews (NO - no API, would need manual input or scraping)
> - ❌ Wishlist (NO - deprecated, unreliable)

### ✅ **What We Should Build**:
> "ML program that recommends Steam games based on:
> - ✅ Games in library
> - ✅ Playtime data
> - ✅ Game genres, tags, and metadata
> - ✅ Implicit preferences from engagement
> - (Optional) Manual likes/dislikes within app"

---

## ⚡ NEXT STEPS

**Before we write more code:**
1. ✅ You review this research
2. ✅ Decide: Option A (pure API) or Option B (API + manual input)?
3. ✅ I'll refactor the data collection code based on what we choose
4. ✅ Update the PLAN.md to match reality
5. ✅ Build the actual working system

**Want me to proceed with Option A (pure playtime-based) or Option B (with manual input)?**

---

---

## 🎮 ANSWERS TO YOUR QUESTIONS

### Q1: Can we get ALL Steam games from the API?
**Answer: YES (sort of)**

There used to be `ISteamApps/GetAppList` but it appears deprecated/broken in 2025. However, we have alternatives:

**Option 1: Third-party maintained lists** (RECOMMENDED)
- SteamSpy API maintains a complete list of Steam games
- URL: `https://steamspy.com/api.php`
- Community-maintained datasets (GitHub repos with full Steam catalog)
- Updated regularly by the community

**Option 2: Build your own list**
- Start with top/featured games from Store API
- Build incrementally as users search
- Not comprehensive but practical

**Option 3: Static snapshot**
- Download a dataset of all Steam app IDs (available on GitHub)
- Update quarterly
- ~150,000+ apps (includes games, DLC, demos, software)

**Reality**: We don't need ALL 150k apps. We can focus on **actual games only** (~50k-70k) using curated lists.

---

### Q2: Can we get game information (metadata)?
**Answer: YES! ✅ Excellent data available**

**Store API Endpoint**: `https://store.steampowered.com/api/appdetails?appids={appid}`

**What we get per game**:
- ✅ **Name, description** (short & detailed)
- ✅ **Genres** (Action, RPG, Strategy, etc.)
- ✅ **Categories** (Single-player, Multiplayer, Co-op, etc.)
- ✅ **Developers & Publishers**
- ✅ **Release date**
- ✅ **Price information**
- ✅ **Metacritic score** (if available)
- ✅ **Screenshots & videos**
- ✅ **Platform support** (Windows, Mac, Linux)
- ✅ **Recommendations count** (total user recommendations)
- ✅ **System requirements**

**No API key required!** This is public data.

---

### Q3: Can we get TAGS (user-defined tags)?
**Answer: NOT from official API, BUT there's a workaround** ⚠️

**Official API**: Does NOT include user tags
**Categories/Genres**: Yes, included in appdetails

**Workaround for tags**:
1. **SteamSpy API** provides popular tags per game
2. **Community-maintained datasets** (GitHub) have tag mappings
3. **Use categories + genres instead** (often sufficient)

**Tags examples** (from SteamSpy): "Multiplayer", "FPS", "Zombies", "Horror", "Open World", etc.
**Categories/Genres** (from official API): Already give us solid classification

**Reality**: Categories + Genres from official API are probably enough for recommendations.

---

### Q4: Can we get public rating/sentiment? (Positive/Negative/Mixed)?
**Answer: YES! ✅ Exactly what you wanted**

**Endpoint**: `https://store.steampowered.com/appreviews/{appid}?json=1&filter=recent&num_per_page=0`

**What we get**:
```json
{
  "review_score": 6,
  "review_score_desc": "Mostly Positive",
  "total_positive": 19885,
  "total_negative": 6585,
  "total_reviews": 26470
}
```

**Review Score Descriptions** (confirmed from testing):
- "Overwhelmingly Positive"
- "Very Positive"
- "Positive"
- "Mostly Positive"
- "Mixed"
- "Mostly Negative"
- "Negative"
- "Very Negative"
- "Overwhelmingly Negative"

**We can use this as a sentiment score!** ✅

---

## 🎯 FINAL VERDICT: Option A is 100% VIABLE!

### ✅ **What We CAN Get (No Scraping Needed)**:

1. **User's Library**
   - All owned games
   - Playtime per game
   - Recent activity

2. **ALL Steam Games** (via community sources or curated lists)
   - ~50-70k actual games (not DLC/demos)

3. **Complete Game Metadata** (per game)
   - Name, description
   - Genres & categories
   - Developers/publishers
   - Release date, price
   - Metacritic score
   - **Review sentiment (Positive/Negative/Mixed)** ✅
   - Total review count (positive + negative)
   - Recommendation count

4. **Optional: User Tags** (via SteamSpy)
   - Most popular tags per game
   - Community-driven classification

---

## 💡 REVISED PROJECT APPROACH (100% API-Based)

### **Phase 1: Data Collection**
1. Get user's library + playtime (Steam Web API)
2. Get all Steam games list (SteamSpy or curated dataset)
3. For each game (user owns + candidate games):
   - Fetch metadata (Store API)
   - Fetch review sentiment (Store API)
   - Fetch tags (SteamSpy - optional)

### **Phase 2: Feature Engineering**
1. **User preferences from playtime**:
   - Loved games (50+ hours)
   - Played games (5-50 hours)
   - Tried games (0-5 hours)

2. **Game features**:
   - Genres (from official API)
   - Categories (from official API)
   - Review sentiment score (Positive/Negative/Mixed)
   - Metacritic score
   - Tags (optional, from SteamSpy)
   - Release year (new vs old preference)

3. **Similarity metrics**:
   - Genre overlap
   - Category overlap
   - Tag similarity (if using tags)
   - Review sentiment matching
   - Content-based filtering on descriptions

### **Phase 3: ML Recommendation Model**
- **Content-based filtering**: Find games similar to user's top-played games
- **Weighted scoring**: 
  - Genre match (30%)
  - Category match (20%)
  - Review sentiment (20%)
  - Tags match (20% - if using)
  - Metacritic score (10%)
- **Filter out**: Games user already owns
- **Rank by**: Combined similarity score

---

## 🚀 CONFIRMED: We Can Build This!

### **Data Pipeline**:
```
1. User enters Steam ID
   ↓
2. Fetch user library + playtime (Steam Web API)
   ↓
3. Identify user's top games (50+ hours played)
   ↓
4. Fetch metadata for top games (Store API + review sentiment)
   ↓
5. Find similar games from full game catalog
   ↓
6. Fetch metadata for candidate games
   ↓
7. Score & rank by similarity
   ↓
8. Return top 10 recommendations
```

### **No Scraping. No ToS Violations. All Official APIs.**

---

## 📚 References
- Steam Web API Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API
- Store API (appdetails): https://store.steampowered.com/api/appdetails
- Store API (reviews): https://store.steampowered.com/appreviews/{appid}?json=1
- SteamSpy API: https://steamspy.com/api.php
- Partner API Docs: https://partner.steamgames.com/doc/webapi_overview
- Confirmed Wishlist Deprecation: StackOverflow (Nov 2024)
- GetOwnedGames: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetOwnedGames_(v0001)
