import PropTypes from 'prop-types'

function ScoreExplanation({ game, mode }) {
  const hasScoreComponents = game.ml_score !== undefined || 
                            game.content_score !== undefined || 
                            game.preference_score !== undefined || 
                            game.review_component_score !== undefined

  if (!hasScoreComponents) {
    return (
      <div className="score-explanation">
        <p className="explanation-text">
          This game scored <strong>{Math.round(game.score)}/100</strong> based on {mode} mode.
        </p>
      </div>
    )
  }

  // Calculate weights based on mode
  const getWeights = () => {
    switch (mode) {
      case 'hybrid':
        return { ml: 0.35, content: 0.35, preference: 0.20, review: 0.10 }
      case 'ml':
        return { ml: 1.0, content: 0, preference: 0, review: 0 }
      case 'content':
        return { ml: 0, content: 1.0, preference: 0, review: 0 }
      case 'preference':
        return { ml: 0, content: 0, preference: 1.0, review: 0 }
      default:
        return { ml: 0.35, content: 0.35, preference: 0.20, review: 0.10 }
    }
  }

  const weights = getWeights()

  return (
    <div className="score-explanation">
      <div className="explanation-header">
        <strong>Match Score: {Math.round(game.score)}/100</strong>
      </div>

      <div className="explanation-components">
        {weights.ml > 0 && game.ml_score !== undefined && (
          <div className="score-component">
            <div className="component-header">
              <span className="component-icon">🧠</span>
              <span className="component-label">ML Prediction</span>
              <span className="component-score">
                {Math.round(game.ml_score)}/100
              </span>
            </div>
            <div className="component-weight">
              Weight: {(weights.ml * 100).toFixed(0)}%
            </div>
            <div className="component-description">
              AI learned patterns from your playtime to predict your engagement with this game.
            </div>
          </div>
        )}

        {weights.content > 0 && game.content_score !== undefined && (
          <div className="score-component">
            <div className="component-header">
              <span className="component-icon">🎮</span>
              <span className="component-label">Content Similarity</span>
              <span className="component-score">
                {Math.round(game.content_score)}/100
              </span>
            </div>
            <div className="component-weight">
              Weight: {(weights.content * 100).toFixed(0)}%
            </div>
            <div className="component-description">
              Similar genres and tags to your most played games.
            </div>
            {game.similar_to && game.similar_to.length > 0 && (
              <div className="component-details">
                <strong>Similar to:</strong> {game.similar_to.join(', ')}
              </div>
            )}
          </div>
        )}

        {weights.preference > 0 && game.preference_score !== undefined && (
          <div className="score-component">
            <div className="component-header">
              <span className="component-icon">❤️</span>
              <span className="component-label">Your Preferences</span>
              <span className="component-score">
                {Math.round(game.preference_score)}/100
              </span>
            </div>
            <div className="component-weight">
              Weight: {(weights.preference * 100).toFixed(0)}%
            </div>
            <div className="component-description">
              Matches your explicit genre and tag preferences.
            </div>
            {(game.preference_boosts || game.preference_penalties) && (
              <div className="component-details">
                {game.preference_boosts && game.preference_boosts.length > 0 && (
                  <div className="preference-list">
                    <strong>Boosts:</strong> {game.preference_boosts.join(', ')}
                  </div>
                )}
                {game.preference_penalties && game.preference_penalties.length > 0 && (
                  <div className="preference-list">
                    <strong>Penalties:</strong> {game.preference_penalties.join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {weights.review > 0 && game.review_component_score !== undefined && (
          <div className="score-component">
            <div className="component-header">
              <span className="component-icon">⭐</span>
              <span className="component-label">Community Reviews</span>
              <span className="component-score">
                {Math.round(game.review_component_score)}/100
              </span>
            </div>
            <div className="component-weight">
              Weight: {(weights.review * 100).toFixed(0)}%
            </div>
            <div className="component-description">
              {game.review_score ? 
                `${Math.round(game.review_score)}% positive from ${game.total_reviews?.toLocaleString() || 0} reviews` : 
                'Community sentiment and review volume'
              }
            </div>
          </div>
        )}
      </div>

      <div className="explanation-footer">
        <small>
          Final score = {mode === 'hybrid' ? 
            'weighted combination of all components' : 
            `${mode} scoring only`
          }
        </small>
      </div>
    </div>
  )
}

ScoreExplanation.propTypes = {
  game: PropTypes.shape({
    score: PropTypes.number.isRequired,
    ml_score: PropTypes.number,
    content_score: PropTypes.number,
    preference_score: PropTypes.number,
    review_component_score: PropTypes.number,
    review_score: PropTypes.number,
    total_reviews: PropTypes.number,
    similar_to: PropTypes.arrayOf(PropTypes.string),
    preference_boosts: PropTypes.arrayOf(PropTypes.string),
    preference_penalties: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  mode: PropTypes.string.isRequired,
}

export default ScoreExplanation
