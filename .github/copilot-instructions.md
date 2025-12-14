<!-- Use this file to provide workspace-specific custom instructions to Copilot. -->

# Steam Game Recommendation System

## Project Context
This is a machine learning project that recommends Steam games based on user library, playtime, reviews, and wishlist data.

## Key Technologies
- Python 3.8+
- pandas, numpy, scikit-learn (ML)
- Flask (web framework)
- Steam API for data collection
- Jupyter notebooks for experimentation

## Coding Guidelines
- Keep code simple and readable
- Use type hints where helpful
- Document complex algorithms
- Focus on MVP functionality first
- Optimize after validation

## Project Structure
- `data/` - Raw and processed datasets
- `models/` - Trained ML models
- `notebooks/` - Jupyter notebooks for exploration
- `src/` - Source code modules
  - `data_collection.py` - Steam API integration
  - `model.py` - ML recommendation model
  - `app.py` - Web application

## Development Workflow
1. Data collection from Steam API
2. Exploratory analysis in Jupyter
3. Model development and validation
4. Web application for deployment
5. Testing with real Steam data

## Important Notes
- Steam API requires API key (stored in .env)
- Respect Steam API rate limits
- User privacy: don't store sensitive data
- Keep deployment simple (Streamlit or Flask)
