"""
ML Prediction Module for engagement scoring.

Handles:
- Loading trained Random Forest model
- Feature engineering for predictions
- Engagement score prediction (0-100)
- Batch predictions for performance
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np
import pandas as pd

from .utils import parse_tags, parse_genre

logger = logging.getLogger(__name__)

# Model paths
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODELS_DIR / "random_forest_enhanced.pkl"
SCALER_PATH = MODELS_DIR / "feature_scaler_enhanced.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names_enhanced.pkl"


class MLPredictor:
    """Handles ML-based engagement predictions."""
    
    def __init__(self):
        """Initialize and load ML models."""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self._load_models()
    
    def _load_models(self):
        """Load the trained ML model, scaler, and feature names."""
        try:
            if MODEL_PATH.exists() and SCALER_PATH.exists() and FEATURE_NAMES_PATH.exists():
                logger.info(f"Loading ML model from {MODEL_PATH}")
                self.model = joblib.load(MODEL_PATH)
                
                logger.info(f"Loading feature scaler from {SCALER_PATH}")
                self.scaler = joblib.load(SCALER_PATH)
                
                logger.info(f"Loading feature names from {FEATURE_NAMES_PATH}")
                self.feature_names = joblib.load(FEATURE_NAMES_PATH)
                
                logger.info(f"✓ ML models loaded: {len(self.feature_names)} features")
            else:
                logger.warning("⚠️  ML models not found. Will use fallback scores.")
                logger.warning(f"  Expected: {MODEL_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {e}")
            self.model = None
            self.scaler = None
            self.feature_names = None
    
    def is_ready(self) -> bool:
        """Check if ML models are loaded and ready."""
        return all([self.model is not None, self.scaler is not None, self.feature_names is not None])
    
    def predict_engagement_batch(self, games_df: pd.DataFrame, owned_games_df: pd.DataFrame) -> pd.Series:
        """
        Predict engagement scores (0-100) for multiple games at once (FAST).
        
        Uses VECTORIZED pandas operations (like the notebook) instead of row-by-row loops.
        This is 100x+ faster because:
        - No iterrows() loops
        - Pure vectorized operations
        - ONE batch prediction
        
        Args:
            games_df: DataFrame of candidate games to score
            owned_games_df: User's owned games library
            
        Returns:
            Series of engagement scores (0-100), indexed by games_df index
        """
        if not self.is_ready() or len(games_df) == 0:
            return pd.Series([50.0] * len(games_df), index=games_df.index)
        
        try:
            # Type assertions
            assert self.model is not None
            assert self.scaler is not None
            assert self.feature_names is not None
            
            # Build ALL features using vectorized operations (like X_test in notebook)
            features_df = self._build_features_vectorized(games_df, owned_games_df)
            
            # Ensure we have all required features (fill missing with 0)
            for feat in self.feature_names:
                if feat not in features_df.columns:
                    features_df[feat] = 0.0
            
            # Select features in the EXACT order the model expects
            features_df = features_df[self.feature_names]
            
            # Scale ALL features at once (just like X_test_scaled = scaler.transform(X_test))
            features_scaled = self.scaler.transform(features_df)
            
            # ONE batch prediction for ALL games (just like model.predict(X_test_scaled))
            predictions = self.model.predict(features_scaled)
            
            # Convert to 0-100 scale and clip
            scores = np.clip(predictions * 100, 0, 100)
            
            return pd.Series(scores, index=games_df.index)
            
        except Exception as e:
            logger.error(f"Batch ML prediction failed: {e}", exc_info=True)
            return pd.Series([50.0] * len(games_df), index=games_df.index)
    
    def predict_engagement(self, game_row: pd.Series, owned_games_df: pd.DataFrame) -> float: # type: ignore
        """
        Predict engagement score (0-100) for a game.
        
        Args:
            game_row: Candidate game to score
            owned_games_df: User's owned games library
            
        Returns:
            Engagement score from 0-100
        """
        if not self.is_ready():
            return 50.0  # Fallback
        
        try:
            # Type assertions (is_ready() already verified these aren't None)
            assert self.model is not None
            assert self.scaler is not None
            assert self.feature_names is not None
            
            # Build user profile features
            user_features = self._build_user_features(owned_games_df)
            
            # Build game features
            game_features = self._build_game_features(game_row)
            
            # Combine
            combined_features = {**user_features, **game_features}
            
            # Create a dictionary with ALL features (fill missing with 0)
            # This avoids DataFrame fragmentation warnings
            full_features = {feat: combined_features.get(feat, 0.0) for feat in self.feature_names}
            
            # Create DataFrame with correct feature order (no need to reorder)
            feature_df = pd.DataFrame([full_features], columns=self.feature_names)
            
            # Scale features
            features_scaled = self.scaler.transform(feature_df)
            
            # Convert back to DataFrame with feature names to avoid sklearn warning
            features_scaled_df = pd.DataFrame(features_scaled, columns=self.feature_names)
            
            # Predict (model returns 0-1 scale)
            prediction = self.model.predict(features_scaled_df)[0]
            
            # Convert to 0-100 and clip
            score = np.clip(prediction * 100, 0, 100)
                        # Debug: log if score seems suspicious
            if score >= 99.9 or score <= 0.1:
                logger.debug(f"Unusual ML score {score:.1f} for game {game_row.get('name', 'unknown')}")
                logger.debug(f"  Raw prediction: {prediction:.4f}")
                logger.debug(f"  Non-zero features: {sum(1 for v in combined_features.values() if v != 0)}/{len(combined_features)}")
                return float(score)
            
        except Exception as e:
            logger.debug(f"ML prediction failed for {game_row.get('name', 'unknown')}: {e}")
            return 50.0  # Fallback
    
    def _build_features_vectorized(self, games_df: pd.DataFrame, owned_games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Build ALL features efficiently - vectorized where possible, optimized loops otherwise.
        
        This matches the notebook approach: build full feature matrix then predict in ONE batch.
        """
        # Start with vectorized numeric features
        result_df = pd.DataFrame(index=games_df.index)
        
        # === USER FEATURES (constant for all games) ===
        user_features = self._build_user_features(owned_games_df)
        for feat_name, value in user_features.items():
            result_df[feat_name] = value
        
        # === GAME FEATURES (vectorized) ===
        result_df['game_price'] = games_df['price'].fillna(0) / 100.0
        result_df['game_positive_reviews'] = games_df['positive'].fillna(0).astype(int)
        result_df['game_negative_reviews'] = games_df['negative'].fillna(0).astype(int)
        result_df['game_total_reviews'] = result_df['game_positive_reviews'] + result_df['game_negative_reviews']
        
        # Review score (avoid division by zero)
        result_df['game_review_score'] = result_df['game_positive_reviews'] / result_df['game_total_reviews']
        result_df['game_review_score'] = result_df['game_review_score'].fillna(0.5)
        
        result_df['game_median_playtime'] = games_df['median_forever'].fillna(0).astype(float)
        
        # === GENRE/TAG FEATURES (optimized loop - unavoidable for sparse multi-hot encoding) ===
        # This IS similar to the notebook - genres/tags need iteration for multi-hot encoding
        for idx, row in games_df.iterrows():
            # Genres
            if 'genre' in row and pd.notna(row['genre']):
                genres = parse_genre(row['genre'])
                for genre in genres:
                    feat_name = f"game_genre_{genre.replace(' ', '_').replace('-', '_').lower()}"
                    if feat_name not in result_df.columns:
                        result_df[feat_name] = 0.0
                    result_df.loc[idx, feat_name] = 1.0 # type: ignore
            
            # Tags
            if 'tags' in row and pd.notna(row['tags']):
                tags_dict = parse_tags(row['tags'])
                for tag in list(tags_dict.keys())[:100]:
                    feat_name = f"game_tag_{tag.replace(' ', '_').replace('-', '_').lower()}"
                    if feat_name not in result_df.columns:
                        result_df[feat_name] = 0.0
                    result_df.loc[idx, feat_name] = 1.0 # type: ignore
        
        return result_df
    
    def _build_game_features_parallel(self, games_df: pd.DataFrame, user_features: Dict[str, float]) -> list:
        """Build game features in parallel using threading."""
        assert self.feature_names is not None
        
        def process_row(row_data):
            idx, row = row_data
            game_feat = self._build_game_features(row)
            combined = {**user_features, **game_feat}
            # Fill missing features with 0
            full_features = {feat: combined.get(feat, 0.0) for feat in self.feature_names} # type: ignore
            return full_features
        
        # Use ThreadPoolExecutor for parallel processing
        # sklearn models are thread-safe for predictions
        with ThreadPoolExecutor(max_workers=8) as executor:
            game_features_list = list(executor.map(process_row, games_df.iterrows()))
        
        return game_features_list
    
    def _build_user_features(self, owned_games_df: pd.DataFrame) -> Dict[str, float]:
        """Build user profile features from owned games library."""
        features = {}
        
        # Basic stats
        features['user_total_games'] = len(owned_games_df)
        features['user_avg_playtime'] = owned_games_df['playtime_forever'].mean() if len(owned_games_df) > 0 else 0
        features['user_total_playtime'] = owned_games_df['playtime_forever'].sum()
        
        # Genre preferences (weighted by playtime)
        all_genres = []
        for _, game in owned_games_df.iterrows():
            if 'genre' in game and pd.notna(game['genre']):
                genres = parse_genre(game['genre'])
                weight = game.get('playtime_forever', 0) / 60  # hours
                all_genres.extend([(g, weight) for g in genres])
        
        genre_weights = {}
        for genre, weight in all_genres:
            genre_weights[genre] = genre_weights.get(genre, 0) + weight
        
        # Top 50 genres as features
        top_genres = sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)[:50]
        for genre, weight in top_genres:
            feat_name = f"user_genre_{genre.replace(' ', '_').replace('-', '_').lower()}"
            features[feat_name] = weight
        
        # Tag preferences (weighted by playtime)
        all_tags = []
        for _, game in owned_games_df.iterrows():
            if 'tags' in game and pd.notna(game['tags']):
                tags_dict = parse_tags(game['tags'])
                weight = game.get('playtime_forever', 0) / 60
                all_tags.extend([(tag, weight) for tag in tags_dict.keys()])
        
        tag_weights = {}
        for tag, weight in all_tags:
            tag_weights[tag] = tag_weights.get(tag, 0) + weight
        
        # Top 100 tags as features
        top_tags = sorted(tag_weights.items(), key=lambda x: x[1], reverse=True)[:100]
        for tag, weight in top_tags:
            feat_name = f"user_tag_{tag.replace(' ', '_').replace('-', '_').lower()}"
            features[feat_name] = weight
        
        return features
    
    def _build_game_features(self, game_row: pd.Series) -> Dict[str, float]:
        """Build feature vector for a candidate game."""
        features = {}
        
        # Basic game stats
        features['game_price'] = float(game_row.get('price', 0)) / 100.0
        features['game_positive_reviews'] = int(game_row.get('positive', 0))
        features['game_negative_reviews'] = int(game_row.get('negative', 0))
        features['game_total_reviews'] = features['game_positive_reviews'] + features['game_negative_reviews']
        
        if features['game_total_reviews'] > 0:
            features['game_review_score'] = features['game_positive_reviews'] / features['game_total_reviews']
        else:
            features['game_review_score'] = 0.5
        
        features['game_median_playtime'] = float(game_row.get('median_forever', 0))
        
        # Genres as binary features
        if 'genre' in game_row and pd.notna(game_row['genre']):
            genres = parse_genre(game_row['genre'])
            for genre in genres:
                feat_name = f"game_genre_{genre.replace(' ', '_').replace('-', '_').lower()}"
                features[feat_name] = 1.0
        
        # Tags as binary features
        if 'tags' in game_row and pd.notna(game_row['tags']):
            tags_dict = parse_tags(game_row['tags'])
            for tag in list(tags_dict.keys())[:100]:
                feat_name = f"game_tag_{tag.replace(' ', '_').replace('-', '_').lower()}"
                features[feat_name] = 1.0
        
        return features
