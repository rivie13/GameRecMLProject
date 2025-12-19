"""
Recommendations router - Generate and explain game recommendations.
"""
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import pandas as pd

from database import get_db
from models import User, UserGame  # type: ignore
from schemas import RecommendationResponse
from services.recommender import HybridRecommender
from routers.auth import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Initialize recommender (singleton)
recommender = HybridRecommender()


@router.get("/{steam_id}", response_model=List[Dict[str, Any]])
async def get_recommendations(
    steam_id: int,
    # Filter parameters
    mode: str = Query(default="hybrid", description="Mode: hybrid, ml, content, preference"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of recommendations"),
    sfw_only: bool = Query(default=True, description="Filter NSFW content"),
    exclude_early_access: bool = Query(default=True, description="Exclude Early Access games"),
    min_reviews: int = Query(default=5000, ge=0, description="Minimum review count"),
    min_review_score: int = Query(default=70, ge=0, le=100, description="Minimum review score %"),
    price_max: Optional[float] = Query(default=None, ge=0, description="Maximum price"),
    release_year_min: Optional[int] = Query(default=None, ge=1980, le=2030),
    release_year_max: Optional[int] = Query(default=None, ge=1980, le=2030),
    # User preference parameters
    boost_tags: Optional[str] = Query(default=None, description="Comma-separated tags to boost, e.g. 'Open World:15,Multiplayer:10'"),
    boost_genres: Optional[str] = Query(default=None, description="Comma-separated genres to boost, e.g. 'RPG:10,Action:5'"),
    dislike_tags: Optional[str] = Query(default=None, description="Comma-separated tags to penalize, e.g. 'Horror:-15'"),
    dislike_genres: Optional[str] = Query(default=None, description="Comma-separated genres to penalize, e.g. 'Sports:-10'"),
    hard_exclude_tags: Optional[str] = Query(default=None, description="Comma-separated tags to exclude completely"),
    hard_exclude_genres: Optional[str] = Query(default=None, description="Comma-separated genres to exclude completely"),
    # Weight tuning (hybrid mode only)
    weight_ml: Optional[float] = Query(default=None, ge=0, le=1, description="ML weight (0-1, default 0.35)"),
    weight_content: Optional[float] = Query(default=None, ge=0, le=1, description="Content weight (0-1, default 0.35)"),
    weight_preference: Optional[float] = Query(default=None, ge=0, le=1, description="Preference weight (0-1, default 0.20)"),
    weight_review: Optional[float] = Query(default=None, ge=0, le=1, description="Review weight (0-1, default 0.10)"),
    # Diversity parameters (JSON format)
    genre_limits: Optional[str] = Query(default=None, description='Genre limits as JSON, e.g. {"Action": 5, "RPG": 3}'),
    tag_limits: Optional[str] = Query(default=None, description='Tag limits as JSON, e.g. {"Souls-like": 3, "Open-World": 4}'),
    series_limits: Optional[str] = Query(default=None, description='Series limits as JSON, e.g. {"Dark Souls": 2, "Fallout": 2}'),
    # Database and auth
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate game recommendations for a user.
    
    Modes:
    - **hybrid**: Combines ML + content + preferences + reviews (recommended)
    - **ml**: ML predictions only
    - **content**: Content-based similarity only
    - **preference**: User preferences only
    
    Filters:
    - Universal filters applied first (SFW, Early Access, min reviews, etc.)
    - User preferences boost/penalize certain tags/genres
    - Hard exclusions remove games completely
    
    Returns:
        List of recommended games with scores and metadata
    """
    # Authorization
    if current_user.steam_id != steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only get recommendations for yourself"
        )
    
    # Fetch user's owned games
    owned_games = db.query(UserGame).filter(
        UserGame.user_steam_id == steam_id
    ).all()
    
    if not owned_games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No games found. Please sync your library first."
        )
    
    # Convert to DataFrame for recommender
    owned_games_data = []
    for game in owned_games:
        owned_games_data.append({
            "appid": int(game.appid),  # Ensure integer type
            "playtime_forever": game.playtime_hours * 60,  # Convert back to minutes
            "playtime_hours": game.playtime_hours,
            "playtime_category": game.playtime_category,
            "engagement_score": game.engagement_score
        })
    
    owned_games_df = pd.DataFrame(owned_games_data)
    
    # Log for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"User {steam_id} owns {len(owned_games_df)} games")
    logger.info(f"ALL owned appids from database: {sorted(owned_games_df['appid'].tolist())}")
    
    # Check for specific game
    if 22490 in owned_games_df['appid'].values:
        logger.info(f"✓ AppID 22490 (Fallout: New Vegas) IS in database for user {steam_id}")
        fnv_data = owned_games_df[owned_games_df['appid'] == 22490].iloc[0]
        logger.info(f"  Fallout: New Vegas playtime: {fnv_data['playtime_hours']} hours ({fnv_data['playtime_forever']} minutes)")
    else:
        logger.warning(f"⚠️  AppID 22490 (Fallout: New Vegas) is NOT in database for user {steam_id}")
        logger.warning(f"  This game should be filtered from recommendations but isn't in the user's library data")
    
    # Need to enrich with catalog metadata (tags, genres, etc.)
    # Load catalog and merge
    catalog = recommender.catalog_df
    assert catalog is not None, "Catalog not loaded in recommender"
    owned_games_df = owned_games_df.merge(
        catalog[['appid', 'name', 'tags', 'genre', 'positive', 'negative', 'median_forever']],
        on='appid',
        how='left'
    )
    
    # Parse preference parameters
    boost_tags_dict = _parse_preference_param(boost_tags) if boost_tags else {}
    boost_genres_dict = _parse_preference_param(boost_genres) if boost_genres else {}
    dislike_tags_dict = _parse_preference_param(dislike_tags) if dislike_tags else {}
    dislike_genres_dict = _parse_preference_param(dislike_genres) if dislike_genres else {}
    hard_exclude_tags_list = hard_exclude_tags.split(',') if hard_exclude_tags else []
    hard_exclude_genres_list = hard_exclude_genres.split(',') if hard_exclude_genres else []
    
    # Parse diversity parameters from JSON
    genre_limits_dict = None
    if genre_limits:
        try:
            genre_limits_dict = json.loads(genre_limits)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid genre_limits JSON format"
            )
    
    tag_limits_dict = None
    if tag_limits:
        try:
            tag_limits_dict = json.loads(tag_limits)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_limits JSON format"
            )
    
    series_limits_dict = None
    if series_limits:
        try:
            series_limits_dict = json.loads(series_limits)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid series_limits JSON format"
            )
    
    # Generate recommendations
    try:
        recommendations_df = recommender.generate_recommendations(
            owned_games_df=owned_games_df,
            sfw_only=sfw_only,
            exclude_early_access=exclude_early_access,
            min_reviews=min_reviews,
            min_review_score=min_review_score,
            release_year_min=release_year_min,
            release_year_max=release_year_max,
            boost_tags=boost_tags_dict,
            boost_genres=boost_genres_dict,
            dislike_tags=dislike_tags_dict,
            dislike_genres=dislike_genres_dict,
            hard_exclude_tags=hard_exclude_tags_list,
            hard_exclude_genres=hard_exclude_genres_list,
            genre_limits=genre_limits_dict,
            tag_limits=tag_limits_dict,
            series_limits=series_limits_dict,
            weight_ml=weight_ml,
            weight_content=weight_content,
            weight_preference=weight_preference,
            weight_review=weight_review,
            top_n=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
    
    # Convert to response format
    recommendations = []
    for _, game in recommendations_df.iterrows():
        appid = int(game['appid'])
        recommendations.append({
            "appid": appid,
            "name": game['name'],
            "developer": game.get('developer', 'Unknown Developer'),
            "header_image": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            "hybrid_score": round(float(game['hybrid_score']), 2),
            "ml_score": round(float(game.get('ml_score', 0)), 2),
            "content_score": round(float(game.get('content_score', 0)), 2),
            "preference_score": round(float(game.get('preference_score', 0)), 2),
            "review_score": round(float(game.get('review_score', 0)), 2),
            "positive_reviews": int(game.get('positive', 0)),
            "negative_reviews": int(game.get('negative', 0)),
            "review_percentage": round(
                (game.get('positive', 0) / (game.get('positive', 0) + game.get('negative', 0) + 0.01)) * 100, 1
            ),
            "median_playtime": float(game.get('median_forever', 0)),
            "price": float(game.get('price', 0)) / 100.0,  # Convert cents to dollars
            "tags": game.get('tags', '{}'),
            "genres": game.get('genre', ''),
            "steam_url": f"https://store.steampowered.com/app/{appid}/"
        })
    
    return recommendations


@router.get("/{steam_id}/explain/{appid}")
async def explain_recommendation(
    steam_id: int,
    appid: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed explanation for why a game was recommended.
    
    Returns:
        - Individual score breakdowns (ML, content, preference, review)
        - Matching tags and genres
        - Disliked tags/genres (if any)
        - Why the game scored the way it did
    """
    # Authorization
    if current_user.steam_id != steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only get explanations for your own recommendations"
        )
    
    # Fetch user's owned games
    owned_games = db.query(UserGame).filter(
        UserGame.user_steam_id == steam_id
    ).all()
    
    if not owned_games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No games found. Please sync your library first."
        )
    
    # Convert to DataFrame
    owned_games_data = []
    for game in owned_games:
        owned_games_data.append({
            "appid": int(game.appid),  # Ensure integer type
            "playtime_forever": game.playtime_hours * 60,
            "playtime_hours": game.playtime_hours,
            "playtime_category": game.playtime_category,
            "engagement_score": game.engagement_score
        })
    
    owned_games_df = pd.DataFrame(owned_games_data)
    
    # Enrich with catalog metadata
    catalog = recommender.catalog_df
    assert catalog is not None, "Catalog not loaded in recommender"
    owned_games_df = owned_games_df.merge(
        catalog[['appid', 'name', 'tags', 'genre', 'positive', 'negative', 'median_forever']],
        on='appid',
        how='left'
    )
    
    # Generate explanation
    try:
        explanation = recommender.explain_recommendation(appid, owned_games_df)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )
    
    return explanation


def _parse_preference_param(param_str: str) -> Dict[str, int]:
    """
    Parse preference parameter string into dictionary.
    
    Format: "tag1:10,tag2:15,tag3:-5"
    Returns: {"tag1": 10, "tag2": 15, "tag3": -5}
    """
    result = {}
    for pair in param_str.split(','):
        if ':' in pair:
            key, value = pair.split(':', 1)
            try:
                result[key.strip()] = int(value.strip())
            except ValueError:
                continue  # Skip invalid entries
    return result
