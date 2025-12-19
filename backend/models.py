"""
SQLAlchemy ORM models for database tables.
"""
from sqlalchemy import (
    BigInteger, Column, Integer, String, Float, 
    DateTime, ForeignKey, Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class User(Base):
    """User model - stores Steam user information."""
    __tablename__ = "users"
    
    steam_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    profile_url = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_sync = Column(DateTime, nullable=True)
    settings = Column(JSON, nullable=True)  # Store user preferences as JSON
    
    # Relationships
    games = relationship("UserGame", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(steam_id={self.steam_id}, username='{self.username}')>"


class UserGame(Base):
    """UserGame model - stores user's owned games with playtime and engagement."""
    __tablename__ = "user_games"
    
    id = Column(Integer, primary_key=True, index=True)
    user_steam_id = Column(
        BigInteger, 
        ForeignKey("users.steam_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    appid = Column(Integer, nullable=False, index=True)
    playtime_hours = Column(Float, nullable=False, default=0.0)
    playtime_category = Column(String(50), nullable=True)  # 'loved', 'played', 'tried', 'unplayed'
    engagement_score = Column(Float, nullable=True)
    last_played = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="games")
    
    # Unique constraint: one row per user-game combination
    __table_args__ = (
        UniqueConstraint('user_steam_id', 'appid', name='uq_user_game'),
        Index('ix_user_games_user_appid', 'user_steam_id', 'appid'),
    )
    
    def __repr__(self):
        return f"<UserGame(user_id={self.user_steam_id}, appid={self.appid}, hours={self.playtime_hours})>"


class Recommendation(Base):
    """Recommendation model - stores generated recommendations with scores."""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_steam_id = Column(
        BigInteger, 
        ForeignKey("users.steam_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    appid = Column(Integer, nullable=False, index=True)
    recommendation_mode = Column(String(50), nullable=False)  # 'hybrid', 'ml', 'content', 'preference'
    score = Column(Float, nullable=False)
    ml_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    preference_score = Column(Float, nullable=True)
    review_score = Column(Float, nullable=True)
    generated_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_recommendations_user_mode', 'user_steam_id', 'recommendation_mode'),
        Index('ix_recommendations_generated_at', 'generated_at'),
    )
    
    def __repr__(self):
        return f"<Recommendation(user_id={self.user_steam_id}, appid={self.appid}, score={self.score})>"


class Feedback(Base):
    """Feedback model - stores user feedback on recommendations."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_steam_id = Column(
        BigInteger, 
        ForeignKey("users.steam_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    appid = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'clicked', 'dismissed', 'wishlisted', 'purchased'
    recommendation_mode = Column(String(50), nullable=True)
    score_at_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    
    # Indexes for analytics
    __table_args__ = (
        Index('ix_feedback_user_appid', 'user_steam_id', 'appid'),
        Index('ix_feedback_action', 'action'),
        Index('ix_feedback_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Feedback(user_id={self.user_steam_id}, appid={self.appid}, action='{self.action}')>"


class CatalogCache(Base):
    """CatalogCache model - caches Steam game catalog metadata."""
    __tablename__ = "catalog_cache"
    
    appid = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    release_year = Column(Integer, nullable=True)  # NULL if not available (~89% of games)
    game_metadata = Column(JSON, nullable=True)  # Store all game metadata as JSON (renamed from 'metadata' to avoid SQLAlchemy conflict)
    last_updated = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<CatalogCache(appid={self.appid}, name='{self.name}')>"
