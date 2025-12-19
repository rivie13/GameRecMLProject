function Landing() {
  const handleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/steam/login`
  }

  return (
    <div className="landing-page">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Discover Your Next Favorite
            <span className="hero-highlight"> Steam Game</span>
          </h1>
          <p className="hero-subtitle">
            AI-powered recommendations based on your gaming library, playtime, and preferences
          </p>
          <button onClick={handleLogin} className="btn btn-primary btn-large">
            <span>Login with Steam</span>
          </button>
          <p className="hero-note">
            We only access your public Steam library data - no passwords stored
          </p>
        </div>
      </section>

      <section className="features">
        <h2 className="section-title">How It Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3 className="feature-title">1. Connect Steam</h3>
            <p className="feature-text">
              Securely connect your Steam account using Steam OpenID authentication
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3 className="feature-title">2. AI Analysis</h3>
            <p className="feature-text">
              Our ML model analyzes your playtime patterns, favorite genres, and gaming preferences
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3 className="feature-title">3. Get Recommendations</h3>
            <p className="feature-text">
              Receive personalized game recommendations with detailed explanations
            </p>
          </div>
        </div>
      </section>

      <section className="features-showcase">
        <h2 className="section-title">What Makes Us Different</h2>
        <div className="showcase-grid">
          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>ML-Powered Predictions</h3>
            <p>Machine learning models trained on your playtime behavior patterns</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>Content-Based Matching</h3>
            <p>Find games similar to your most-loved titles</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>Hybrid Scoring System</h3>
            <p>Combines ML predictions, content similarity, reviews, and preferences</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>Visual Analytics</h3>
            <p>Rich visualizations of your gaming profile and preferences</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>Customizable Filters</h3>
            <p>Fine-tune recommendations with genre/tag boosts and exclusions</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">✅</div>
            <h3>Detailed Explanations</h3>
            <p>Understand why each game was recommended for you</p>
          </div>
        </div>
      </section>

      <section className="tech-stack">
        <h2 className="section-title">Built With</h2>
        <div className="tech-list">
          <div className="tech-item">Python</div>
          <div className="tech-item">FastAPI</div>
          <div className="tech-item">PostgreSQL</div>
          <div className="tech-item">React 19</div>
          <div className="tech-item">scikit-learn</div>
          <div className="tech-item">XGBoost</div>
          <div className="tech-item">Steam API</div>
          <div className="tech-item">Vite</div>
        </div>
        <p className="tech-note">
          This is an educational ML portfolio project demonstrating recommendation systems and full-stack development.
        </p>
      </section>

      <section className="cta">
        <h2 className="cta-title">Ready to Discover New Games?</h2>
        <button onClick={handleLogin} className="btn btn-primary btn-large">
          <span>Get Started Now</span>
        </button>
      </section>
    </div>
  )
}

export default Landing
