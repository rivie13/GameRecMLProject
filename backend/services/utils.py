"""
Utility functions for the recommendation system.
"""
import ast
from typing import Dict, List

import pandas as pd


def parse_tags(tag_string) -> Dict[str, int]:
    """Parse tag string into dictionary of tag: votes"""
    if pd.isna(tag_string):
        return {}
    try:
        return ast.literal_eval(str(tag_string))
    except:
        return {}


def parse_genre(genre_string) -> List[str]:
    """Parse genre string into list of genres"""
    if pd.isna(genre_string):
        return []
    return [g.strip() for g in str(genre_string).split(',')]


# NSFW and meta tag filters
NSFW_TAGS = {
    'Sexual Content', 'Nudity', 'NSFW', 'Adult',
    'Hentai', 'Erotic', 'Sexual', 'Porn', '18+', 'Adult Only'
}

META_TAGS = {
    'Indie', 'Casual', 'Free to Play', 'Early Access',
    'Great Soundtrack', 'Singleplayer', 'Multiplayer',
    'Co-op', 'Online Co-Op', 'PvP', 'PvE',
    'Moddable', 'Controller', 'Partial Controller Support',
    'Steam Achievements', 'Steam Cloud', 'Steam Trading Cards',
    'VR', 'VR Only',
    'Anime', 'Cute', 'Funny', 'Comedy',
    'Classic', 'Remake', 'Remaster', 'Retro'
}

META_GENRES = {
    'Indie', 'Casual', 'Early Access', 'Free to Play',
    'Massively Multiplayer',
    'Utilities', 'Software', 'Animation & Modeling', 'Design & Illustration',
    'Audio Production', 'Video Production', 'Web Publishing', 'Education',
    'Photo Editing', 'Game Development'
}
