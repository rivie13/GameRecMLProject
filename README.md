# Steam Game Recommendation System

A machine learning project that recommends new Steam games based on your library, playtime, reviews, and wishlist.

## 🎮 Project Overview

This project analyzes your Steam gaming data to provide personalized game recommendations:
- **Game Library**: Games you own
- **Playtime**: Hours spent on each game
- **Reviews**: Your ratings and reviews
- **Wishlist**: Games you're interested in

## 📁 Project Structure

```
GameRecMLProject/
├── data/              # Raw and processed data
├── models/            # Trained ML models
├── notebooks/         # Jupyter notebooks for experimentation
├── src/               # Source code
│   ├── data_collection.py    # Steam API data fetching
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
   Create a `.env` file in the root directory:
   ```
   STEAM_API_KEY=your_api_key_here
   STEAM_ID=your_steam_id_here
   ```

## 📊 Usage

### 1. Collect Your Steam Data
```bash
python src/data_collection.py
```

### 2. Train the Model
Open and run the notebook:
```bash
jupyter notebook notebooks/model_development.ipynb
```

### 3. Get Recommendations
Run the application:
```bash
python src/app.py
```

## 🔮 Future Plans
- Deploy as a web application
- Support for multiple users
- Enhanced recommendation algorithms
- Integration with more gaming platforms

## 📝 License
This is a personal project for learning purposes.
