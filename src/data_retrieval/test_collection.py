"""
Test script for data collection
Usage: python src/test_collection.py
"""
import os
from dotenv import load_dotenv
from data_collection import SteamDataCollector

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('STEAM_API_KEY')
    steam_id = os.getenv('STEAM_ID')
    
    if not api_key or not steam_id:
        print("❌ Error: STEAM_API_KEY or STEAM_ID not found!")
        print("Please create a .env file with your API credentials")
        print("You can copy .env.example and fill in your values")
        return
    
    print(f"✅ Loaded credentials")
    print(f"Steam ID: {steam_id}")
    print(f"API Key: {api_key[:10]}...")
    
    # Create collector
    collector = SteamDataCollector(api_key, steam_id)
    
    # Collect user library (without enrichment first - faster)
    print("\n" + "="*60)
    print("TEST 1: Fetch user library (basic)")
    print("="*60)
    library = collector.collect_user_library(enrich=False)
    
    if not library.empty:
        print(f"\n📊 Summary:")
        print(f"Total games: {len(library)}")
        print(f"Total playtime: {library['playtime_forever'].sum() / 60:.1f} hours")
        print(f"\nTop 5 most played games:")
        print(library.nlargest(5, 'playtime_forever')[['name', 'playtime_forever']])
        
        # Optional: Test enrichment on a few games
        print("\n" + "="*60)
        print("TEST 2: Enrich a few games (metadata + reviews)")
        print("="*60)
        print("Testing with top 3 most played games...")
        
        top_games = library.nlargest(3, 'playtime_forever')
        enriched = collector.enrich_game_data(top_games, fetch_metadata=True, fetch_reviews=True)
        
        print("\n📊 Enriched data sample:")
        print(enriched[['name', 'playtime_forever', 'genres', 'review_score_desc']].to_string())
    else:
        print("❌ Failed to fetch library")

if __name__ == "__main__":
    main()
