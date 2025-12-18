"""
Get detailed Steam game catalog with tags, genres, and languages using multithreading
This is MUCH slower than get_steam_catalog.py but includes all metadata

Usage: python src/get_detailed_catalog.py
"""
import os
import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import json

# Thread-safe counter
progress_lock = Lock()
progress = {'count': 0, 'total': 0, 'failed': 0}

def fetch_game_details(appid):
    """Fetch detailed info for a single game from SteamSpy"""
    url = "https://steamspy.com/api.php"
    params = {'request': 'appdetails', 'appid': appid}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Update progress
        with progress_lock:
            progress['count'] += 1
            if progress['count'] % 100 == 0:
                print(f"   Progress: {progress['count']}/{progress['total']} games "
                      f"({progress['count']/progress['total']*100:.1f}%) - "
                      f"Failed: {progress['failed']}")
        
        return {
            'appid': int(appid),
            'name': data.get('name', 'Unknown'),
            'developer': data.get('developer', ''),
            'publisher': data.get('publisher', ''),
            'score_rank': data.get('score_rank', ''),
            'owners': data.get('owners', ''),
            'average_forever': data.get('average_forever', 0),
            'average_2weeks': data.get('average_2weeks', 0),
            'median_forever': data.get('median_forever', 0),
            'median_2weeks': data.get('median_2weeks', 0),
            'positive': data.get('positive', 0),
            'negative': data.get('negative', 0),
            'userscore': data.get('userscore', 0),
            'ccu': data.get('ccu', 0),
            'price': data.get('price', '0'),
            'initialprice': data.get('initialprice', '0'),
            'discount': data.get('discount', '0'),
            'tags': json.dumps(data.get('tags', {})),  # JSON string
            'languages': data.get('languages', ''),
            'genre': data.get('genre', '')
        }
        
    except Exception as e:
        with progress_lock:
            progress['count'] += 1
            progress['failed'] += 1
        print(f"   ⚠️  Failed to fetch appid {appid}: {e}")
        return None

def get_detailed_catalog(num_games=5000, max_workers=10, resume=True):
    """
    Fetch detailed game catalog with multithreading
    
    Args:
        num_games: Number of top games to fetch (default 5000)
        max_workers: Number of parallel threads (default 10)
        resume: Skip already fetched games if True (default True)
    """
    print("="*60)
    print("FETCHING DETAILED STEAM CATALOG WITH MULTITHREADING")
    print("="*60)
    
    # Check for existing data to resume
    existing_appids = set()
    if resume and os.path.exists('data/steam_catalog_detailed.csv'):
        try:
            existing_df = pd.read_csv('data/steam_catalog_detailed.csv')
            existing_appids = set(existing_df['appid'].astype(str))
            print(f"\n📂 Found existing data: {len(existing_appids)} games already fetched")
        except:
            pass
    
    # First, get the basic catalog to get list of appids
    print("\n[Step 1/3] Getting list of games from SteamSpy...")
    url = "https://steamspy.com/api.php"
    all_appids = []
    
    # Fetch enough pages to get the top N games
    pages_needed = (num_games // 1000) + 1
    for page in range(pages_needed):
        print(f"   Fetching page {page}...", end=" ")
        try:
            params = {'request': 'all', 'page': page}
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            all_appids.extend(data.keys())
            print(f"({len(data)} games)")
            time.sleep(0.5)  # Reduced delay
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    # Limit to top N games and filter out already fetched
    all_appids = list(all_appids)[:num_games]
    appids_to_fetch = [aid for aid in all_appids if aid not in existing_appids]
    progress['total'] = len(appids_to_fetch)
    
    if len(appids_to_fetch) == 0:
        print(f"\n✅ All {len(existing_appids)} games already fetched!")
        return pd.read_csv('data/steam_catalog_detailed.csv')
    
    print(f"\n[Step 2/3] Fetching detailed data for {len(appids_to_fetch)} games...")
    print(f"Using {max_workers} parallel threads")
    print(f"Estimated time: ~{len(appids_to_fetch) / max_workers / 60:.1f} minutes")
    print("Progress updates every 100 games")
    print("💾 Auto-saving every 1000 games (safe to Ctrl+C and resume later)\n")
    
    start_time = time.time()
    games_data = []
    save_counter = 0
    
    # Load existing data if resuming
    if existing_appids:
        existing_df = pd.read_csv('data/steam_catalog_detailed.csv')
        games_data = existing_df.to_dict('records')
    
    # Use ThreadPoolExecutor for parallel requests
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_appid = {
            executor.submit(fetch_game_details, appid): appid 
            for appid in appids_to_fetch
        }
        
        # Collect results as they complete and save incrementally
        for future in as_completed(future_to_appid):
            result = future.result()
            if result:
                games_data.append(result)
                save_counter += 1
                
                # Auto-save every 1000 games
                if save_counter % 1000 == 0:
                    temp_df = pd.DataFrame(games_data)
                    temp_df.to_csv('data/steam_catalog_detailed.csv', index=False)
                    elapsed = time.time() - start_time
                    rate = progress['count'] / elapsed if elapsed > 0 else 0
                    remaining = (progress['total'] - progress['count']) / rate if rate > 0 else 0
                    print(f"   💾 Auto-saved! {len(games_data)} total games. ETA: {remaining/60:.1f} min")
    
    elapsed = time.time() - start_time
    
    print(f"\n[Step 3/3] Final save...")
    df = pd.DataFrame(games_data)
    
    # Sort by number of owners (most popular first)
    df.to_csv('data/steam_catalog_detailed.csv', index=False)
    print(f"💾 Saved to data/steam_catalog_detailed.csv")
    
    # Show summary
    print("\n📊 CATALOG SUMMARY:")
    print(f"Total games fetched: {len(df)}")
    print(f"Failed requests: {progress['failed']}")
    print(f"Games with tags: {(df['tags'] != '{}').sum()}")
    print(f"Games with genres: {(df['genre'] != '').sum()}")
    print(f"Free games: {(df['price'] == '0').sum()}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Average: {elapsed/len(df):.2f} seconds per game")
    
    return df

def main():
    print("🎮 Detailed Steam Catalog Downloader (with tags/genres)")
    print("Uses multithreading to fetch detailed game data\n")
    
    print("How many games to fetch?")
    print("  1. Top 1,000 (fastest, ~2-3 minutes)")
    print("  2. Top 5,000 (recommended, ~10-15 minutes)")
    print("  3. Top 10,000 (~20-30 minutes)")
    print("  4. All ~30,000+ (1-2 hours)")
    choice = input("\nEnter 1, 2, 3, or 4 [default: 2]: ").strip() or "2"
    
    num_games = {
        "1": 1000,
        "2": 5000,
        "3": 10000,
        "4": 999999  # Will fetch all available
    }.get(choice, 5000)
    
    threads = input("Number of parallel threads (20-50 recommended for speed) [default: 40]: ").strip()
    max_workers = int(threads) if threads.isdigit() else 40
    
    catalog = get_detailed_catalog(num_games=num_games, max_workers=max_workers)
    
    if not catalog.empty:
        print("\n✅ SUCCESS! You now have detailed game data with tags and genres")
        print("\nNext steps:")
        print("1. Run: python src/data_collection.py - to get YOUR games")
        print("2. Then we can build the recommendation model!")

if __name__ == "__main__":
    main()
