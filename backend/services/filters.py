"""
Filtering logic for the recommendation system.

Contains:
- Universal filters (NSFW, Early Access, reviews, price, etc.)
- Hard exclusions (specific tags/genres to completely avoid)
- Diversity filters (limit genres, tags, series)
"""
import logging
from typing import Dict, List, Optional

import pandas as pd

from .utils import NSFW_TAGS, META_GENRES

logger = logging.getLogger(__name__)


def apply_universal_filters(
    catalog_df: pd.DataFrame,
    sfw_only: bool,
    exclude_early_access: bool,
    min_reviews: int,
    min_review_score: int,
    price_max: Optional[float] = None,
    release_year_min: Optional[int] = None,
    release_year_max: Optional[int] = None
) -> pd.DataFrame:
    """Apply universal quality and appropriateness filters."""
    filtered = catalog_df.copy()
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
    
    # Price filter
    if price_max is not None:
        before = len(filtered)
        price_cents = price_max * 100
        filtered = filtered[
            (filtered['price'] <= price_cents) | (filtered['price'] == 0)
        ]
        logger.info(f"  Max price filter (${price_max}): {before} → {len(filtered)} games")
    
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
            filtered['release_year'] >= release_year_min
        ]
        logger.info(f"  Min year filter ({release_year_min}): {before} → {len(filtered)} games")
    
    if release_year_max is not None:
        before = len(filtered)
        filtered = filtered[
            filtered['release_year'] <= release_year_max
        ]
        logger.info(f"  Max year filter ({release_year_max}): {before} → {len(filtered)} games")
    
    logger.info(f"✓ Universal filters complete: {initial_count} → {len(filtered)} games")
    return filtered


def apply_hard_exclusions(
    df: pd.DataFrame,
    exclude_tags: List[str],
    exclude_genres: List[str]
) -> pd.DataFrame:
    """Completely remove games with specified tags or genres."""
    if not exclude_tags and not exclude_genres:
        return df
    
    initial_count = len(df)
    
    if exclude_tags:
        df = df[~df['tags_dict'].apply(
            lambda tags: any(tag in exclude_tags for tag in tags.keys())
        )]
        logger.info(f"  Excluded {len(exclude_tags)} tags: {initial_count} → {len(df)} games")
    
    if exclude_genres:
        df = df[~df['genre_list'].apply(
            lambda genres: any(genre in exclude_genres for genre in genres)
        )]
        logger.info(f"  Excluded {len(exclude_genres)} genres: {initial_count} → {len(df)} games")
    
    return df


def apply_diversity_filters(
    df: pd.DataFrame,
    genre_limits: Optional[Dict[str, int]] = None,
    tag_limits: Optional[Dict[str, int]] = None,
    series_limits: Optional[Dict[str, int]] = None
) -> pd.DataFrame:
    """
    Apply diversity filters to limit representation of genres/tags/series.
    
    Args:
        df: DataFrame with recommendations sorted by hybrid_score (descending)
        genre_limits: Dict of genre: max_count
        tag_limits: Dict of tag: max_count
        series_limits: Dict of series: max_count
        
    Returns:
        Filtered DataFrame maintaining score order
    """
    if not genre_limits and not tag_limits and not series_limits:
        return df
    
    logger.info("Applying diversity filters...")
    initial_count = len(df)
    
    # Track counts
    genre_counts = {}
    tag_counts = {}
    series_counts = {}
    
    # Filter row by row, maintaining order
    filtered_rows = []
    
    for idx, row in df.iterrows():
        include = True
        
        # Check genre limits
        if genre_limits:
            for genre in row['genre_list']:
                if genre in genre_limits:
                    if genre_counts.get(genre, 0) >= genre_limits[genre]:
                        include = False
                        break
        
        # Check tag limits
        if include and tag_limits:
            for tag in row['tags_dict'].keys():
                if tag in tag_limits:
                    if tag_counts.get(tag, 0) >= tag_limits[tag]:
                        include = False
                        break
        
        # Check series limits (simple name matching)
        if include and series_limits:
            for series_name, limit in series_limits.items():
                if series_name.lower() in row['name'].lower():
                    if series_counts.get(series_name, 0) >= limit:
                        include = False
                        break
        
        if include:
            filtered_rows.append(row)
            
            # Update counts
            for genre in row['genre_list']:
                if genre in (genre_limits or {}):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            for tag in row['tags_dict'].keys():
                if tag in (tag_limits or {}):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            for series_name in (series_limits or {}).keys():
                if series_name.lower() in row['name'].lower():
                    series_counts[series_name] = series_counts.get(series_name, 0) + 1
    
    result = pd.DataFrame(filtered_rows)
    logger.info(f"  Diversity filters: {initial_count} → {len(result)} games")
    
    if genre_limits:
        logger.info(f"  Genre counts: {genre_counts}")
    if tag_limits:
        logger.info(f"  Tag counts: {tag_counts}")
    if series_limits:
        logger.info(f"  Series counts: {series_counts}")
    
    return result
