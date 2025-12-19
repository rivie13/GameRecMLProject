import { useState } from 'react'
import PropTypes from 'prop-types'

function FilterControls({ filters, onFilterChange, onApply }) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value })
  }

  const handleApply = () => {
    if (onApply) {
      onApply()
    }
  }

  const handleReset = () => {
    onFilterChange({
      mode: 'hybrid',
      limit: 20,
      min_reviews: 5000,
      min_review_score: 70,
      price_max: null,
      release_year_min: null,
      release_year_max: null,
      sfw_only: true,
      exclude_early_access: true,
      boost_tags: '',
      boost_genres: '',
      dislike_tags: '',
      dislike_genres: '',
      hard_exclude_tags: '',
      hard_exclude_genres: '',
    })
    handleApply()
  }

  return (
    <div className="filter-controls">
      <div className="filter-section">
        <h3>Recommendation Mode</h3>
        <div className="filter-group">
          <div className="mode-selector">
            <button 
              className={`mode-btn ${filters.mode === 'hybrid' ? 'active' : ''}`}
              onClick={() => handleChange('mode', 'hybrid')}
            >
              <span className="mode-icon">🤖</span>
              <span className="mode-label">Hybrid</span>
              <span className="mode-desc">Best of all worlds</span>
            </button>
            <button 
              className={`mode-btn ${filters.mode === 'ml' ? 'active' : ''}`}
              onClick={() => handleChange('mode', 'ml')}
            >
              <span className="mode-icon">🧠</span>
              <span className="mode-label">ML-Only</span>
              <span className="mode-desc">AI predictions</span>
            </button>
            <button 
              className={`mode-btn ${filters.mode === 'content' ? 'active' : ''}`}
              onClick={() => handleChange('mode', 'content')}
            >
              <span className="mode-icon">🎮</span>
              <span className="mode-label">Content-Based</span>
              <span className="mode-desc">Similar games</span>
            </button>
            <button 
              className={`mode-btn ${filters.mode === 'preference' ? 'active' : ''}`}
              onClick={() => handleChange('mode', 'preference')}
            >
              <span className="mode-icon">❤️</span>
              <span className="mode-label">Preference-Tuned</span>
              <span className="mode-desc">Your tastes</span>
            </button>
          </div>
        </div>
      </div>

      <div className="filter-section">
        <h3>Basic Filters</h3>
        
        <div className="filter-group">
          <label htmlFor="limit">Number of Recommendations</label>
          <input 
            type="number" 
            id="limit"
            min="1" 
            max="100"
            value={filters.limit}
            onChange={(e) => handleChange('limit', parseInt(e.target.value))}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="min_reviews">
            Minimum Reviews: {filters.min_reviews.toLocaleString()}
          </label>
          <input 
            type="range" 
            id="min_reviews"
            min="0" 
            max="10000"
            step="500"
            value={filters.min_reviews}
            onChange={(e) => handleChange('min_reviews', parseInt(e.target.value))}
          />
          <div className="range-labels">
            <span>0</span>
            <span>5k</span>
            <span>10k</span>
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="min_review_score">
            Minimum Review Score: {filters.min_review_score}%
          </label>
          <input 
            type="range" 
            id="min_review_score"
            min="0" 
            max="100"
            step="5"
            value={filters.min_review_score}
            onChange={(e) => handleChange('min_review_score', parseInt(e.target.value))}
          />
          <div className="range-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="price_max">Maximum Price ($)</label>
          <input 
            type="number" 
            id="price_max"
            min="0" 
            step="5"
            placeholder="No limit"
            value={filters.price_max || ''}
            onChange={(e) => handleChange('price_max', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>

        <div className="filter-group checkbox-group">
          <label>
            <input 
              type="checkbox" 
              checked={filters.sfw_only}
              onChange={(e) => handleChange('sfw_only', e.target.checked)}
            />
            <span>SFW Only (Exclude NSFW content)</span>
          </label>
        </div>

        <div className="filter-group checkbox-group">
          <label>
            <input 
              type="checkbox" 
              checked={filters.exclude_early_access}
              onChange={(e) => handleChange('exclude_early_access', e.target.checked)}
            />
            <span>Exclude Early Access</span>
          </label>
        </div>

        <div className="filter-info">
          <p className="info-message">
            ℹ️ <strong>Note:</strong> Meta genres (Indie, Casual, Utilities, Software, etc.) are automatically filtered out to focus on actual game genres.
          </p>
        </div>

        <div className="filter-actions">
          <button 
            className="btn btn-primary"
            onClick={handleApply}
          >
            Apply Filters
          </button>
          <button 
            className="btn btn-secondary"
            onClick={handleReset}
          >
            Reset to Defaults
          </button>
        </div>
      </div>

      {/* Advanced Filters Section */}
      <div className="filter-section advanced-filters">
        <div className="advanced-header">
          <h3>Advanced Filters</h3>
          <button 
            className="advanced-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? '▼ Hide' : '▶ Show'}
          </button>
        </div>

        {showAdvanced && (
          <div className="advanced-content">
            {/* Release Year Filter */}
            <div className="filter-subsection">
              <h4>Release Year Range</h4>
              <p className="filter-note">Note: Only ~11% of games have release date data</p>
              <div className="filter-row">
                <div className="filter-group">
                  <label htmlFor="release_year_min">From Year</label>
                  <input 
                    type="number" 
                    id="release_year_min"
                    min="1980" 
                    max="2030"
                    placeholder="e.g. 2015"
                    value={filters.release_year_min || ''}
                    onChange={(e) => handleChange('release_year_min', e.target.value ? parseInt(e.target.value) : null)}
                  />
                </div>
                <div className="filter-group">
                  <label htmlFor="release_year_max">To Year</label>
                  <input 
                    type="number" 
                    id="release_year_max"
                    min="1980" 
                    max="2030"
                    placeholder="e.g. 2025"
                    value={filters.release_year_max || ''}
                    onChange={(e) => handleChange('release_year_max', e.target.value ? parseInt(e.target.value) : null)}
                  />
                </div>
              </div>
            </div>

            {/* Preference Boosts */}
            <div className="filter-subsection">
              <h4>🔺 Boost Preferences</h4>
              <p className="filter-note">Format: "Tag:Points" (e.g., "Open World:20,Multiplayer:15")</p>
              
              <div className="filter-group">
                <label htmlFor="boost_tags">Boost Tags</label>
                <input 
                  type="text" 
                  id="boost_tags"
                  placeholder="e.g. Open World:20,RPG:15"
                  value={filters.boost_tags || ''}
                  onChange={(e) => handleChange('boost_tags', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Boosts games with these tags (+5 to +20 points)</small>
              </div>

              <div className="filter-group">
                <label htmlFor="boost_genres">Boost Genres</label>
                <input 
                  type="text" 
                  id="boost_genres"
                  placeholder="e.g. RPG:15,Action:10"
                  value={filters.boost_genres || ''}
                  onChange={(e) => handleChange('boost_genres', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Boosts games with these genres (+5 to +20 points)</small>
              </div>
            </div>

            {/* Preference Penalties */}
            <div className="filter-subsection">
              <h4>🔻 Dislike Preferences</h4>
              <p className="filter-note">Format: "Tag:-Points" (e.g., "Horror:-15,Sports:-20")</p>
              
              <div className="filter-group">
                <label htmlFor="dislike_tags">Penalize Tags</label>
                <input 
                  type="text" 
                  id="dislike_tags"
                  placeholder="e.g. Horror:-15,Survival:-10"
                  value={filters.dislike_tags || ''}
                  onChange={(e) => handleChange('dislike_tags', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Penalizes games with these tags (-5 to -20 points)</small>
              </div>

              <div className="filter-group">
                <label htmlFor="dislike_genres">Penalize Genres</label>
                <input 
                  type="text" 
                  id="dislike_genres"
                  placeholder="e.g. Sports:-20,Racing:-15"
                  value={filters.dislike_genres || ''}
                  onChange={(e) => handleChange('dislike_genres', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Penalizes games with these genres (-5 to -20 points)</small>
              </div>
            </div>

            {/* Hard Exclusions */}
            <div className="filter-subsection hard-exclusions">
              <h4>🚫 Hard Exclusions (Complete Removal)</h4>
              <p className="filter-note">These will NEVER appear in recommendations</p>
              
              <div className="filter-group">
                <label htmlFor="hard_exclude_tags">Exclude Tags</label>
                <input 
                  type="text" 
                  id="hard_exclude_tags"
                  placeholder="e.g. Racing,Battle Royale"
                  value={filters.hard_exclude_tags || ''}
                  onChange={(e) => handleChange('hard_exclude_tags', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Comma-separated list (no points needed)</small>
              </div>

              <div className="filter-group">
                <label htmlFor="hard_exclude_genres">Exclude Genres</label>
                <input 
                  type="text" 
                  id="hard_exclude_genres"
                  placeholder="e.g. Sports,Simulation"
                  value={filters.hard_exclude_genres || ''}
                  onChange={(e) => handleChange('hard_exclude_genres', e.target.value)}
                  className="input-full-width"
                />
                <small className="input-hint">Comma-separated list (no points needed)</small>
              </div>
            </div>

            <div className="filter-actions">
              <button 
                className="btn btn-primary"
                onClick={handleApply}
              >
                Apply Advanced Filters
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

FilterControls.propTypes = {
  filters: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    limit: PropTypes.number.isRequired,
    min_reviews: PropTypes.number.isRequired,
    min_review_score: PropTypes.number.isRequired,
    price_max: PropTypes.number,
    release_year_min: PropTypes.number,
    release_year_max: PropTypes.number,
    sfw_only: PropTypes.bool.isRequired,
    exclude_early_access: PropTypes.bool.isRequired,
    boost_tags: PropTypes.string,
    boost_genres: PropTypes.string,
    dislike_tags: PropTypes.string,
    dislike_genres: PropTypes.string,
    hard_exclude_tags: PropTypes.string,
    hard_exclude_genres: PropTypes.string,
  }).isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onApply: PropTypes.func,
}

export default FilterControls
