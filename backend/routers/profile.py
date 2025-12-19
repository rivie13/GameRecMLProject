"""
Profile router - User profile management and Steam library sync.
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from database import get_db
from models import User, UserGame  # type: ignore
from schemas import ProfileResponse, ProfileStatsResponse, SyncRequest, SyncResponse
from services.steam_api import steam_api
from routers.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/{steam_id}", response_model=ProfileResponse)
async def get_profile(
    steam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's gaming profile.
    
    Returns:
        - Basic user info (username, avatar, etc.)
        - Game library summary
        - Last sync timestamp
    """
    # Authorization: users can only access their own profile
    if current_user.steam_id != steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile"
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get game library stats
    game_count = db.query(func.count(UserGame.id)).filter(
        UserGame.user_steam_id == steam_id
    ).scalar()
    
    total_playtime = db.query(func.sum(UserGame.playtime_hours)).filter(
        UserGame.user_steam_id == steam_id
    ).scalar() or 0.0
    
    return ProfileResponse(
        steam_id=user.steam_id,
        username=user.username,
        profile_url=user.profile_url,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        last_sync=user.last_sync,
        total_games=game_count,
        total_playtime_hours=round(total_playtime, 1),
        settings=user.settings or {}
    )


@router.get("/{steam_id}/stats", response_model=ProfileStatsResponse)
async def get_profile_stats(
    steam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed statistics for visualizations.
    
    Returns:
        - Playtime distribution by category
        - Top 10 most played games
        - Genre distribution
        - Engagement metrics
        - Full game data with metadata for charts
    """
    # Authorization
    if current_user.steam_id != steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile"
        )
    
    # Get all user games
    games = db.query(UserGame).filter(
        UserGame.user_steam_id == steam_id
    ).all()
    
    if not games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No games found. Please sync your library first."
        )
    
    # Calculate playtime categories
    loved = sum(1 for g in games if g.playtime_hours >= 50)
    played = sum(1 for g in games if 10 <= g.playtime_hours < 50)
    tried = sum(1 for g in games if 0 < g.playtime_hours < 10)
    unplayed = sum(1 for g in games if g.playtime_hours == 0)
    
    # Get top 10 most played
    top_games = sorted(games, key=lambda x: x.playtime_hours, reverse=True)[:10]
    
    # Calculate total playtime
    total_hours = sum(g.playtime_hours for g in games)
    
    # Determine gaming style based on play patterns
    if total_hours == 0:
        gaming_style = "Collector"
    elif loved > len(games) * 0.3:  # 30%+ loved games
        gaming_style = "Completionist"
    elif unplayed > len(games) * 0.5:  # 50%+ unplayed
        gaming_style = "Hoarder"
    elif tried > len(games) * 0.5:  # 50%+ tried but not finished
        gaming_style = "Explorer"
    elif played > len(games) * 0.4:  # 40%+ moderately played
        gaming_style = "Casual Gamer"
    else:
        gaming_style = "Enthusiast"
    
    # Load catalog metadata for visualization charts
    from services.recommender import HybridRecommender
    
    # Use singleton pattern to get recommender instance
    try:
        recommender = HybridRecommender()
        catalog = recommender.catalog_df
    except Exception as e:
        # If recommender fails to load, continue without catalog enrichment
        import logging
        logging.getLogger(__name__).warning(f"Failed to load recommender catalog: {e}")
        catalog = None
    
    # Build enriched game list for visualizations
    enriched_games = []
    top_genre_playtime = {}
    
    # Fetch fresh game names from Steam API for games not in catalog
    steam_games_cache = {}
    try:
        owned_games_data = await steam_api.get_owned_games(steam_id)
        if owned_games_data:
            for steam_game in owned_games_data.get("games", []):
                steam_games_cache[steam_game["appid"]] = steam_game.get("name", f"Game {steam_game['appid']}")
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to fetch game names from Steam API: {e}")
    
    for game in games:
        # Find game in catalog
        game_data = catalog[catalog['appid'] == game.appid] if catalog is not None else None
        
        if game_data is not None and len(game_data) > 0:
            game_info = game_data.iloc[0]
            game_name = game_info.get('name', f"Game {game.appid}")
            genres = game_info.get('genre_list', [])
            tags = list(game_info.get('tags_dict', {}).keys()) if isinstance(game_info.get('tags_dict'), dict) else []
            release_year = game_info.get('release_year') if not pd.isna(game_info.get('release_year')) else None
            
            # Track genre playtime for top_genre calculation
            for genre in genres:
                top_genre_playtime[genre] = top_genre_playtime.get(genre, 0) + game.playtime_hours
        else:
            # Fallback: Try Steam API cache, then fall back to appid
            game_name = steam_games_cache.get(game.appid, f"Game {game.appid}")
            genres = []
            tags = []
            release_year = None
        
        enriched_games.append({
            "appid": game.appid,
            "name": game_name,
            "playtime_hours": round(game.playtime_hours, 2),
            "playtime_category": game.playtime_category,
            "engagement_score": round(game.engagement_score, 1) if game.engagement_score else None,
            "genres": genres,
            "tags": tags[:20],  # Limit to top 20 tags per game
            "release_year": int(release_year) if release_year else None
        })
    
    # Calculate top genre by playtime
    if top_genre_playtime:
        top_genre = max(top_genre_playtime.items(), key=lambda x: x[1])[0]
    else:
        top_genre = "N/A"
    
    return ProfileStatsResponse(
        steam_id=steam_id,
        total_games=len(games),
        playtime_distribution={
            "loved_50plus": loved,
            "played_10_50": played,
            "tried_under10": tried,
            "unplayed": unplayed
        },
        top_10_games=[
            {
                "appid": g.appid,
                "playtime_hours": round(g.playtime_hours, 1),
                "playtime_category": g.playtime_category
            }
            for g in top_games
        ],
        total_playtime_hours=round(total_hours, 1),
        top_genre=top_genre,
        gaming_style=gaming_style,
        games=enriched_games,  # Full game data for visualizations
        feature_importance=None  # TODO: Load from ML model if available
    )


@router.post("/{steam_id}/sync", response_model=SyncResponse)
async def sync_library(
    steam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync user's Steam library.
    
    Steps:
    1. Fetch owned games from Steam API
    2. Update database with latest playtime data
    3. Calculate engagement scores and categories
    4. Update user's last_sync timestamp
    
    Returns:
        - Number of games synced
        - Timestamp of sync
        - Summary stats
    """
    # Authorization
    if current_user.steam_id != steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only sync your own library"
        )
    
    # Fetch owned games from Steam API
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"=" * 60)
    logger.info(f"STARTING LIBRARY SYNC FOR STEAM ID: {steam_id}")
    logger.info(f"=" * 60)
    
    owned_games_data = await steam_api.get_owned_games(steam_id)
    if not owned_games_data:
        logger.error(f"Failed to fetch games from Steam API for user {steam_id}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch games from Steam API"
        )
    
    games_list = owned_games_data.get("games", [])
    if not games_list:
        logger.warning(f"No games found in Steam library for user {steam_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No games found in Steam library"
        )
    
    logger.info(f"✓ Steam API returned {len(games_list)} games")
    
    # Log all appids being synced
    all_appids = [game["appid"] for game in games_list]
    logger.info(f"All appids from Steam API: {sorted(all_appids)}")
    
    # Check for specific problematic game
    if 22490 in all_appids:
        logger.info(f"✓ AppID 22490 (Fallout: New Vegas) IS in Steam API response")
    else:
        logger.warning(f"⚠️  AppID 22490 (Fallout: New Vegas) is NOT in Steam API response")
        logger.warning(f"   This game will not be in the database and will be recommended")
    
    # Update or create user games
    logger.info(f"\nSyncing games to database...")
    synced_count = 0
    updated_count = 0
    created_count = 0
    
    for game in games_list:
        appid = game.get("appid")
        playtime_minutes = game.get("playtime_forever", 0)
        playtime_hours = playtime_minutes / 60.0
        
        # Determine playtime category
        if playtime_hours >= 50:
            category = "loved"
        elif playtime_hours >= 10:
            category = "played"
        elif playtime_hours > 0:
            category = "tried"
        else:
            category = "unplayed"
        
        # Calculate engagement score (0-100)
        # Log-normalized playtime score (0-60 points)
        if playtime_hours > 0:
            playtime_score = min(60, (playtime_hours / 100) * 60)  # Simplified
        else:
            playtime_score = 0
        
        engagement_score = playtime_score  # Can be enhanced with achievement data later
        
        # Upsert game
        existing_game = db.query(UserGame).filter(
            UserGame.user_steam_id == steam_id,
            UserGame.appid == appid
        ).first()
        
        if existing_game:
            existing_game.playtime_hours = playtime_hours
            existing_game.playtime_category = category
            existing_game.engagement_score = engagement_score
            updated_count += 1
        else:
            new_game = UserGame(
                user_steam_id=steam_id,
                appid=appid,
                playtime_hours=playtime_hours,
                playtime_category=category,
                engagement_score=engagement_score
            )
            db.add(new_game)
            created_count += 1
        
        synced_count += 1
    
    logger.info(f"Sync summary: {synced_count} total, {created_count} new, {updated_count} updated")
    
    # Update user's last_sync timestamp
    user = db.query(User).filter(User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.last_sync = datetime.utcnow()
    
    # Commit all changes
    logger.info(f"Committing {synced_count} games to database...")
    db.commit()
    logger.info(f"✓ Database commit successful")
    
    # Verify what's in the database after sync
    db_game_count = db.query(UserGame).filter(UserGame.user_steam_id == steam_id).count()
    logger.info(f"Database now contains {db_game_count} games for user {steam_id}")
    
    # Check if 22490 made it to the database
    fnv_in_db = db.query(UserGame).filter(
        UserGame.user_steam_id == steam_id,
        UserGame.appid == 22490
    ).first()
    
    if fnv_in_db:
        logger.info(f"✓ AppID 22490 (Fallout: New Vegas) IS now in database")
    else:
        logger.warning(f"⚠️  AppID 22490 (Fallout: New Vegas) is NOT in database")
    
    logger.info(f"=" * 60)
    logger.info(f"SYNC COMPLETE")
    logger.info(f"=" * 60)
    
    return SyncResponse(
        success=True,
        synced_count=synced_count,
        synced_at=user.last_sync,
        message=f"Successfully synced {synced_count} games ({created_count} new, {updated_count} updated)"
    )
