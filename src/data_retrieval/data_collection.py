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
        """
        Fetch detailed metadata for a game from Store API
        
        Returns: dict with game info (genres, categories, description, etc.)
        """
        url = f"{self.store_url}/appdetails"
        params = {'appids': appid}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if str(appid) in data and data[str(appid)]['success']:
                game_data = data[str(appid)]['data']
                
                # Extract key fields
                metadata = {
                    'appid': appid,
                    'name': game_data.get('name', ''),
                    'type': game_data.get('type', ''),
                    'short_description': game_data.get('short_description', ''),
                    'detailed_description': game_data.get('detailed_description', ''),
                    'developers': game_data.get('developers', []),
                    'publishers': game_data.get('publishers', []),
                    'genres': [g.get('description', '') for g in game_data.get('genres', [])],
                    'categories': [c.get('description', '') for c in game_data.get('categories', [])],
                    'release_date': game_data.get('release_date', {}).get('date', ''),
                    'metacritic_score': game_data.get('metacritic', {}).get('score', None),
                    'recommendations': game_data.get('recommendations', {}).get('total', 0),
                    'price_overview': game_data.get('price_overview', {}),
                    'platforms': game_data.get('platforms', {})
                }
                return metadata
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game metadata for {appid}: {e}")
            return None
    
    def get_game_reviews_sentiment(self, appid):
        """
        Fetch review sentiment for a game from Store API
        
        Returns: dict with review scores and sentiment
        """
        url = f"{self.store_url[:-4]}/appreviews/{appid}"  # Remove '/api' from base URL
        params = {
            'json': 1,
            'filter': 'recent',
            'num_per_page': 0  # We just want the summary, not individual reviews
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') == 1:
                summary = data.get('query_summary', {})
                return {
                    'appid': appid,
                    'review_score': summary.get('review_score', 0),
                    'review_score_desc': summary.get('review_score_desc', 'No Reviews'),
                    'total_positive': summary.get('total_positive', 0),
                    'total_negative': summary.get('total_negative', 0),
                    'total_reviews': summary.get('total_reviews', 0)
                }
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching review sentiment for {appid}: {e}")
            return None
    
    def get_steamspy_game_list(self, page=0):
        """
        Fetch game list from SteamSpy (alternative game catalog source)
        
        Args:
            page: Page number for pagination (default 0 = all games)
        
        Returns: dict of games from SteamSpy
        """
        params = {
            'request': 'all',
            'page': page
        }
        
        try:
            response = requests.get(self.steamspy_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SteamSpy game list: {e}")
            return {}
    
    def enrich_game_data(self, games_df, fetch_metadata=True, fetch_reviews=True, delay=1.5, use_catalog=True):
        """
        Enrich user's game library with metadata and review sentiment
        
        Args:
            games_df: DataFrame with user's games (from get_owned_games)
            fetch_metadata: Whether to fetch game metadata
            fetch_reviews: Whether to fetch review sentiment
            delay: Delay between API calls to avoid rate limiting (seconds)
            use_catalog: Whether to use existing catalog data first
        
        Returns: Enriched DataFrame
        """
        enriched_data = []
        total_games = len(games_df)
        
        # Load existing catalog if available
        catalog = pd.DataFrame()
        if use_catalog:
            catalog_path = 'data/steam_catalog_detailed.csv'
            if os.path.exists(catalog_path):
                try:
                    catalog = pd.read_csv(catalog_path)
                    catalog['appid'] = catalog['appid'].astype(int)
                    print(f"📦 Loaded existing catalog: {len(catalog)} games")
                except Exception as e:
                    print(f"Warning: Could not load catalog: {e}")
                    catalog = pd.DataFrame()
        
        print(f"\nEnriching data for {total_games} games...")
        
        # Count how many games are already in catalog
        games_in_catalog = 0
        games_need_api = 0
        if not catalog.empty:
            games_in_catalog = len(games_df[games_df['appid'].isin(catalog['appid'])])
            games_need_api = total_games - games_in_catalog
            print(f"✅ {games_in_catalog} games found in catalog (instant, no API calls)")
            print(f"🔄 {games_need_api} games missing from catalog (will fetch from API)")
            if games_need_api > 0:
                estimated_time = games_need_api * 3  # ~3 seconds per game (2 calls × 1.5s delay)
                print(f"⏱️  Estimated time: ~{estimated_time} seconds ({estimated_time/60:.1f} minutes)")
        else:
            games_need_api = total_games
            print(f"⚠️  No catalog found - will fetch all {total_games} games from API")
            estimated_time = total_games * 3
            print(f"⏱️  Estimated time: ~{estimated_time} seconds ({estimated_time/60:.1f} minutes)")
        print()
        
        for idx, game in games_df.iterrows():
            appid = game['appid']
            game_data = game.to_dict()
            
            # Check catalog first - if game is in catalog, use that data and skip API calls!
            has_catalog_data = False
            if not catalog.empty and appid in catalog['appid'].values:
                catalog_row = catalog[catalog['appid'] == appid].iloc[0]
                # Merge catalog data (has everything we need: genre, tags, positive/negative reviews, etc.)
                game_data.update(catalog_row.to_dict())
                has_catalog_data = True
                print(f"[{idx+1}/{total_games}] ✅ {game.get('name', 'Unknown')} (AppID: {appid}) - Found in catalog, skipping API")
            else:
                # Game NOT in catalog - need to fetch from API
                print(f"[{idx+1}/{total_games}] 🔄 {game.get('name', 'Unknown')} (AppID: {appid}) - Not in catalog, fetching API...")
                
                # Fetch metadata (type, description, developers, genres, categories, etc.)
                if fetch_metadata:
                    metadata = self.get_game_metadata(appid)
                    if metadata:
                        game_data.update(metadata)
                    time.sleep(delay)  # Rate limiting
                
                # Fetch review sentiment (review_score, total_positive/negative, etc.)
                if fetch_reviews:
                    reviews = self.get_game_reviews_sentiment(appid)
                    if reviews:
                        game_data.update(reviews)
                    time.sleep(delay)  # Rate limiting
            
            enriched_data.append(game_data)
        
        # Summary
        print("\n" + "="*60)
        print("ENRICHMENT COMPLETE")
        print("="*60)
        if not catalog.empty:
            api_calls_made = games_need_api * 2  # metadata + reviews
            api_calls_saved = games_in_catalog * 2
            print(f"✅ Games from catalog: {games_in_catalog} (instant)")
            print(f"🔄 Games from API: {games_need_api}")
            print(f"💰 API calls saved: {api_calls_saved} (would have been {api_calls_made + api_calls_saved} total)")
            if games_in_catalog > 0:
                time_saved = games_in_catalog * 3 / 60  # minutes
                print(f"⏱️  Time saved: ~{time_saved:.1f} minutes")
        
        # Create DataFrame and remove unused columns
        df = pd.DataFrame(enriched_data)
        
        # Drop columns from Steam API that are not needed and are mostly empty
        # These would only be populated for games NOT in catalog (very few)
        columns_to_drop = [
            'type', 'short_description', 'detailed_description',  # Not used in ML model
            'developers', 'publishers',  # Duplicates of 'developer' and 'publisher' from catalog
            'genres',  # Duplicate of 'genre' from catalog
            'categories',  # Not used in ML model
            'release_date', 'metacritic_score', 'recommendations',  # Not used in ML model
            'price_overview', 'platforms',  # Not used in ML model (have 'price' from catalog)
            'review_score', 'review_score_desc',  # Not used (have 'positive'/'negative' from catalog)
            'total_positive', 'total_negative', 'total_reviews'  # Duplicates of catalog data
        ]
        
        # Drop columns that exist in the dataframe
        existing_cols_to_drop = [col for col in columns_to_drop if col in df.columns]
        if existing_cols_to_drop:
            df = df.drop(columns=existing_cols_to_drop)
            print(f"🧹 Cleaned up {len(existing_cols_to_drop)} unused columns")
        
        return df
    
    def collect_user_library(self, enrich=False):
        """
        Collect user's game library with optional enrichment
        
        Args:
            enrich: If True, fetch metadata and reviews for each game (slow!)
        
        Returns: DataFrame with user's games
        """
        print("=" * 60)
        print("STEAM DATA COLLECTION - User Library")
        print("=" * 60)
        
        # Get owned games
        print("\n[1/1] Fetching owned games from Steam Web API...")
        owned_games = self.get_owned_games()
        
        if owned_games.empty:
            print("❌ No games found or error occurred")
            return owned_games
        
        print(f"✅ Found {len(owned_games)} games")
        
        # Save basic library
        owned_games.to_csv('data/owned_games.csv', index=False)
        print(f"💾 Saved to data/owned_games.csv")
        
        # Optional: Enrich with metadata and reviews
        if enrich:
            print("\n[Optional] Enriching game data with metadata and reviews...")
            enriched_games = self.enrich_game_data(owned_games)
            enriched_games.to_csv('data/owned_games_enriched.csv', index=False)
            print(f"💾 Saved enriched data to data/owned_games_enriched.csv")
            return enriched_games
        
        return owned_games

def main():
    """Main execution function - Collect user games and enrich with catalog data"""
    if not STEAM_API_KEY or not STEAM_ID:
        print("Error: Please set STEAM_API_KEY and STEAM_ID in your .env file")
        return
    
    collector = SteamDataCollector(STEAM_API_KEY, STEAM_ID)
    
    # Collect user library WITH enrichment (uses catalog, minimal API calls)
    print("🎮 Collecting your games and enriching with catalog data...")
    print("⚡ Using existing catalog - should be fast!")
    
    library = collector.collect_user_library(enrich=True)
    
    if not library.empty:
        print("\n" + "="*60)
        print("✅ DATA COLLECTION COMPLETE!")
        print("="*60)
        print(f"📊 Total games collected: {len(library)}")
        print(f"💾 Saved to: data/owned_games_enriched.csv")
        print(f"\n🎯 Top 5 most played:")
        # Use 'genre' from catalog instead of 'genres' (which was removed)
        top_5 = library.nlargest(5, 'playtime_forever')[['name', 'playtime_forever', 'playtime_hours', 'genre']]
        print(top_5.to_string(index=False))
    else:
        print("❌ Failed to collect data")

if __name__ == "__main__":
    main()
