function Landing() {
  const handleLogin = () => {
    // Redirect to backend Steam login endpoint
    // Backend will redirect to Steam, then back to our callback
    window.location.href = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/steam/login`
  }

  return (
    <div className="landing-page">
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">🎮 BETA</div>
          <h1 className="hero-title">
            Tired of Scrolling Through
            <span className="hero-highlight"> 200 Games</span>
            <br />You Never Play?
          </h1>
          <p className="hero-subtitle">
            Stop staring at your Steam library like it's a Netflix queue. Get actual recommendations based on what you <em>actually play</em>.
          </p>
          <button onClick={handleLogin} className="btn btn-primary btn-large">
            <span>🎮 Connect Steam Library</span>
          </button>
          <p className="hero-note">
            No BS. Just your public library data. No passwords, no sketchy stuff.
          </p>
        </div>
      </section>

      <section className="features">
        <h2 className="section-title">How This Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3 className="feature-title">1. Link Your Steam</h3>
            <p className="feature-text">
              Quick Steam login. We grab your library and playtime data (the stuff that's already public anyway).
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3 className="feature-title">2. ML Does Its Thing</h3>
            <p className="feature-text">
              The algorithm learns what you actually play vs what collects dust. It's trained on YOUR habits, not some generic taste profile.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3 className="feature-title">3. Get Actual Recs</h3>
            <p className="feature-text">
              Not just "popular games" or "new releases." Games that match YOUR vibe, with scores that explain why.
            </p>
          </div>
        </div>
      </section>

      <section className="features-showcase">
        <h2 className="section-title">Why This Doesn't Suck</h2>
        <div className="showcase-grid">
          <div className="showcase-item">
            <div className="showcase-icon">🧠</div>
            <h3>Learns Your Taste</h3>
            <p>ML trained on YOUR playtime, not generic "most popular" garbage</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">🎮</div>
            <h3>"More Like This" That Works</h3>
            <p>Finds games similar to stuff you've sunk 100+ hours into</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">🔥</div>
            <h3>Hybrid Algorithm</h3>
            <p>Combines ML, similarity matching, community reviews, and your preferences</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">📊</div>
            <h3>See Your Gaming Profile</h3>
            <p>Charts showing your genre preferences, playtime patterns, and what makes you tick</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">⚙️</div>
            <h3>Tune It Yourself</h3>
            <p>Boost genres you like, exclude stuff you hate (looking at you, Battle Royales)</p>
          </div>

          <div className="showcase-item">
            <div className="showcase-icon">💡</div>
            <h3>Know Why It's Recommended</h3>
            <p>Detailed breakdown of match scores - no black box BS</p>
          </div>
        </div>
      </section>

      <section className="tech-stack">
        <h2 className="section-title">The Nerdy Stuff</h2>
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
          Built as a portfolio project to learn ML/recommendation systems. Open source, not affiliated with Steam.
        </p>
      </section>

      <section className="cta">
        <h2 className="cta-title">Stop Buying Games You Never Play</h2>
        <p className="cta-subtitle">Let's find something you'll actually finish.</p>
        <button onClick={handleLogin} className="btn btn-primary btn-large">
          <span>🎮 Let's Go</span>
        </button>
      </section>
    </div>
  )
}

export default Landing
