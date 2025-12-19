function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3 className="footer-title">GameRec AI</h3>
          <p className="footer-text">
            AI-powered Steam game recommendations using machine learning and content-based filtering.
          </p>
        </div>

        <div className="footer-section">
          <h4 className="footer-subtitle">Tech Stack</h4>
          <ul className="footer-list">
            <li>FastAPI + PostgreSQL</li>
            <li>React 19 + Vite</li>
            <li>scikit-learn + XGBoost</li>
            <li>Steam Web API</li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-subtitle">Features</h4>
          <ul className="footer-list">
            <li>ML-powered recommendations</li>
            <li>Content-based filtering</li>
            <li>User preference tuning</li>
            <li>Gaming profile analytics</li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-subtitle">About</h4>
          <p className="footer-text">
            Built as an educational ML portfolio project. No affiliation with Steam or Valve Corporation.
          </p>
          <p className="footer-text-small">
            Data sourced from Steam Web API and SteamSpy.
          </p>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} GameRec AI. Educational project - not for commercial use.</p>
        <p className="footer-disclaimer">
          Steam and the Steam logo are trademarks of Valve Corporation.
        </p>
      </div>
    </footer>
  )
}

export default Footer
