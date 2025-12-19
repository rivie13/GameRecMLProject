"""
Add header image URLs to Steam catalog.

Steam provides game header images at a standard CDN URL:
https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg

This script adds this URL to the catalog without needing API calls.
"""
import pandas as pd
from pathlib import Path

def add_header_images():
    """Add header image URLs to catalog based on appid."""
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    catalog_path = project_root / 'data' / 'steam_catalog_detailed.csv'
    output_path = project_root / 'data' / 'steam_catalog_detailed.csv'
    
    print(f"Loading catalog from: {catalog_path}")
    df = pd.read_csv(catalog_path)
    
    print(f"Loaded {len(df)} games")
    print(f"Columns: {df.columns.tolist()}")
    
    # Add header image URL column
    # Steam CDN format: https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg
    df['header_image'] = df['appid'].apply(
        lambda x: f"https://cdn.akamai.steamstatic.com/steam/apps/{x}/header.jpg"
    )
    
    print(f"\n✓ Added header_image column")
    print(f"Sample URLs:")
    for idx in range(min(5, len(df))):
        print(f"  {df.iloc[idx]['name']}: {df.iloc[idx]['header_image']}")
    
    # Save updated catalog
    print(f"\nSaving updated catalog to: {output_path}")
    df.to_csv(output_path, index=False)
    
    print(f"✓ Done! Added header images to {len(df)} games")
    print(f"\nNew columns: {df.columns.tolist()}")

if __name__ == "__main__":
    add_header_images()
