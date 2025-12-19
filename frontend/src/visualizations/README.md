# Visualization Components

This directory contains all 8 chart components for the Gaming Profile page.

## Components

### 1. PlaytimeHistogram
Shows distribution of games across engagement categories (Unplayed, Tried, Played, Loved).

**Props**: `{ data: Array<{ playtime_hours: number }> }`

### 2. TopGamesBar
Displays top 10 most played games as a horizontal bar chart.

**Props**: `{ data: Array<{ name: string, playtime_hours: number }> }`

### 3. GenreCountBar
Shows top 10 genres by number of games owned.

**Props**: `{ data: Array<{ genres: Array<string> }> }`

### 4. GenrePlaytimeBar
Shows top 10 genres by total hours played (more meaningful than count).

**Props**: `{ data: Array<{ genres: Array<string>, playtime_hours: number }> }`

### 5. EngagementScatter
Scatter plot showing engagement score vs playtime with bubble sizing.

**Props**: `{ data: Array<{ name: string, playtime_hours: number, engagement_score: number }> }`

### 6. FeatureImportanceBar
Shows top 15 ML features by importance (optional, only if data available).

**Props**: `{ featureImportanceData: Array<{ feature: string, importance: number }> }`

### 7. ReleaseYearTimeline
Scatter plot showing release year vs playtime (only for games with release dates).

**Props**: `{ data: Array<{ name: string, release_year: number, playtime_hours: number, engagement_score: number }> }`

### 8. TagCloud
Custom tag cloud showing playtime-weighted tag importance (top 50 tags).

**Props**: `{ data: Array<{ tags: Array<string>, playtime_hours: number }> }`

## Usage

```jsx
import {
  PlaytimeHistogram,
  TopGamesBar,
  GenreCountBar,
  GenrePlaytimeBar,
  EngagementScatter,
  FeatureImportanceBar,
  ReleaseYearTimeline,
  TagCloud
} from '../visualizations'

// In your component
<PlaytimeHistogram data={games} />
<TopGamesBar data={games} />
<GenreCountBar data={games} />
<GenrePlaytimeBar data={games} />
<EngagementScatter data={games} />
<FeatureImportanceBar featureImportanceData={features} />
<ReleaseYearTimeline data={games} />
<TagCloud data={games} />
```

## Features

- ✅ **Interactive tooltips** on all charts
- ✅ **Responsive design** (works on mobile and desktop)
- ✅ **Color-coded** for easy visual interpretation
- ✅ **Dark theme** optimized
- ✅ **PropTypes validation** for type safety
- ✅ **Error handling** for missing/incomplete data
- ✅ **React 19 compatible**

## Dependencies

- `recharts`: ^3.6.0 (for charts 1-7)
- `react`: ^19.2.0
- `prop-types`: Runtime type checking

No external library needed for Chart 8 (TagCloud) - custom implementation.

## Styling

All charts use consistent styling from `styles/main.css`:

- `.chart-container` - Card styling with padding and shadow
- `.chart-title` - Steam-themed headers
- `.visualizations-grid` - Responsive grid layout

## Data Format

Charts expect data from the API endpoint `/api/profile/{steam_id}/stats`:

```json
{
  "games": [
    {
      "name": "Game Name",
      "playtime_hours": 123.4,
      "engagement_score": 85,
      "genres": ["Action", "RPG"],
      "tags": ["Open World", "Multiplayer"],
      "release_year": 2023
    }
  ],
  "feature_importance": [
    {
      "feature": "tag_Open-World",
      "importance": 0.15
    }
  ]
}
```

## Notes

- Charts 1-5: Core visualizations (always visible)
- Chart 6: Optional (only shows if `feature_importance` data available)
- Chart 7: Optional (only shows games with `release_year` data, ~11% of catalog)
- Chart 8: Shows top 50 tags by playtime-weighted importance
