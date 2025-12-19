"""
Authentication routes for Steam OpenID login.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_db
from models import User # type: ignore
from schemas import Token, LoginResponse, UserResponse
from services.steam_api import steam_api
from utils.security import (
    create_access_token,
    decode_access_token,
    extract_steam_id_from_claimed_id,
)
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# HTTP Bearer scheme for JWT token authentication in Swagger UI
security = HTTPBearer()


# ============================================================
# Steam OpenID Login Flow
# ============================================================

@router.get("/steam/login")
async def steam_login():
    """
    Initiate Steam OpenID login.
    
    Redirects user directly to Steam login page.
    User will be redirected back to /api/auth/steam/callback after login.
    """
    # Generate callback URL (where Steam will redirect after login)
    callback_url = f"{settings.backend_url}/api/auth/steam/callback"
    
    # Get Steam OpenID login URL
    login_url = steam_api.get_openid_login_url(callback_url)
    
    # Redirect directly to Steam
    return RedirectResponse(url=login_url, status_code=302)


@router.get("/steam/callback")
async def steam_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Steam OpenID callback after user authentication.
    
    This endpoint:
    1. Verifies the OpenID response from Steam
    2. Extracts the user's Steam ID
    3. Fetches user profile from Steam API
    4. Creates or updates user in database
    5. Generates JWT token
    6. Returns login response with token
    
    Query parameters are automatically sent by Steam after authentication.
    """
    # Get all query parameters from Steam callback
    params = dict(request.query_params)
    
    # Verify OpenID response with Steam
    steam_id_str = await steam_api.verify_openid_response(params)
    
    if not steam_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Steam authentication failed or was denied"
        )
    
    try:
        steam_id = int(steam_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Steam ID format"
        )
    
    print(f"[AUTH] Steam OpenID verified - Steam ID from OpenID: {steam_id}")
    
    # Fetch user profile from Steam API
    player_data = await steam_api.get_player_summary(steam_id)
    
    print(f"[AUTH] Steam API returned player data: {player_data}")
    
    if not player_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile from Steam"
        )
    
    # Check if user exists in database
    user = db.query(User).filter(User.steam_id == steam_id).first()
    
    if user:
        # Update existing user
        print(f"[AUTH] Found existing user in DB: steam_id={user.steam_id}, username={user.username}")
        user.username = player_data["username"]
        user.profile_url = player_data["profile_url"]
        user.avatar_url = player_data["avatar_url"]
    else:
        # Create new user
        print(f"[AUTH] Creating NEW user with steam_id={steam_id}")
        user = User(
            steam_id=steam_id,
            username=player_data["username"],
            profile_url=player_data["profile_url"],
            avatar_url=player_data["avatar_url"]
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    print(f"[AUTH] After commit - user.steam_id={user.steam_id}, user.profile_url={user.profile_url}")
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(steam_id)},
        expires_delta=access_token_expires
    )
    
    # Redirect to frontend callback with token and user data
    # Frontend will parse the query params and store in localStorage
    from urllib.parse import urlencode
    import json
    
    user_data = {
        "steam_id": str(user.steam_id),  # Send as string to avoid JavaScript number precision loss
        "username": user.username,
        "profile_url": user.profile_url,
        "avatar_url": user.avatar_url
    }
    
    print(f"[AUTH] Sending user_data to frontend: {user_data}")
    
    query_params = urlencode({
        "token": access_token,
        "user": json.dumps(user_data)
    })
    
    redirect_url = f"{settings.frontend_url}/auth/callback?{query_params}"
    
    print(f"[AUTH] Redirecting to: {redirect_url[:100]}...")
    
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/logout")
async def logout():
    """
    Logout user.
    
    Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token from storage.
    
    This endpoint is included for completeness and can be used for:
    - Logging logout events
    - Token blacklisting (future enhancement)
    - Clearing server-side sessions (if added later)
    """
    return {
        "message": "Logged out successfully",
        "detail": "Remove the JWT token from client storage"
    }


# ============================================================
# Token Dependency for Protected Routes
# ============================================================

async def get_current_user_from_token(
    token: Annotated[str, Depends(lambda: None)],
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user from JWT token.
    
    Use this as a dependency in protected routes:
    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        ...
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    # Extract Steam ID from token
    steam_id_str: str | None = payload.get("sub")
    if not steam_id_str:
        raise credentials_exception
    
    try:
        steam_id = int(steam_id_str)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.steam_id == steam_id).first()
    if not user:
        raise credentials_exception
    
    return user


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate user from JWT token.
    
    Token is automatically extracted from Authorization header.
    Expected header format: "Bearer <token>"
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    if not token:
        raise credentials_exception
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    # Extract Steam ID from token
    steam_id_str: str | None = payload.get("sub")
    if not steam_id_str:
        raise credentials_exception
    
    try:
        steam_id = int(steam_id_str)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.steam_id == steam_id).first()
    if not user:
        raise credentials_exception
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user's information.
    
    This is a protected route that requires a valid JWT token.
    Use this to verify authentication and get user details.
    
    Example:
        GET /api/auth/me
        Headers: Authorization: Bearer <token>
    """
    return UserResponse.model_validate(current_user)
