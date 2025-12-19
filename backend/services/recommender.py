"""
Hybrid Recommendation Engine Service

This module implements the hybrid recommendation system combining:
1. ML predictions (35%) - Random Forest model trained on user playtime behavior
2. Content-based scoring (35%) - Tag/genre/playtime similarity matching
3. Preference adjustments (20%) - User-specified boosts/penalties
4. Review quality (10%) - Community sentiment and engagement

Architecture:
  Stage 1: Universal Filters (NSFW, Early Access, min reviews, etc.)
  Stage 2: ML Prediction (Random Forest engagement score)
  Stage 3: Content-Based Scoring (similarity to loved games)
  Stage 4: Preference Adjustments (boosts/penalties)
  Stage 5: Review Quality Score (separate component)
  Stage 6: Combine & Rank
  Stage 7: Hard Exclusions (absolute no-gos)
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION & CONSTANTS
# ============================================================

# Model paths (relative to backend directory)
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
DATA_DIR = Path(__file__).parent.parent.parent / "data"

MODEL_PATH = MODELS_DIR / "random_forest_enhanced.pkl"
SCALER_PATH = MODELS_DIR / "feature_scaler_enhanced.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names_enhanced.pkl"

# Hybrid scoring weights
WEIGHT_ML = 0.35
WEIGHT_CONTENT = 0.35
WEIGHT_PREFERENCE = 0.20
WEIGHT_REVIEW = 0.10

# NSFW and meta tag filters
NSFW_TAGS = {
    'Sexual Content', 'Nudity', 'NSFW', 'Adult',
    'Hentai', 'Erotic', 'Sexual', 'Porn', '18+', 'Adult Only'
}

META_TAGS = {
    'Indie', 'Casual', 'Free to Play', 'Early Access',
    'Great Soundtrack', 'Singleplayer', 'Multiplayer',
    'Co-op', 'Online Co-Op', 'PvP', 'PvE',
    'Moddable', 'Controller', 'Partial Controller Support',
    'Steam Achievements', 'Steam Cloud', 'Steam Trading Cards',
    'VR', 'VR Only',
    'Anime', 'Cute', 'Funny', 'Comedy',
    'Classic', 'Remake', 'Remaster', 'Retro'
}

META_GENRES = {
    'Indie', 'Casual', 'Early Access', 'Free to Play',
    'Massively Multiplayer',
    'Utilities', 'Software', 'Animation & Modeling', 'Design & Illustration',
    'Audio Production', 'Video Production', 'Web Publishing', 'Education',
    'Photo Editing', 'Game Development'
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_tags(tag_string) -> Dict[str, int]:
    """Parse tag string into dictionary of tag: votes"""
    if pd.isna(tag_string):
        return {}
    try:
        return ast.literal_eval(str(tag_string))
    except:
        return {}


def parse_genre(genre_string) -> List[str]:
    """Parse genre string into list of genres"""
    if pd.isna(genre_string):
        return []
    return [g.strip() for g in str(genre_string).split(',')]


def build_user_profiles(
    owned_games_df: pd.DataFrame,
    loved_threshold_minutes: int = 3000,  # 50 hours
    disliked_threshold_minutes: int = 300  # 5 hours
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, int], Dict[str, int]]:
    """
    Build user preference profiles from owned games.
    
    Returns:
        - user_tag_profile: Dict[tag, weighted_score] for loved games
        - user_genre_profile: Dict[genre, weighted_score] for loved games
        - disliked_tag_profile: Dict[tag, count] for disliked games
        - disliked_genre_profile: Dict[genre, count] for disliked games
    """
    # Parse tags and genres
    owned_games_df['tags_dict'] = owned_games_df['tags'].apply(parse_tags)
    owned_games_df['genre_list'] = owned_games_df['genre'].apply(parse_genre)
    
    # Identify loved and disliked games
    loved_games = owned_games_df[owned_games_df['playtime_forever'] > loved_threshold_minutes].copy()
    disliked_games = owned_games_df[owned_games_df['playtime_forever'] < disliked_threshold_minutes].copy()
    
    logger.info(f"Building profiles: {len(loved_games)} loved games, {len(disliked_games)} disliked games")
    
    # Build loved tag profile (weighted by playtime)
    user_tag_profile = {}
    total_playtime = loved_games['playtime_forever'].sum()
    
    for _, game in loved_games.iterrows():
        playtime_weight = game['playtime_forever'] / total_playtime if total_playtime > 0 else 0
        for tag, votes in game['tags_dict'].items():
            # Skip NSFW and meta tags
            if tag in NSFW_TAGS or tag in META_TAGS:
                continue
            if tag not in user_tag_profile:
                user_tag_profile[tag] = 0
            user_tag_profile[tag] += votes * playtime_weight
    
    # Build disliked tag profile (count occurrences)
    disliked_tag_profile = {}
    for _, game in disliked_games.iterrows():
        for tag in game['tags_dict'].keys():
            if tag in NSFW_TAGS or tag in META_TAGS:
                continue
            disliked_tag_profile[tag] = disliked_tag_profile.get(tag, 0) + 1
    
    # Remove overlaps with loved tags
    loved_tag_set = set(user_tag_profile.keys())
    disliked_tag_profile = {
        tag: count for tag, count in disliked_tag_profile.items()
        if tag not in loved_tag_set and count >= 3  # At least 3 games
    }
    
    # Build loved genre profile (weighted by playtime)
    user_genre_profile = {}
    for _, game in loved_games.iterrows():
        playtime_weight = game['playtime_forever'] / total_playtime if total_playtime > 0 else 0
        for genre in game['genre_list']:
            if genre in META_GENRES:
                continue
            if genre not in user_genre_profile:
                user_genre_profile[genre] = 0
            user_genre_profile[genre] += playtime_weight
    
    # Build disliked genre profile
    disliked_genre_profile = {}
    for _, game in disliked_games.iterrows():
        for genre in game['genre_list']:
            if genre in META_GENRES:
                continue
            disliked_genre_profile[genre] = disliked_genre_profile.get(genre, 0) + 1
    
    # Remove overlaps
    loved_genre_set = set(user_genre_profile.keys())
    disliked_genre_profile = {
        genre: count for genre, count in disliked_genre_profile.items()
        if genre not in loved_genre_set and count >= 3
    }
    
    return user_tag_profile, user_genre_profile, disliked_tag_profile, disliked_genre_profile


def calculate_content_score(
    game_row: pd.Series,
    user_tag_profile: Dict[str, float],
    user_genre_profile: Dict[str, float]
) -> float:
    """
    Calculate content-based score (0-100) for a single game.
    
    Components (NO REVIEWS - they're separate!):
    - Tag similarity: 55 points (specific gameplay features)
    - Genre overlap: 25 points (broad categories)
    - Median playtime match: 20 points (engagement signal)
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Get game tags (handle both dict and list formats)
    game_tags_raw = game_row['tags_dict']
    if isinstance(game_tags_raw, dict):
        game_tags = game_tags_raw
    elif isinstance(game_tags_raw, list):
        game_tags = {tag: 1 for tag in game_tags_raw}
    else:
        game_tags = {}
    
    # Check for NSFW content (hard filter)
    if any(tag in NSFW_TAGS for tag in game_tags.keys()):
        return 0.0
    
    # 1. Tag similarity (55 points)
    tag_score = 0.0
    if game_tags and user_tag_profile:
        # Calculate cosine-style similarity with vote weighting
        matching_score = 0.0
        total_user_weight = sum(user_tag_profile.values())
        
        for tag, votes in game_tags.items():
            if tag in NSFW_TAGS or tag in META_TAGS:
                continue
            if tag in user_tag_profile:
                # Normalized contribution: user preference * game popularity
                user_weight = user_tag_profile[tag] / (total_user_weight + 0.01)
                vote_weight = min(1.0, votes / 500)  # Cap at 500 votes for normalization
                matching_score += user_weight * vote_weight
        
        # Scale to 0-55 range (matching_score is 0-1)
        tag_score = matching_score * 55
    
    score += tag_score
    
    # 2. Genre overlap (25 points)
    genre_score = 0.0
    game_genres = game_row['genre_list']
    if game_genres:
        for genre in game_genres:
            if genre in META_GENRES:
                continue
            if genre in user_genre_profile:
                genre_score += user_genre_profile[genre]
        
        genre_score = min(25, genre_score * 25)
    
    score += genre_score
    
    # 3. Median playtime similarity (20 points)
    median_playtime = game_row.get('median_forever', 0)
    if pd.notna(median_playtime) and median_playtime > 0:
        median_hours = median_playtime / 60
        if median_hours >= 50:
            playtime_score = 20  # Deep, engaging game
        elif median_hours >= 20:
            playtime_score = 15  # Good engagement
        elif median_hours >= 10:
            playtime_score = 10  # Decent engagement
        elif median_hours >= 5:
            playtime_score = 5   # Some engagement
        else:
            playtime_score = 0   # Low engagement
    else:
        playtime_score = 0
    
    score += playtime_score
    
    return max(0, score)


def calculate_preference_score(
    game_row: pd.Series,
    disliked_tag_profile: Dict[str, int],
    disliked_genre_profile: Dict[str, int],
    boost_tags: Optional[Dict[str, int]] = None,
    boost_genres: Optional[Dict[str, int]] = None,
    dislike_tags: Optional[Dict[str, int]] = None,
    dislike_genres: Optional[Dict[str, int]] = None
) -> float:
    """
    Calculate preference adjustments (0-100 scale).
    
    Combines:
    - Auto-learned dislikes from <5hr games
    - User-specified boosts (want to see more)
    - User-specified additional dislikes
    
    Returns:
        Score from 0-100 where 50 is neutral
    """
    score = 50.0  # Start neutral
    
    boost_tags = boost_tags or {}
    boost_genres = boost_genres or {}
    dislike_tags = dislike_tags or {}
    dislike_genres = dislike_genres or {}
    
    # Get game tags
    game_tags_raw = game_row['tags_dict']
    if isinstance(game_tags_raw, dict):
        game_tags = game_tags_raw
    elif isinstance(game_tags_raw, list):
        game_tags = {tag: 1 for tag in game_tags_raw}
    else:
        game_tags = {}
    
    game_genres = game_row['genre_list']
    
    # Apply auto-learned disliked tag penalties
    for tag in game_tags.keys():
        if tag in disliked_tag_profile:
            score -= 5  # -5 points per auto-learned disliked tag
    
    # Apply auto-learned disliked genre penalties
    for genre in game_genres:
        if genre in disliked_genre_profile:
            score -= 10  # -10 points per auto-learned disliked genre
    
    # Apply user-specified boosts
    for tag in game_tags.keys():
        if tag in boost_tags:
            score += boost_tags[tag]
    
    for genre in game_genres:
        if genre in boost_genres:
            score += boost_genres[genre]
    
    # Apply user-specified additional penalties
    for tag in game_tags.keys():
        if tag in dislike_tags:
            score += dislike_tags[tag]  # Already negative in dict
    
    for genre in game_genres:
        if genre in dislike_genres:
            score += dislike_genres[genre]  # Already negative in dict
    
    return max(0, min(100, score))


def calculate_review_score(game_row: pd.Series) -> float:
    """
    Calculate review quality score (0-100 scale).
    
    Components:
    - Quality tier based on positive percentage
    - Volume bonus (logarithmic)
    
    Returns:
        Score from 0-100
    """
    positive = game_row.get('positive', 0)
    negative = game_row.get('negative', 0)
    total = positive + negative
    
    if total == 0:
        return 0.0
    
    positive_ratio = positive / total
    review_percentage = positive_ratio * 100
    
    # Quality tiers
    if review_percentage >= 95:
        quality_multiplier = 2.5  # Overwhelmingly Positive
    elif review_percentage >= 90:
        quality_multiplier = 2.0  # Very Positive
    elif review_percentage >= 80:
        quality_multiplier = 1.5  # Mostly Positive
    elif review_percentage >= 70:
        quality_multiplier = 1.0  # Positive
    elif review_percentage >= 60:
        quality_multiplier = 0.5  # Mixed
    else:
        quality_multiplier = 0.1  # Negative
    
    # Volume bonus (logarithmic)
    volume_score = np.log10(total + 1) * quality_multiplier
    
    # Normalize to 0-100 (max realistic: log10(1M) * 2.5 = 15)
    return min(100, (volume_score / 15) * 100)


# ============================================================
# RECOMMENDER CLASS
# ============================================================

class HybridRecommender:
    """
    Hybrid recommendation engine combining ML, content-based, preferences, and reviews.
    """
    
    def __init__(self):
        """Initialize the recommender and load ML models."""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.catalog_df: Optional[pd.DataFrame] = None
        
        self._load_models()
        self._load_catalog()
    
    def _load_models(self):
        """Load the trained ML model, scaler, and feature names."""
        try:
            logger.info(f"Loading ML model from {MODEL_PATH}")
            self.model = joblib.load(MODEL_PATH)
            
            logger.info(f"Loading feature scaler from {SCALER_PATH}")
            self.scaler = joblib.load(SCALER_PATH)
            
            logger.info(f"Loading feature names from {FEATURE_NAMES_PATH}")
            self.feature_names = joblib.load(FEATURE_NAMES_PATH)
            
            logger.info("ML models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
            raise
    
    def _load_catalog(self):
        """Load the Steam catalog with detailed metadata."""
        try:
            catalog_path = DATA_DIR / "steam_catalog_detailed.csv"
            logger.info(f"Loading catalog from {catalog_path}")
            self.catalog_df = pd.read_csv(catalog_path)
            
            initial_count = len(self.catalog_df)
            
            # Parse release_date to extract year
            self.catalog_df['release_year'] = pd.to_datetime(
                self.catalog_df['release_date'], 
                format='%b %d, %Y', 
                errors='coerce'
            ).dt.year
            
            # DEDUPLICATE: Remove duplicate game names, keep the one with most reviews
            logger.info(f"Checking for duplicate game names...")
            self.catalog_df['total_reviews'] = self.catalog_df['positive'] + self.catalog_df['negative']
            
            # Find duplicates
            duplicates = self.catalog_df[self.catalog_df.duplicated(subset=['name'], keep=False)]
            if len(duplicates) > 0:
                logger.info(f"Found {len(duplicates)} duplicate entries for {duplicates['name'].nunique()} games")
                
                # Log some examples
                for name in duplicates['name'].unique()[:5]:
                    dupes = self.catalog_df[self.catalog_df['name'] == name]
                    logger.info(f"  '{name}': {len(dupes)} versions (appids: {dupes['appid'].tolist()})")
                
                # Keep only the version with most reviews (most popular/current)
                self.catalog_df = self.catalog_df.sort_values('total_reviews', ascending=False).drop_duplicates(
                    subset=['name'], keep='first'
                ).sort_index()
                
                logger.info(f"Deduplicated: {initial_count} → {len(self.catalog_df)} games (removed {initial_count - len(self.catalog_df)} duplicates)")
            
            # Parse tags and genres
            self.catalog_df['tags_dict'] = self.catalog_df['tags'].apply(parse_tags)
            self.catalog_df['genre_list'] = self.catalog_df['genre'].apply(parse_genre)
            
            logger.info(f"Catalog loaded: {len(self.catalog_df)} unique games")
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            raise
    
    def generate_recommendations(
        self,
        owned_games_df: pd.DataFrame,
        sfw_only: bool = True,
        exclude_early_access: bool = True,
        min_reviews: int = 5000,
        min_review_score: int = 70,
        release_year_min: Optional[int] = None,
        release_year_max: Optional[int] = None,
        boost_tags: Optional[Dict[str, int]] = None,
        boost_genres: Optional[Dict[str, int]] = None,
        dislike_tags: Optional[Dict[str, int]] = None,
        dislike_genres: Optional[Dict[str, int]] = None,
        hard_exclude_tags: Optional[List[str]] = None,
        hard_exclude_genres: Optional[List[str]] = None,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Generate hybrid recommendations for a user.
        
        Args:
            owned_games_df: DataFrame with user's owned games
            sfw_only: Filter out NSFW content
            exclude_early_access: Filter out Early Access games
            min_reviews: Minimum review count threshold
            min_review_score: Minimum positive review percentage
            release_year_min: Minimum release year (inclusive)
            release_year_max: Maximum release year (inclusive)
            boost_tags: Dict of tag: boost_points to prioritize
            boost_genres: Dict of genre: boost_points to prioritize
            dislike_tags: Dict of tag: penalty_points to avoid
            dislike_genres: Dict of genre: penalty_points to avoid
            hard_exclude_tags: List of tags to completely exclude
            hard_exclude_genres: List of genres to completely exclude
            top_n: Number of recommendations to return
            
        Returns:
            DataFrame with top N recommendations and all scores
        """
        logger.info("=" * 60)
        logger.info("STARTING HYBRID RECOMMENDATION GENERATION")
        logger.info("=" * 60)
        
        # Stage 1: Universal Filters
        logger.info("\nStage 1: Applying universal filters...")
        catalog_filtered = self._apply_universal_filters(
            sfw_only, exclude_early_access, min_reviews, min_review_score,
            release_year_min, release_year_max
        )
        
        # Exclude already owned games (by appid AND by name for duplicate editions)
        owned_appids = set(owned_games_df['appid'].tolist())
        owned_names = set(owned_games_df['name'].dropna().unique()) if 'name' in owned_games_df.columns else set()
        
        logger.info(f"User owns {len(owned_appids)} games")
        logger.info(f"Sample of owned appids (first 10): {sorted(list(owned_appids))[:10]}")
        logger.info(f"Sample of owned names (first 5): {sorted(list(owned_names))[:5]}")
        logger.info(f"Catalog before filtering: {len(catalog_filtered)} games")
        
        # Ensure both are same type (int) for comparison
        owned_appids_int = set(int(appid) for appid in owned_appids)
        catalog_filtered['appid'] = catalog_filtered['appid'].astype(int)
        
        # Filter by BOTH appid AND name (handles duplicate editions)
        catalog_unowned = catalog_filtered[
            ~catalog_filtered['appid'].isin(owned_appids_int) & 
            ~catalog_filtered['name'].isin(owned_names)
        ].copy()
        
        removed_by_appid = len(catalog_filtered[catalog_filtered['appid'].isin(owned_appids_int)])
        removed_by_name = len(catalog_filtered[
            ~catalog_filtered['appid'].isin(owned_appids_int) & 
            catalog_filtered['name'].isin(owned_names)
        ])
        
        logger.info(f"Filtered owned games:")
        logger.info(f"  - By appid: {removed_by_appid} games")
        logger.info(f"  - By name (duplicate editions): {removed_by_name} games")
        logger.info(f"  - Total removed: {len(catalog_filtered) - len(catalog_unowned)} games")
        logger.info(f"  - Remaining: {len(catalog_unowned)} games")
        
        # Verify no owned games remain
        remaining_owned_appid = catalog_unowned[catalog_unowned['appid'].isin(owned_appids_int)]
        remaining_owned_name = catalog_unowned[catalog_unowned['name'].isin(owned_names)]
        
        if len(remaining_owned_appid) > 0:
            logger.error(f"❌ ERROR: {len(remaining_owned_appid)} owned games (by appid) still in catalog!")
            logger.error(f"{remaining_owned_appid[['appid', 'name']].head(10).to_dict('records')}")
        
        if len(remaining_owned_name) > 0:
            logger.error(f"❌ ERROR: {len(remaining_owned_name)} owned games (by name) still in catalog!")
            logger.error(f"{remaining_owned_name[['appid', 'name']].head(10).to_dict('records')}")
        
        # Build user profiles
        logger.info("\nBuilding user preference profiles...")
        user_tag_profile, user_genre_profile, disliked_tag_profile, disliked_genre_profile = \
            build_user_profiles(owned_games_df)
        
        # Stage 2: ML Predictions
        logger.info("\nStage 2: Generating ML predictions...")
        # TODO: Implement ML prediction logic
        # For now, use placeholder scores
        catalog_unowned['ml_score'] = 50.0  # Placeholder
        
        # Stage 3: Content-Based Scoring
        logger.info("\nStage 3: Calculating content-based scores...")
        catalog_unowned['content_score'] = catalog_unowned.apply(
            lambda row: calculate_content_score(row, user_tag_profile, user_genre_profile),
            axis=1
        )
        
        # Stage 4: Preference Adjustments
        logger.info("\nStage 4: Calculating preference scores...")
        catalog_unowned['preference_score'] = catalog_unowned.apply(
            lambda row: calculate_preference_score(
                row, disliked_tag_profile, disliked_genre_profile,
                boost_tags, boost_genres, dislike_tags, dislike_genres
            ),
            axis=1
        )
        
        # Stage 5: Review Quality
        logger.info("\nStage 5: Calculating review scores...")
        catalog_unowned['review_score'] = catalog_unowned.apply(
            calculate_review_score, axis=1
        )
        
        # Stage 6: Combine & Rank
        logger.info("\nStage 6: Combining scores with adaptive weighting...")
        
        # Detect if user has meaningful preferences
        # Preferences are meaningful if:
        # 1. User explicitly provided boost/dislike tags/genres, OR
        # 2. User has auto-learned dislikes from their library
        has_explicit_preferences = bool(
            (boost_tags and len(boost_tags) > 0) or
            (boost_genres and len(boost_genres) > 0) or
            (dislike_tags and len(dislike_tags) > 0) or
            (dislike_genres and len(dislike_genres) > 0)
        )
        has_learned_preferences = bool(
            (disliked_tag_profile and len(disliked_tag_profile) > 0) or
            (disliked_genre_profile and len(disliked_genre_profile) > 0)
        )
        has_preferences = has_explicit_preferences or has_learned_preferences
        
        # Adaptive weighting: redistribute preference weight if not using preferences
        if has_preferences:
            # Standard weights when preferences are meaningful
            weight_ml = WEIGHT_ML
            weight_content = WEIGHT_CONTENT
            weight_preference = WEIGHT_PREFERENCE
            weight_review = WEIGHT_REVIEW
            logger.info(f"Using standard weights (preferences detected: explicit={has_explicit_preferences}, learned={has_learned_preferences})")
        else:
            # Redistribute preference weight proportionally to other components
            # Original: ML=35%, Content=35%, Preference=20%, Review=10%
            # Without preference: Redistribute 20% proportionally
            # ML: 35% → 43.75% (+25% of 35%)
            # Content: 35% → 43.75% (+25% of 35%)
            # Review: 10% → 12.5% (+25% of 10%)
            redistribution_factor = 1.0 / (1.0 - WEIGHT_PREFERENCE)
            weight_ml = WEIGHT_ML * redistribution_factor
            weight_content = WEIGHT_CONTENT * redistribution_factor
            weight_preference = 0.0
            weight_review = WEIGHT_REVIEW * redistribution_factor
            logger.info(f"Using adaptive weights (no preferences detected): ML={weight_ml:.1%}, Content={weight_content:.1%}, Review={weight_review:.1%}")
        
        # Weighted average - each component is 0-100, result is also 0-100
        catalog_unowned['hybrid_score'] = (
            weight_ml * catalog_unowned['ml_score'] +
            weight_content * catalog_unowned['content_score'] +
            weight_preference * catalog_unowned['preference_score'] +
            weight_review * catalog_unowned['review_score']
        )
        
        # Stage 7: Hard Exclusions
        logger.info("\nStage 7: Applying hard exclusions...")
        catalog_final = self._apply_hard_exclusions(
            catalog_unowned, hard_exclude_tags or [], hard_exclude_genres or []
        )
        
        # Get top N (get more than needed to account for deduplication)
        top_recommendations = catalog_final.nlargest(top_n * 2, 'hybrid_score')
        
        # Check for duplicate game names and similar editions in recommendations
        # Create normalized names by removing edition suffixes
        edition_suffixes = [
            'Special Edition', 'Definitive Edition', 'Remastered', 'Remake',
            'Enhanced Edition', 'Complete Edition', 'GOTY', 'Game of the Year Edition',
            'Ultimate Edition', 'Deluxe Edition', 'Premium Edition', 'Gold Edition',
            'Anniversary Edition', 'Legendary Edition', 'Royal Edition', 'Director\'s Cut',
            'Redux', 'HD', 'Legacy', 'VR Only', 'VR'
        ]
        
        def normalize_name(name):
            """Remove edition suffixes and extra whitespace for fuzzy matching."""
            if pd.isna(name):
                return ""
            normalized = str(name).strip()
            # Remove trailing colons and dashes
            normalized = normalized.rstrip(' :-')
            # Remove edition suffixes
            for suffix in edition_suffixes:
                # Try with colon/dash separator
                for sep in [':', ' -', ' –', ' —', '']:
                    pattern = f"{sep} {suffix}"
                    if normalized.endswith(pattern):
                        normalized = normalized[:-len(pattern)].strip()
                        break
            return normalized.strip()
        
        top_recommendations['normalized_name'] = top_recommendations['name'].apply(normalize_name)
        
        # Find both exact duplicates and similar editions
        duplicates_exact = top_recommendations[top_recommendations.duplicated(subset=['name'], keep=False)]
        duplicates_normalized = top_recommendations[top_recommendations.duplicated(subset=['normalized_name'], keep=False)]
        
        if len(duplicates_exact) > 0 or len(duplicates_normalized) > 0:
            if len(duplicates_exact) > 0:
                logger.info(f"\nFound {len(duplicates_exact)} exact duplicate entries:")
                for name in duplicates_exact['name'].unique():
                    dupes = top_recommendations[top_recommendations['name'] == name]
                    logger.info(f"  '{name}': {len(dupes)} versions")
            
            if len(duplicates_normalized) > 0:
                logger.info(f"\nFound {len(duplicates_normalized)} similar game editions:")
                for norm_name in duplicates_normalized['normalized_name'].unique():
                    dupes = top_recommendations[top_recommendations['normalized_name'] == norm_name]
                    if len(dupes) > 1:
                        logger.info(f"  Base game: '{norm_name}'")
                        for _, dupe in dupes.iterrows():
                            logger.info(f"    - {dupe['appid']}: '{dupe['name']}' (score: {dupe['hybrid_score']:.2f})")
            
            # Deduplicate by normalized name, keeping highest-scoring version
            logger.info(f"\nDeduplicating by normalized name (keeping highest-scoring edition)...")
            before_dedup = len(top_recommendations)
            top_recommendations = top_recommendations.sort_values('hybrid_score', ascending=False).drop_duplicates(
                subset=['normalized_name'], keep='first'
            )
            logger.info(f"  Removed {before_dedup - len(top_recommendations)} duplicate/similar editions")
        
        # Drop the temporary normalized_name column
        top_recommendations = top_recommendations.drop(columns=['normalized_name'])
        
        # Now take only top N after deduplication
        top_recommendations = top_recommendations.head(top_n)
        
        # Final verification: check if any recommended games are owned
        recommended_appids = set(top_recommendations['appid'].tolist())
        recommended_names = set(top_recommendations['name'].tolist())
        
        owned_in_recommendations = recommended_appids & owned_appids_int
        name_matches = recommended_names & owned_names
        
        if owned_in_recommendations:
            logger.error(f"❌ ERROR: {len(owned_in_recommendations)} owned games (by appid) in final recommendations!")
            logger.error(f"Owned games being recommended: {sorted(list(owned_in_recommendations))}")
            problematic_games = top_recommendations[top_recommendations['appid'].isin(owned_in_recommendations)]
            logger.error(f"Problematic games: {problematic_games[['appid', 'name', 'hybrid_score']].to_dict('records')}")
        elif name_matches:
            logger.error(f"❌ ERROR: {len(name_matches)} owned games (by name) in final recommendations!")
            logger.error(f"Owned game names: {sorted(list(name_matches))}")
            problematic_games = top_recommendations[top_recommendations['name'].isin(name_matches)]
            logger.error(f"Problematic games: {problematic_games[['appid', 'name', 'hybrid_score']].to_dict('records')}")
        else:
            logger.info(f"✓ Verified: No owned games in recommendations")
        
        logger.info(f"\n✓ Generated {len(top_recommendations)} unique recommendations")
        logger.info("=" * 60)
        
        return top_recommendations
    
    def _apply_universal_filters(
        self,
        sfw_only: bool,
        exclude_early_access: bool,
        min_reviews: int,
        min_review_score: int,
        release_year_min: Optional[int] = None,
        release_year_max: Optional[int] = None
    ) -> pd.DataFrame:
        """Apply universal quality and appropriateness filters."""
        assert self.catalog_df is not None, "Catalog not loaded"
        filtered = self.catalog_df.copy()
        initial_count = len(filtered)
        
        # NSFW filter
        if sfw_only:
            def has_nsfw(tags_dict):
                if isinstance(tags_dict, dict):
                    return any(tag in NSFW_TAGS for tag in tags_dict.keys())
                return False
            
            filtered = filtered[~filtered['tags_dict'].apply(has_nsfw)]
            logger.info(f"  SFW filter: {initial_count} → {len(filtered)} games")
        
        # Early Access filter
        if exclude_early_access:
            before = len(filtered)
            filtered = filtered[
                ~filtered['genre_list'].apply(lambda x: 'Early Access' in x)
            ]
            logger.info(f"  Early Access filter: {before} → {len(filtered)} games")
        
        # Review count filter
        before = len(filtered)
        filtered = filtered[
            (filtered['positive'] + filtered['negative']) >= min_reviews
        ]
        logger.info(f"  Min reviews filter ({min_reviews}): {before} → {len(filtered)} games")
        
        # Review score filter
        before = len(filtered)
        filtered = filtered[
            (filtered['positive'] / (filtered['positive'] + filtered['negative']) * 100) >= min_review_score
        ]
        logger.info(f"  Min review score filter ({min_review_score}%): {before} → {len(filtered)} games")
        
        # Meta genre filter
        before = len(filtered)
        filtered = filtered[
            ~filtered['genre_list'].apply(
                lambda x: any(g in META_GENRES for g in x)
            )
        ]
        logger.info(f"  Meta genre filter: {before} → {len(filtered)} games")
        
        # Release year filters
        if release_year_min is not None:
            before = len(filtered)
            filtered = filtered[
                (filtered['release_year'].notna()) & 
                (filtered['release_year'] >= release_year_min)
            ]
            logger.info(f"  Min release year filter ({release_year_min}): {before} → {len(filtered)} games")
        
        if release_year_max is not None:
            before = len(filtered)
            filtered = filtered[
                (filtered['release_year'].notna()) & 
                (filtered['release_year'] <= release_year_max)
            ]
            logger.info(f"  Max release year filter ({release_year_max}): {before} → {len(filtered)} games")
        
        return filtered
    
    def _apply_hard_exclusions(
        self,
        df: pd.DataFrame,
        exclude_tags: List[str],
        exclude_genres: List[str]
    ) -> pd.DataFrame:
        """Apply hard exclusions (absolute no-gos)."""
        filtered = df.copy()
        
        if exclude_genres:
            before = len(filtered)
            filtered = filtered[
                ~filtered['genre_list'].apply(lambda x: any(g in exclude_genres for g in x))
            ]
            logger.info(f"  Hard exclude genres: {before} → {len(filtered)} games")
        
        if exclude_tags:
            before = len(filtered)
            
            def has_excluded_tag(tags_dict):
                if isinstance(tags_dict, dict):
                    return any(t in exclude_tags for t in tags_dict.keys())
                elif isinstance(tags_dict, list):
                    return any(t in exclude_tags for t in tags_dict)
                return False
            
            filtered = filtered[~filtered['tags_dict'].apply(has_excluded_tag)]
            logger.info(f"  Hard exclude tags: {before} → {len(filtered)} games")
        
        return filtered
    
    def explain_recommendation(
        self,
        appid: int,
        owned_games_df: pd.DataFrame
    ) -> Dict:
        """
        Generate a detailed explanation for why a game was recommended.
        
        Args:
            appid: Steam App ID of the game
            owned_games_df: User's owned games
            
        Returns:
            Dict with detailed score breakdowns and explanations
        """
        # Find the game in catalog
        assert self.catalog_df is not None, "Catalog not loaded"
        game = self.catalog_df[self.catalog_df['appid'] == appid]
        if game.empty:
            raise ValueError(f"Game {appid} not found in catalog")
        
        game = game.iloc[0]
        
        # Build user profiles
        user_tag_profile, user_genre_profile, disliked_tag_profile, disliked_genre_profile = \
            build_user_profiles(owned_games_df)
        
        # Calculate individual scores
        content_score = calculate_content_score(game, user_tag_profile, user_genre_profile)
        preference_score = calculate_preference_score(
            game, disliked_tag_profile, disliked_genre_profile
        )
        review_score = calculate_review_score(game)
        ml_score = 50.0  # Placeholder
        
        # Calculate hybrid score (weighted average)
        hybrid_score = (
            WEIGHT_ML * ml_score +
            WEIGHT_CONTENT * content_score +
            WEIGHT_PREFERENCE * preference_score +
            WEIGHT_REVIEW * review_score
        )
        
        # Build explanation
        explanation = {
            "appid": int(appid),
            "name": game['name'],
            "hybrid_score": round(hybrid_score, 2),
            "scores": {
                "ml": {"score": round(ml_score, 2), "weight": WEIGHT_ML},
                "content": {"score": round(content_score, 2), "weight": WEIGHT_CONTENT},
                "preference": {"score": round(preference_score, 2), "weight": WEIGHT_PREFERENCE},
                "review": {"score": round(review_score, 2), "weight": WEIGHT_REVIEW}
            },
            "matching_tags": [],
            "matching_genres": [],
            "disliked_tags": [],
            "disliked_genres": []
        }
        
        # Find matching tags
        game_tags = game['tags_dict'] if isinstance(game['tags_dict'], dict) else {}
        for tag in game_tags.keys():
            if tag in user_tag_profile and tag not in NSFW_TAGS and tag not in META_TAGS:
                explanation["matching_tags"].append({
                    "tag": tag,
                    "user_weight": round(user_tag_profile[tag], 2)
                })
        
        # Find matching genres
        for genre in game['genre_list']:
            if genre in user_genre_profile and genre not in META_GENRES:
                explanation["matching_genres"].append({
                    "genre": genre,
                    "user_weight": round(user_genre_profile[genre], 4)
                })
        
        # Find disliked tags/genres
        for tag in game_tags.keys():
            if tag in disliked_tag_profile:
                explanation["disliked_tags"].append(tag)
        
        for genre in game['genre_list']:
            if genre in disliked_genre_profile:
                explanation["disliked_genres"].append(genre)
        
        return explanation
