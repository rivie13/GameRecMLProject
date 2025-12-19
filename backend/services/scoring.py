"""
Scoring functions for the recommendation system.

Contains:
- Content-based scoring
- Preference scoring
- Review scoring
- User profile building
"""
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .utils import parse_tags, parse_genre, NSFW_TAGS

logger = logging.getLogger(__name__)


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
            user_tag_profile[tag] = user_tag_profile.get(tag, 0) + playtime_weight
    
    # Build disliked tag profile (count occurrences)
    disliked_tag_profile = {}
    for _, game in disliked_games.iterrows():
        for tag in game['tags_dict'].keys():
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
            user_genre_profile[genre] = user_genre_profile.get(genre, 0) + playtime_weight
    
    # Build disliked genre profile
    disliked_genre_profile = {}
    for _, game in disliked_games.iterrows():
        for genre in game['genre_list']:
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
    
    Components:
    - Tag similarity: 55 points
    - Genre overlap: 25 points
    - Median playtime match: 20 points
    
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
        matching_score = 0.0
        total_user_weight = sum(user_tag_profile.values())
        
        for tag, votes in game_tags.items():
            if tag in user_tag_profile:
                tag_weight = user_tag_profile[tag]
                vote_factor = min(votes / 500, 1.0)
                matching_score += (tag_weight / total_user_weight) * vote_factor
        
        normalized_score = matching_score / 0.5
        tag_score = min(55, normalized_score * 55)
    
    score += tag_score
    
    # 2. Genre overlap (25 points)
    genre_score = 0.0
    game_genres = game_row['genre_list']
    if game_genres:
        for genre in game_genres:
            if genre in user_genre_profile:
                genre_score += user_genre_profile[genre]
        
        genre_score = min(25, genre_score * 25)
    
    score += genre_score
    
    # 3. Median playtime similarity (20 points)
    median_playtime = game_row.get('median_forever', 0)
    if pd.notna(median_playtime) and median_playtime > 0:
        median_hours = median_playtime / 60
        if median_hours >= 50:
            playtime_score = 20
        elif median_hours >= 20:
            playtime_score = 15
        elif median_hours >= 10:
            playtime_score = 10
        elif median_hours >= 5:
            playtime_score = 5
        else:
            playtime_score = 2
    else:
        playtime_score = 0
    
    score += playtime_score
    
    return max(0, score)


def calculate_preference_score(
    game_row: pd.Series,
    user_tag_profile: Dict[str, float],
    user_genre_profile: Dict[str, float],
    disliked_tag_profile: Dict[str, int],
    disliked_genre_profile: Dict[str, int],
    boost_tags: Optional[Dict[str, int]] = None,
    boost_genres: Optional[Dict[str, int]] = None,
    dislike_tags: Optional[Dict[str, int]] = None,
    dislike_genres: Optional[Dict[str, int]] = None
) -> float:
    """
    Calculate preference adjustments (0-100 scale).
    
    Combines auto-learned and user-specified preferences.
    
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
    
    # 1. Apply AUTO-LEARNED LIKES from loved games
    for tag in game_tags.keys():
        if tag in user_tag_profile:
            boost = user_tag_profile[tag] * 20
            score += boost
    
    for genre in game_genres:
        if genre in user_genre_profile:
            boost = user_genre_profile[genre] * 15
            score += boost
    
    # 2. Apply AUTO-LEARNED DISLIKES
    for tag in game_tags.keys():
        if tag in disliked_tag_profile:
            score -= 10
    
    for genre in game_genres:
        if genre in disliked_genre_profile:
            score -= 8
    
    # 3. Apply USER-SPECIFIED BOOSTS
    for tag in game_tags.keys():
        if tag in boost_tags:
            score += boost_tags[tag]
    
    for genre in game_genres:
        if genre in boost_genres:
            score += boost_genres[genre]
    
    # 4. Apply USER-SPECIFIED DISLIKES
    for tag in game_tags.keys():
        if tag in dislike_tags:
            score += dislike_tags[tag]  # Already negative
    
    for genre in game_genres:
        if genre in dislike_genres:
            score += dislike_genres[genre]  # Already negative
    
    # Clamp to 0-100 range
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
        quality_multiplier = 2.5
    elif review_percentage >= 90:
        quality_multiplier = 2.0
    elif review_percentage >= 80:
        quality_multiplier = 1.5
    elif review_percentage >= 70:
        quality_multiplier = 1.0
    elif review_percentage >= 60:
        quality_multiplier = 0.5
    else:
        quality_multiplier = 0.1
    
    # Volume bonus (logarithmic)
    volume_score = np.log10(total + 1) * quality_multiplier
    
    # Normalize to 0-100
    return min(100, (volume_score / 15) * 100)
