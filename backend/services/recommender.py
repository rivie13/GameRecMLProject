"""
Hybrid Recommendation Engine - Main Orchestrator

Refactored architecture with clear separation of concerns:
- recommender.py (this file): Main orchestration and workflow
- scoring.py: Content, preference, and review scoring logic
- ml_predictor.py: ML model and predictions
- filters.py: Universal, hard exclusion, and diversity filters
- utils.py: Helper functions and constants
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .ml_predictor import MLPredictor
from .scoring import (
    build_user_profiles,
    calculate_content_score,
    calculate_preference_score,
    calculate_review_score
)
from .filters import (
    apply_universal_filters,
    apply_hard_exclusions,
    apply_diversity_filters
)
from .utils import parse_tags, parse_genre

logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Default hybrid scoring weights
WEIGHT_ML = 0.35
WEIGHT_CONTENT = 0.35
WEIGHT_PREFERENCE = 0.20
WEIGHT_REVIEW = 0.10


class HybridRecommender:
    """Hybrid recommendation engine combining ML, content, preferences, and reviews."""
    
    def __init__(self):
        """Initialize the recommender."""
        self.catalog_df: Optional[pd.DataFrame] = None
        self.ml_predictor = MLPredictor()
        self._load_catalog()
    
    def _load_catalog(self):
        """Load and preprocess the Steam catalog."""
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
            
            # Deduplicate by name (keep most reviewed)
            logger.info(f"Checking for duplicate game names...")
            self.catalog_df['total_reviews'] = self.catalog_df['positive'] + self.catalog_df['negative']
            
            duplicates = self.catalog_df[self.catalog_df.duplicated(subset=['name'], keep=False)]
            if len(duplicates) > 0:
                logger.info(f"Found {len(duplicates)} duplicate entries for {duplicates['name'].nunique()} games")
                self.catalog_df = self.catalog_df.sort_values('total_reviews', ascending=False).drop_duplicates(
                    subset=['name'], keep='first'
                ).sort_index()
                logger.info(f"Deduplicated: {initial_count} → {len(self.catalog_df)} games")
            
            # Parse tags and genres
            self.catalog_df['tags_dict'] = self.catalog_df['tags'].apply(parse_tags)
            self.catalog_df['genre_list'] = self.catalog_df['genre'].apply(parse_genre)
            
            # Ensure proper data types
            if 'appid' in self.catalog_df.columns:
                self.catalog_df['appid'] = self.catalog_df['appid'].astype(int)
            
            logger.info(f"✓ Catalog loaded: {len(self.catalog_df)} unique games")
        except Exception as e:
            logger.error(f"❌ Failed to load catalog: {e}")
            raise
    
    def generate_recommendations(
        self,
        owned_games_df: pd.DataFrame,
        sfw_only: bool = True,
        exclude_early_access: bool = True,
        min_reviews: int = 5000,
        min_review_score: int = 70,
        price_max: Optional[float] = None,
        release_year_min: Optional[int] = None,
        release_year_max: Optional[int] = None,
        boost_tags: Optional[Dict[str, int]] = None,
        boost_genres: Optional[Dict[str, int]] = None,
        dislike_tags: Optional[Dict[str, int]] = None,
        dislike_genres: Optional[Dict[str, int]] = None,
        hard_exclude_tags: Optional[List[str]] = None,
        hard_exclude_genres: Optional[List[str]] = None,
        genre_limits: Optional[Dict[str, int]] = None,
        tag_limits: Optional[Dict[str, int]] = None,
        series_limits: Optional[Dict[str, int]] = None,
        weight_ml: Optional[float] = None,
        weight_content: Optional[float] = None,
        weight_preference: Optional[float] = None,
        weight_review: Optional[float] = None,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Generate hybrid recommendations for a user.
        
        Returns:
            DataFrame with top N recommendations and all scores
        """
        logger.info("=" * 60)
        logger.info("HYBRID RECOMMENDATION ENGINE")
        logger.info("=" * 60)
        
        assert self.catalog_df is not None, "Catalog not loaded"
        
        # Stage 1: Universal Filters
        logger.info("\n[Stage 1] Applying universal filters...")
        catalog_filtered = apply_universal_filters(
            self.catalog_df,
            sfw_only, exclude_early_access, min_reviews, min_review_score,
            price_max, release_year_min, release_year_max
        )
        
        # Exclude owned games
        owned_appids = set(owned_games_df['appid'].tolist())
        owned_names = set(owned_games_df['name'].dropna().unique()) if 'name' in owned_games_df.columns else set()
        
        logger.info(f"\n[Stage 1.5] Filtering owned games...")
        logger.info(f"  User owns {len(owned_appids)} games")
        
        owned_appids_int = set(int(appid) for appid in owned_appids)
        catalog_filtered['appid'] = catalog_filtered['appid'].astype(int)
        
        catalog_unowned = catalog_filtered[
            ~catalog_filtered['appid'].isin(owned_appids_int) & 
            ~catalog_filtered['name'].isin(owned_names)
        ].copy()
        
        logger.info(f"  Remaining after filtering owned: {len(catalog_unowned)} games")
        
        # Build user profiles
        logger.info(f"\n[Stage 2] Building user profiles...")
        user_tag_profile, user_genre_profile, disliked_tag_profile, disliked_genre_profile = \
            build_user_profiles(owned_games_df)
        
        # Stage 3: ML Predictions (BATCH - FAST!)
        logger.info(f"\n[Stage 3] Generating ML predictions (batch mode)...")
        if self.ml_predictor.is_ready():
            try:
                # Batch prediction: ONE call for all games (100x faster than apply)
                catalog_unowned['ml_score'] = self.ml_predictor.predict_engagement_batch(
                    catalog_unowned, owned_games_df
                )
                logger.info(f"  ✓ ML predictions: range {catalog_unowned['ml_score'].min():.1f}-{catalog_unowned['ml_score'].max():.1f}")
            except Exception as e:
                logger.error(f"  ❌ ML prediction failed: {e}")
                catalog_unowned['ml_score'] = 50.0
        else:
            logger.warning(f"  ⚠️  Using fallback scores (models not loaded)")
            catalog_unowned['ml_score'] = 50.0
        
        # Stage 4: Content Scoring
        logger.info(f"\n[Stage 4] Calculating content scores...")
        catalog_unowned['content_score'] = catalog_unowned.apply(
            lambda row: calculate_content_score(row, user_tag_profile, user_genre_profile),
            axis=1
        )
        logger.info(f"  ✓ Content scores: range {catalog_unowned['content_score'].min():.1f}-{catalog_unowned['content_score'].max():.1f}")
        
        # Stage 5: Preference Scoring
        logger.info(f"\n[Stage 5] Calculating preference scores...")
        catalog_unowned['preference_score'] = catalog_unowned.apply(
            lambda row: calculate_preference_score(
                row, user_tag_profile, user_genre_profile,
                disliked_tag_profile, disliked_genre_profile,
                boost_tags, boost_genres, dislike_tags, dislike_genres
            ),
            axis=1
        )
        logger.info(f"  ✓ Preference scores: range {catalog_unowned['preference_score'].min():.1f}-{catalog_unowned['preference_score'].max():.1f}")
        
        # Stage 6: Review Scoring
        logger.info(f"\n[Stage 6] Calculating review scores...")
        catalog_unowned['review_score'] = catalog_unowned.apply(
            calculate_review_score, axis=1
        )
        logger.info(f"  ✓ Review scores: range {catalog_unowned['review_score'].min():.1f}-{catalog_unowned['review_score'].max():.1f}")
        
        # Stage 7: Combine scores
        logger.info(f"\n[Stage 7] Combining scores...")
        weight_ml, weight_content, weight_preference, weight_review = self._determine_weights(
            weight_ml, weight_content, weight_preference, weight_review,
            user_tag_profile, user_genre_profile, boost_tags, boost_genres
        )
        
        # Store weights
        catalog_unowned['weight_ml_used'] = weight_ml
        catalog_unowned['weight_content_used'] = weight_content
        catalog_unowned['weight_preference_used'] = weight_preference
        catalog_unowned['weight_review_used'] = weight_review
        
        # Calculate hybrid score
        catalog_unowned['hybrid_score'] = (
            weight_ml * catalog_unowned['ml_score'] +
            weight_content * catalog_unowned['content_score'] +
            weight_preference * catalog_unowned['preference_score'] +
            weight_review * catalog_unowned['review_score']
        )
        logger.info(f"  ✓ Hybrid scores: range {catalog_unowned['hybrid_score'].min():.1f}-{catalog_unowned['hybrid_score'].max():.1f}")
        
        # Stage 8: Hard Exclusions
        logger.info(f"\n[Stage 8] Applying hard exclusions...")
        catalog_final = apply_hard_exclusions(
            catalog_unowned, hard_exclude_tags or [], hard_exclude_genres or []
        )
        
        # Stage 9: Diversity Filters
        if genre_limits or tag_limits or series_limits:
            logger.info(f"\n[Stage 9] Applying diversity filters...")
            catalog_final = apply_diversity_filters(
                catalog_final, genre_limits, tag_limits, series_limits
            )
        
        # Get top N (with deduplication)
        logger.info(f"\n[Stage 10] Selecting top {top_n} recommendations...")
        top_recommendations = self._deduplicate_and_select_top_n(catalog_final, top_n)
        
        logger.info(f"\n✓ Generated {len(top_recommendations)} recommendations")
        logger.info("=" * 60)
        
        return top_recommendations
    
    def _determine_weights(
        self,
        weight_ml: Optional[float],
        weight_content: Optional[float],
        weight_preference: Optional[float],
        weight_review: Optional[float],
        user_tag_profile: Dict,
        user_genre_profile: Dict,
        boost_tags: Optional[Dict],
        boost_genres: Optional[Dict]
    ) -> tuple[float, float, float, float]:
        """Determine final weights (custom or adaptive defaults)."""
        
        # If all custom weights provided, use them
        if all(w is not None for w in [weight_ml, weight_content, weight_preference, weight_review]):
            # Type assertions (we know they're not None after the check above)
            assert weight_ml is not None
            assert weight_content is not None
            assert weight_preference is not None
            assert weight_review is not None
            
            total = weight_ml + weight_content + weight_preference + weight_review
            if not (0.95 <= total <= 1.05):
                logger.warning(f"Weights sum to {total:.2f}, normalizing...")
                weight_ml /= total
                weight_content /= total
                weight_preference /= total
                weight_review /= total
            
            logger.info(f"  Using custom weights: ML={weight_ml:.0%}, Content={weight_content:.0%}, Pref={weight_preference:.0%}, Review={weight_review:.0%}")
            return weight_ml, weight_content, weight_preference, weight_review
        
        # Otherwise use adaptive defaults
        has_explicit_boosts = bool(boost_tags or boost_genres)
        has_loved_games = bool(user_tag_profile or user_genre_profile)
        has_meaningful_preferences = has_explicit_boosts or has_loved_games
        
        if has_meaningful_preferences:
            logger.info(f"  Using standard weights (preferences detected)")
            return WEIGHT_ML, WEIGHT_CONTENT, WEIGHT_PREFERENCE, WEIGHT_REVIEW
        else:
            # Redistribute preference weight
            redistribution = 1.0 / (1.0 - WEIGHT_PREFERENCE)
            wm = WEIGHT_ML * redistribution
            wc = WEIGHT_CONTENT * redistribution
            wr = WEIGHT_REVIEW * redistribution
            logger.info(f"  Using adaptive weights (no prefs): ML={wm:.0%}, Content={wc:.0%}, Review={wr:.0%}")
            return wm, wc, 0.0, wr
    
    def _deduplicate_and_select_top_n(self, df: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """Remove duplicate editions and select top N."""
        # Get top 2N to account for deduplication
        top_candidates = df.nlargest(top_n * 2, 'hybrid_score')
        
        # Normalize names (remove edition suffixes)
        edition_suffixes = [
            'Special Edition', 'Definitive Edition', 'Remastered', 'Remake',
            'Enhanced Edition', 'Complete Edition', 'GOTY', 'Game of the Year Edition',
            'Ultimate Edition', 'Deluxe Edition', 'Premium Edition', 'Gold Edition',
            'Anniversary Edition', 'Legendary Edition', 'Royal Edition', "Director's Cut",
            'Redux', 'HD', 'Legacy', 'VR Only', 'VR'
        ]
        
        def normalize_name(name):
            if pd.isna(name):
                return ""
            normalized = str(name).strip().rstrip(' :-')
            for suffix in edition_suffixes:
                for sep in [':', ' -', ' –', ' —', '']:
                    pattern = f"{sep} {suffix}"
                    if normalized.endswith(pattern):
                        normalized = normalized[:-len(pattern)].strip()
                        break
            return normalized.strip()
        
        top_candidates['normalized_name'] = top_candidates['name'].apply(normalize_name)
        
        # Deduplicate by normalized name (keep highest scoring)
        top_candidates = top_candidates.sort_values('hybrid_score', ascending=False).drop_duplicates(
            subset=['normalized_name'], keep='first'
        )
        
        # Drop temp column and take top N
        top_candidates = top_candidates.drop(columns=['normalized_name'])
        return top_candidates.head(top_n)
    
    def explain_recommendation(
        self,
        appid: int,
        owned_games_df: pd.DataFrame
    ) -> Dict:
        """Generate detailed explanation for a recommendation."""
        assert self.catalog_df is not None, "Catalog not loaded"
        
        game = self.catalog_df[self.catalog_df['appid'] == appid]
        if game.empty:
            raise ValueError(f"Game {appid} not found in catalog")
        
        game = game.iloc[0]
        
        # Build profiles
        user_tag_profile, user_genre_profile, disliked_tag_profile, disliked_genre_profile = \
            build_user_profiles(owned_games_df)
        
        # Calculate scores
        content_score = calculate_content_score(game, user_tag_profile, user_genre_profile)
        preference_score = calculate_preference_score(
            game, user_tag_profile, user_genre_profile,
            disliked_tag_profile, disliked_genre_profile
        )
        review_score = calculate_review_score(game)
        
        # ML score
        if self.ml_predictor.is_ready():
            try:
                ml_score = self.ml_predictor.predict_engagement(game, owned_games_df)
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")
                ml_score = 50.0
        else:
            ml_score = 50.0
        
        # Hybrid score
        hybrid_score = (
            WEIGHT_ML * ml_score +
            WEIGHT_CONTENT * content_score +
            WEIGHT_PREFERENCE * preference_score +
            WEIGHT_REVIEW * review_score
        )
        
        return {
            "appid": int(appid),
            "name": game['name'],
            "hybrid_score": round(hybrid_score, 2),
            "scores": {
                "ml": {"score": round(ml_score, 2), "weight": WEIGHT_ML},
                "content": {"score": round(content_score, 2), "weight": WEIGHT_CONTENT},
                "preference": {"score": round(preference_score, 2), "weight": WEIGHT_PREFERENCE},
                "review": {"score": round(review_score, 2), "weight": WEIGHT_REVIEW}
            }
        }
