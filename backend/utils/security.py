"""
Security utilities for JWT token generation, validation, and password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the data to encode in the token (e.g., {"sub": steam_id})
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded token payload as dict, or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Note:
        This is not used for Steam OAuth but included for future use cases
        (e.g., admin accounts, API keys, etc.)
    """
    return pwd_context.hash(password)


def extract_steam_id_from_claimed_id(claimed_id: str) -> Optional[int]:
    """
    Extract Steam ID from OpenID claimed ID.
    
    Steam OpenID returns claimed ID in format:
    https://steamcommunity.com/openid/id/<steamid>
    
    Args:
        claimed_id: Full OpenID claimed ID URL
        
    Returns:
        Steam ID as integer, or None if invalid format
    """
    try:
        # Expected format: https://steamcommunity.com/openid/id/76561197960287930
        if "/openid/id/" in claimed_id:
            steam_id = claimed_id.split("/openid/id/")[-1]
            return int(steam_id)
        return None
    except (ValueError, IndexError):
        return None
