# Steam Game Recommendation System

A machine learning project that recommends new Steam games based on your library, playtime, genres/tags, and reviews.
## 🎮 Project Overview

This project analyzes your Steam gaming data to provide personalized game recommendations:
- **Game Library**: Games you own
- **Playtime**: Hours spent on each game
- **Reviews**: Overall player ratings for each game
- **Genres/Tags**: Game categories and tags

## 📁 Project Structure

```
GameRecMLProject/
├── data/              # Raw and processed data
├── models/            # Trained ML models
├── notebooks/         # Jupyter notebooks for experimentation
├── src/               # Source code
│   ├── data_collection.py    # Steam API data fetching
│   ├── get_detailed_catalog.py # Fetch detailed game info from Steam Store API and steam spy API
│   ├── test_collection.py   # Test data collection scripts
│   ├── model.py              # ML model implementation
│   └── app.py                # Web application
├── requirements.txt   # Python dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Steam API Key (get one at https://steamcommunity.com/dev/apikey)
- Your Steam ID

### Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory (copy from `.env.example`):
   ```
   STEAM_API_KEY=your_api_key_here
   STEAM_ID=your_steam_id_here
   
   # Optional: For multi-user training (comma-separated)
   FRIEND_STEAM_IDS=76561197960287930,76561197960287931
   ```
   
   **Finding Steam IDs:**
   - Get your Steam ID from [steamid.io](https://steamid.io/)
   - API Key from [Steam Web API](https://steamcommunity.com/dev/apikey)

## 📊 Usage

### 1. Collect Your Steam Data
```bash
python src/data_collection.py
```

### 1.1 Collect Steam Catalog Data
```bash
python src/get_detailed_catalog.py
```
**NOTE**: This step may take a while as it fetches detailed information for all Steam games. Steam API has rate limits, so please be patient.

### 2. Train the Model

#### Single User Training
Open and run the feature engineering notebook:
```bash
jupyter notebook notebooks/feature_engineering.ipynb
```

#### Multi-User Training (Recommended)
Train on multiple Steam users for better generalization:
```bash
jupyter notebook notebooks/multi_user_training.ipynb
```
**Prerequisites:**
- Add friend Steam IDs to `.env` file: `FRIEND_STEAM_IDS=id1,id2,id3`
- Handles users with 500+ games efficiently
- Learns engagement patterns across different user preferences

### 3. Get Recommendations
Run the application:
```bash
python src/app.py
```
**NOTE**: No web application is deployed or coded yet. This will be in a future update.

## 🔮 Future Plans
- Deploy as a web application
- Support for multiple users
- Enhanced recommendation algorithms
- Integration with more gaming platforms

## 📝 License
This is a personal project for learning purposes.
