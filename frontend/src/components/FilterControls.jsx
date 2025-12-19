import { useState } from 'react'
import PropTypes from 'prop-types'

function FilterControls({ filters, onFilterChange, onApply }) {
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
      genre_limits: [],
      tag_limits: [],
      series_limits: [],
      weight_ml: null,
      weight_content: null,
      weight_preference: null,
      weight_review: null,
    })
    handleApply()
  }

  // Helper to add a genre/tag limit
  const addGenreLimit = () => {
    const newLimits = [...(filters.genre_limits || []), { genre: '', limit: 3 }]
    handleChange('genre_limits', newLimits)
  }

  const addTagLimit = () => {
    const newLimits = [...(filters.tag_limits || []), { tag: '', limit: 3 }]
    handleChange('tag_limits', newLimits)
  }

  const updateGenreLimit = (index, field, value) => {
    const newLimits = [...filters.genre_limits]
    newLimits[index][field] = value
    handleChange('genre_limits', newLimits)
  }

  const updateTagLimit = (index, field, value) => {
    const newLimits = [...filters.tag_limits]
    newLimits[index][field] = value
    handleChange('tag_limits', newLimits)
  }

  const removeGenreLimit = (index) => {
    const newLimits = filters.genre_limits.filter((_, i) => i !== index)
    handleChange('genre_limits', newLimits)
  }

  const removeTagLimit = (index) => {
    const newLimits = filters.tag_limits.filter((_, i) => i !== index)
    handleChange('tag_limits', newLimits)
  }

  const addSeriesLimit = () => {
    const newLimits = [...(filters.series_limits || []), { series: '', limit: 2 }]
    handleChange('series_limits', newLimits)
  }

  const updateSeriesLimit = (index, field, value) => {
    const newLimits = [...filters.series_limits]
    newLimits[index][field] = value
    handleChange('series_limits', newLimits)
  }

  const removeSeriesLimit = (index) => {
    const newLimits = filters.series_limits.filter((_, i) => i !== index)
    handleChange('series_limits', newLimits)
  }

  // Calculate weight total
  const weightTotal = (
    (filters.weight_ml || 35) +
    (filters.weight_content || 35) +
    (filters.weight_preference || 20) +
    (filters.weight_review || 10)
  )

  return (
    <div className="filter-controls">
      <div className="filter-section">
        <div className="filter-content">
          {/* Recommendation Mode */}
          <div className="filter-subsection">
            <h4>Recommendation Mode</h4>
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

            {/* Basic Filters */}
            <div className="filter-subsection">
              <h4>Basic Filters</h4>
              
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
            </div>

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
            {/* Weight Tuning (Hybrid Mode Only) */}
            {filters.mode === 'hybrid' && (
              <div className="filter-subsection">
                <h4>⚖️ Component Weights (Hybrid Tuning)</h4>
                <p className="filter-note">
                  Adjust how much each component influences recommendations. 
                  Total should equal 100%. Leave at defaults for auto-tuning (35/35/20/10).
                </p>
                
                <div className="weight-controls">
                  <div className="filter-group">
                    <label htmlFor="weight_ml">
                      🧠 ML Weight: {filters.weight_ml || 35}%
                    </label>
                    <input 
                      type="range"
                      id="weight_ml"
                      min="0" 
                      max="100"
                      value={filters.weight_ml || 35}
                      onChange={(e) => handleChange('weight_ml', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="filter-group">
                    <label htmlFor="weight_content">
                      🎮 Content Weight: {filters.weight_content || 35}%
                    </label>
                    <input 
                      type="range"
                      id="weight_content"
                      min="0" 
                      max="100"
                      value={filters.weight_content || 35}
                      onChange={(e) => handleChange('weight_content', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="filter-group">
                    <label htmlFor="weight_preference">
                      ❤️ Preference Weight: {filters.weight_preference || 20}%
                    </label>
                    <input 
                      type="range"
                      id="weight_preference"
                      min="0" 
                      max="100"
                      value={filters.weight_preference || 20}
                      onChange={(e) => handleChange('weight_preference', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="filter-group">
                    <label htmlFor="weight_review">
                      ⭐ Review Weight: {filters.weight_review || 10}%
                    </label>
                    <input 
                      type="range"
                      id="weight_review"
                      min="0" 
                      max="100"
                      value={filters.weight_review || 10}
                      onChange={(e) => handleChange('weight_review', parseInt(e.target.value))}
                    />
                  </div>

                  <div className={`weight-total ${weightTotal !== 100 ? 'weight-warning' : 'weight-ok'}`}>
                    Total: {weightTotal}%
                    {weightTotal !== 100 && (
                      <span className="weight-note"> ⚠️ Should equal 100%</span>
                    )}
                  </div>
                </div>
              </div>
            )}
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

            {/* Diversity Filters */}
            <div className="filter-subsection">
              <h4>🎲 Diversity Controls</h4>
              <p className="filter-note">Set specific limits for genres and tags to increase variety</p>
              
              <div className="diversity-section">
                <div className="diversity-header">
                  <strong>Genre Limits</strong>
                  <button 
                    type="button"
                    className="btn btn-small"
                    onClick={addGenreLimit}
                  >
                    + Add Genre Limit
                  </button>
                </div>
                
                {(!filters.genre_limits || filters.genre_limits.length === 0) ? (
                  <p className="filter-hint">No genre limits set. Click "+ Add Genre Limit" to add one.</p>
                ) : (
                  <div className="limit-list">
                    {filters.genre_limits.map((item, index) => (
                      <div key={index} className="limit-item">
                        <input
                          type="text"
                          placeholder="Genre name (e.g., Action, RPG)"
                          value={item.genre}
                          onChange={(e) => updateGenreLimit(index, 'genre', e.target.value)}
                          className="limit-name"
                        />
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={item.limit}
                          onChange={(e) => updateGenreLimit(index, 'limit', parseInt(e.target.value) || 1)}
                          className="limit-count"
                        />
                        <button
                          type="button"
                          className="btn-remove"
                          onClick={() => removeGenreLimit(index)}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <small className="input-hint">E.g., "Action" with limit 5 = max 5 Action games</small>
              </div>

              <div className="diversity-section">
                <div className="diversity-header">
                  <strong>Tag Limits</strong>
                  <button 
                    type="button"
                    className="btn btn-small"
                    onClick={addTagLimit}
                  >
                    + Add Tag Limit
                  </button>
                </div>
                
                {(!filters.tag_limits || filters.tag_limits.length === 0) ? (
                  <p className="filter-hint">No tag limits set. Click "+ Add Tag Limit" to add one.</p>
                ) : (
                  <div className="limit-list">
                    {filters.tag_limits.map((item, index) => (
                      <div key={index} className="limit-item">
                        <input
                          type="text"
                          placeholder="Tag name (e.g., Souls-like, Open-World)"
                          value={item.tag}
                          onChange={(e) => updateTagLimit(index, 'tag', e.target.value)}
                          className="limit-name"
                        />
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={item.limit}
                          onChange={(e) => updateTagLimit(index, 'limit', parseInt(e.target.value) || 1)}
                          className="limit-count"
                        />
                        <button
                          type="button"
                          className="btn-remove"
                          onClick={() => removeTagLimit(index)}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <small className="input-hint">E.g., "Souls-like" with limit 3 = max 3 Souls-like games</small>
              </div>

              <div className="diversity-section">
                <div className="diversity-header">
                  <strong>Series Limits</strong>
                  <button 
                    type="button"
                    className="btn btn-small"
                    onClick={addSeriesLimit}
                  >
                    + Add Series Limit
                  </button>
                </div>
                
                {(!filters.series_limits || filters.series_limits.length === 0) ? (
                  <p className="filter-hint">No series limits set. Click "+ Add Series Limit" to add one.</p>
                ) : (
                  <div className="limit-list">
                    {filters.series_limits.map((item, index) => (
                      <div key={index} className="limit-item">
                        <input
                          type="text"
                          placeholder="Series name (e.g., Dark Souls, Fallout)"
                          value={item.series}
                          onChange={(e) => updateSeriesLimit(index, 'series', e.target.value)}
                          className="limit-name"
                        />
                        <input
                          type="number"
                          min="1"
                          max="5"
                          value={item.limit}
                          onChange={(e) => updateSeriesLimit(index, 'limit', parseInt(e.target.value) || 1)}
                          className="limit-count"
                        />
                        <button
                          type="button"
                          className="btn-remove"
                          onClick={() => removeSeriesLimit(index)}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <small className="input-hint">E.g., "Dark Souls" with limit 2 = max 2 Dark Souls games</small>
              </div>
            </div>

            {/* Filter Actions */}
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
    genre_limits: PropTypes.array,
    tag_limits: PropTypes.array,
    series_limits: PropTypes.array,
  }).isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onApply: PropTypes.func,
}

export default FilterControls
