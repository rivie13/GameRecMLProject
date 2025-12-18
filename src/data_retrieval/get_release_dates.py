"""
Script to fetch release dates for games in the Steam catalog.
Uses the Steam Store API to get release date information.
Uses threading for faster data collection.
"""

import pandas as pd
import requests
import time
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
CATALOG_FILE = DATA_DIR / "steam_catalog_detailed.csv"
CHECKPOINT_FILE = DATA_DIR / "cache" / "release_dates_checkpoint.json"

# Threading configuration
MAX_WORKERS = 3  # Number of concurrent threads (reduced to avoid rate limits)
RATE_LIMIT_DELAY = 1.0  # Delay between requests (seconds)
MAX_RETRIES = 8  # Maximum number of retries for 429 errors
RETRY_BASE_DELAY = 3  # Base delay for exponential backoff (seconds) - gives up to 384s max wait

# Create cache directory if it doesn't exist
CHECKPOINT_FILE.parent.mkdir(exist_ok=True)

# Thread-safe lock for checkpoint updates
checkpoint_lock = Lock()

def get_release_date(appid):
    """
    Fetch release date for a single game from Steam Store API.
    Includes retry logic for rate limiting (429 errors).
    
    Args:
        appid: Steam app ID
        
    Returns:
        tuple: (appid, dict with release date info or None if unavailable)
    """
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    
    for attempt in range(MAX_RETRIES):
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        try:
            response = requests.get(url, timeout=10)
            
            # Handle rate limiting with exponential backoff
            if response.status_code == 429:
                retry_delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"Rate limited for appid {appid}, retrying in {retry_delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(retry_delay)
                continue
            
            # Handle forbidden errors (region-locked or removed games)
            if response.status_code == 403:
                print(f"Forbidden (403) for appid {appid} - skipping")
                return (appid, None)
            
            response.raise_for_status()
            data = response.json()
            
            # Check if request was successful
            if str(appid) in data and data[str(appid)]['success']:
                game_data = data[str(appid)]['data']
                
                if 'release_date' in game_data:
                    release_info = game_data['release_date']
                    return (appid, {
                        'release_date': release_info.get('date', None),
                        'coming_soon': release_info.get('coming_soon', False)
                    })
            
            return (appid, None)
            
        except requests.exceptions.HTTPError as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error fetching appid {appid} after {MAX_RETRIES} attempts: {e}")
                return (appid, None)
            continue
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching appid {appid}: {e}")
            return (appid, None)
            
        except json.JSONDecodeError:
            print(f"Invalid JSON response for appid {appid}")
            return (appid, None)
    
    # Max retries reached
    print(f"Max retries reached for appid {appid}")
    return (appid, None)

def load_checkpoint():
    """Load checkpoint data if it exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint_data):
    """Save checkpoint data."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint_data, f)

def main():
    """Main function to fetch release dates for all games in catalog."""
    
    print("Loading Steam catalog...")
    df = pd.read_csv(CATALOG_FILE)
    print(f"Loaded {len(df)} games")
    
    # Load checkpoint to resume if interrupted
    checkpoint = load_checkpoint()
    processed_count = len(checkpoint)
    
    if processed_count > 0:
        print(f"Found checkpoint with {processed_count} games already processed")
    
    # Get list of appids that need processing
    # Process games that:
    # 1. Haven't been processed yet (not in checkpoint), OR
    # 2. Were processed but failed (release_date is None)
    appids_to_process = [
        appid for appid in df['appid']
        if str(appid) not in checkpoint or checkpoint[str(appid)].get('release_date') is None
    ]
    
    total_games = len(df)
    remaining = len(appids_to_process)
    already_successful = sum(1 for v in checkpoint.values() if v.get('release_date') is not None)
    
    print(f"Already have data for {already_successful} games")
    print(f"Retrying {remaining} games (new + previously failed) using {MAX_WORKERS} threads...")
    
    success_count = 0
    fail_count = 0
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_appid = {
            executor.submit(get_release_date, appid): appid
            for appid in appids_to_process
        }
        
        # Process completed tasks
        for future in as_completed(future_to_appid):
            appid, release_info = future.result()
            
            # Thread-safe checkpoint update
            with checkpoint_lock:
                if release_info:
                    checkpoint[str(appid)] = release_info
                    success_count += 1
                else:
                    checkpoint[str(appid)] = {'release_date': None, 'coming_soon': None}
                    fail_count += 1
                
                # Save checkpoint periodically
                if (success_count + fail_count) % 50 == 0:
                    save_checkpoint(checkpoint)
                    processed = len(checkpoint)
                    print(f"Progress: {processed}/{total_games} games processed "
                          f"({success_count} successful, {fail_count} failed)")
    
    # Final checkpoint save
    save_checkpoint(checkpoint)
    
    print(f"\nCompleted! Processed {len(checkpoint)} games")
    print(f"New data retrieved: {success_count} successful, {fail_count} failed")
    
    # Add release date data to dataframe
    print("\nMerging release dates with catalog...")
    df['release_date'] = df['appid'].apply(
        lambda x: checkpoint.get(str(x), {}).get('release_date')
    )
    df['coming_soon'] = df['appid'].apply(
        lambda x: checkpoint.get(str(x), {}).get('coming_soon')
    )
    
    # Update the existing catalog file
    df.to_csv(CATALOG_FILE, index=False)
    print(f"\nUpdated catalog saved to: {CATALOG_FILE}")
    
    # Print some statistics
    games_with_dates = df['release_date'].notna().sum()
    print(f"\nStatistics:")
    print(f"- Total games: {len(df)}")
    print(f"- Games with release dates: {games_with_dates} ({games_with_dates/len(df)*100:.1f}%)")
    print(f"- Games marked as coming soon: {df['coming_soon'].sum()}")

if __name__ == "__main__":
    main()
