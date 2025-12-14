"""
Steam Data Collection Module

Fetches data from Steam APIs:
- User's game library + playtime (Steam Web API)
- Game metadata (Store API - genres, categories, descriptions)
- Review sentiment (Store API - positive/negative/mixed ratings)
- Game catalog (SteamSpy API - optional)
"""

import os
import requests
import json
import time
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM_ID = os.getenv('STEAM_ID')

class SteamDataCollector:
    """Collects data from Steam APIs (Web API + Store API)"""
    
    def __init__(self, api_key, steam_id):
        self.api_key = api_key
        self.steam_id = steam_id
        self.base_url = "https://api.steampowered.com"
        self.store_url = "https://store.steampowered.com/api"
        self.steamspy_url = "https://steamspy.com/api.php"
        
    def get_owned_games(self):
        """Fetch all owned games with playtime"""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': self.steam_id,
            'include_appinfo': 1,
            'include_played_free_games': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']
                df = pd.DataFrame(games)
                df['playtime_hours'] = df['playtime_forever'] / 60  # Convert minutes to hours
                return df
            return pd.DataFrame()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching owned games: {e}")
            return pd.DataFrame()
    
    def get_game_metadata(self, appid):
        """Fetch detailed information about a specific game"""
        url = f"https://store.steampowered.com/api/appdetails"
        params = {'appids': appid}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if str(appid) in data and data[str(appid)]['success']:
                return data[str(appid)]['data']
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game details for {appid}: {e}")
            return None
    
    def collect_all_data(self):
        """Collect all available user data"""
        print("Collecting Steam data...")
        
        # Get owned games
        print("Fetching owned games...")
        owned_games = self.get_owned_games()
        
        if not owned_games.empty:
            print(f"Found {len(owned_games)} games")
            
            # Save to CSV
            owned_games.to_csv('data/owned_games.csv', index=False)
            print("Saved owned games to data/owned_games.csv")
        else:
            print("No games found or error occurred")
        
        # Get reviews (placeholder)
        reviews = self.get_user_reviews()
        
        # Get wishlist (placeholder)
        wishlist = self.get_wishlist()
        
        return {
            'owned_games': owned_games,
            'reviews': reviews,
            'wishlist': wishlist
        }

def main():
    """Main execution function"""
    if not STEAM_API_KEY or not STEAM_ID:
        print("Error: Please set STEAM_API_KEY and STEAM_ID in your .env file")
        return
    
    collector = SteamDataCollector(STEAM_API_KEY, STEAM_ID)
    data = collector.collect_all_data()
    
    print("\nData collection complete!")
    print(f"Owned games: {len(data['owned_games'])} records")
    print(f"Reviews: {len(data['reviews'])} records")
    print(f"Wishlist: {len(data['wishlist'])} records")

if __name__ == "__main__":
    main()
