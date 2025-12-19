"""
Steam API integration for authentication and data retrieval.
Implements Steam OpenID authentication flow.
"""

import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from config import settings


class SteamAPI:
    """
    Steam Web API client for authentication and data retrieval.
    """
    
    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
    STEAM_API_BASE_URL = "https://api.steampowered.com"
    
    def __init__(self):
        self.api_key = settings.steam_api_key
        self.backend_url = settings.backend_url
        
    def get_openid_login_url(self, return_url: str) -> str:
        """
        Generate Steam OpenID login URL.
        
        Args:
            return_url: Callback URL for Steam to redirect after authentication
            
        Returns:
            Full Steam OpenID login URL
            
        Steam OpenID flow:
        1. User clicks "Login with Steam"
        2. User is redirected to Steam OpenID URL
        3. User logs in on Steam and approves
        4. Steam redirects back to our callback URL with OpenID response
        """
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": return_url,
            "openid.realm": self.backend_url,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        return f"{self.STEAM_OPENID_URL}?{urlencode(params)}"
    
    async def verify_openid_response(self, params: Dict[str, str]) -> Optional[str]:
        """
        Verify Steam OpenID authentication response.
        
        Args:
            params: Query parameters from Steam callback
            
        Returns:
            Steam ID (as string) if valid, None if invalid
            
        Verification process:
        1. Change mode from "id_res" to "check_authentication"
        2. Send all params back to Steam
        3. Steam responds with "is_valid:true" if authentic
        
        Security: This prevents attackers from forging Steam authentication
        by requiring server-side verification with Steam's servers.
        """
        # Validate required OpenID parameters are present
        required_params = ["openid.mode", "openid.claimed_id", "openid.identity"]
        if not all(param in params for param in required_params):
            return None
        
        # Prepare verification params
        verification_params = params.copy()
        verification_params["openid.mode"] = "check_authentication"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.STEAM_OPENID_URL,
                    data=verification_params
                )
                
                # Check if Steam confirms validity
                if "is_valid:true" in response.text:
                    # Extract Steam ID from claimed_id
                    claimed_id = params.get("openid.claimed_id", "")
                    if "/openid/id/" in claimed_id:
                        steam_id = claimed_id.split("/openid/id/")[-1]
                        # Validate Steam ID format (should be numeric and 17 digits)
                        if steam_id.isdigit() and len(steam_id) == 17:
                            return steam_id
                        
                return None
                
        except Exception as e:
            print(f"Error verifying OpenID response: {e}")
            return None
    
    async def get_player_summary(self, steam_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch player summary from Steam API.
        
        Args:
            steam_id: Steam user ID
            
        Returns:
            Dictionary containing player data (username, avatar, profile_url)
            or None if request fails
            
        API: ISteamUser/GetPlayerSummaries/v2
        Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_.28v0002.29
        """
        url = f"{self.STEAM_API_BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            "key": self.api_key,
            "steamids": str(steam_id)
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                players = data.get("response", {}).get("players", [])
                
                if players:
                    player = players[0]
                    return {
                        "steam_id": player.get("steamid"),
                        "username": player.get("personaname"),
                        "profile_url": player.get("profileurl"),
                        "avatar_url": player.get("avatarfull"),
                    }
                    
                return None
                
        except Exception as e:
            print(f"Error fetching player summary: {e}")
            return None
    
    async def get_owned_games(self, steam_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch user's owned games from Steam API.
        
        Args:
            steam_id: Steam user ID
            
        Returns:
            Dictionary containing games data or None if request fails
            
        API: IPlayerService/GetOwnedGames/v1
        Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetOwnedGames_.28v0001.29
        """
        url = f"{self.STEAM_API_BASE_URL}/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": str(steam_id),
            "include_appinfo": 1,
            "include_played_free_games": 1,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("response", {})
                
        except Exception as e:
            print(f"Error fetching owned games: {e}")
            return None


# Singleton instance
steam_api = SteamAPI()
