"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


# ============================================================
# Authentication Schemas
# ============================================================

class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    steam_id: Optional[int] = None


class LoginResponse(BaseModel):
    """Response after successful Steam login."""
    user: "UserResponse"
    access_token: str
    token_type: str = "bearer"


# ============================================================
# User Schemas
# ============================================================

class UserBase(BaseModel):
    """Base user schema."""
    steam_id: int
    username: str
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response."""
    created_at: datetime
    last_sync: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# User Game Schemas
# ============================================================

class UserGameBase(BaseModel):
    """Base user game schema."""
    appid: int
    playtime_hours: float = 0.0
    playtime_category: Optional[str] = None
    engagement_score: Optional[float] = None


class UserGameCreate(UserGameBase):
    """Schema for adding a game to user's library."""
    user_steam_id: int


class UserGameResponse(UserGameBase):
    """Schema for user game response."""
    id: int
    user_steam_id: int
    last_played: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Recommendation Schemas
# ============================================================

class RecommendationBase(BaseModel):
    """Base recommendation schema."""
    appid: int
    recommendation_mode: str
    score: float
    ml_score: Optional[float] = None
    content_score: Optional[float] = None
    preference_score: Optional[float] = None
    review_score: Optional[float] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation."""
    user_steam_id: int


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response."""
    id: int
    user_steam_id: int
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(BaseModel):
    """Schema for recommendation request with filters."""
    mode: str = Field(default="hybrid", description="Recommendation mode: hybrid, ml, content, preference")
    limit: int = Field(default=20, ge=1, le=100, description="Number of recommendations")
    min_reviews: int = Field(default=100, ge=0, description="Minimum number of reviews")
    min_score: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum review score (0-1)")
    price_max: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    exclude_early_access: bool = Field(default=False, description="Exclude Early Access games")
    sfw_only: bool = Field(default=True, description="Only show SFW games")
    release_year_min: Optional[int] = Field(default=None, ge=1980, le=2030)
    release_year_max: Optional[int] = Field(default=None, ge=1980, le=2030)


# ============================================================
# Feedback Schemas
# ============================================================

class FeedbackBase(BaseModel):
    """Base feedback schema."""
    appid: int
    action: str  # 'clicked', 'dismissed', 'wishlisted', 'purchased'
    recommendation_mode: Optional[str] = None
    score_at_time: Optional[float] = None


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""
    user_steam_id: int


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    id: int
    user_steam_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Catalog Cache Schemas
# ============================================================

class CatalogCacheBase(BaseModel):
    """Base catalog cache schema."""
    appid: int
    name: str
    release_year: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CatalogCacheCreate(CatalogCacheBase):
    """Schema for creating catalog cache entry."""
    pass


class CatalogCacheResponse(CatalogCacheBase):
    """Schema for catalog cache response."""
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Profile & Stats Schemas
# ============================================================

class ProfileResponse(BaseModel):
    """Schema for user profile response."""
    steam_id: int
    username: str
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_sync: Optional[datetime] = None
    total_games: int
    total_playtime_hours: float
    settings: Dict[str, Any] = {}


class ProfileStatsResponse(BaseModel):
    """Schema for user profile statistics."""
    steam_id: int
    total_games: int
    total_playtime_hours: float
    playtime_distribution: Dict[str, int]  # {'loved_50plus': 10, 'played_10_50': 50, 'tried_under10': 100, 'unplayed': 50}
    top_10_games: list[Dict[str, Any]]
    top_genre: str  # Most played genre by hours ("N/A" if not available)
    gaming_style: str  # User's gaming style based on play patterns


class SyncRequest(BaseModel):
    """Schema for library sync request."""
    pass  # No body needed, just POST to endpoint


class SyncResponse(BaseModel):
    """Schema for library sync response."""
    success: bool
    synced_count: int
    synced_at: datetime
    message: str


class VisualizationDataResponse(BaseModel):
    """Schema for visualization data."""
    playtime_histogram: list[Dict[str, Any]]
    top_games: list[Dict[str, Any]]
    genre_count: list[Dict[str, Any]]
    genre_playtime: list[Dict[str, Any]]
    engagement_scatter: Optional[list[Dict[str, Any]]] = None
    release_timeline: Optional[list[Dict[str, Any]]] = None


# ============================================================
# Health Check Schema
# ============================================================

class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    database: str
    version: str = "1.0.0"
