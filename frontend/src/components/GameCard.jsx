import { useState } from 'react'
import { api } from '../api/client'
import toast from 'react-hot-toast'
import PropTypes from 'prop-types'
import ScoreExplanation from './ScoreExplanation'

function GameCard({ game, steamId, mode }) {
  const [showExplanation, setShowExplanation] = useState(false)
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)

  const handleFeedback = async (action) => {
    if (isSubmittingFeedback) return
    
    setIsSubmittingFeedback(true)
    try {
      await api.feedback.submit({
        steam_id: parseInt(steamId),
        appid: game.appid,
        action: action,
        recommendation_mode: mode,
        score_at_time: game.score
      })
      
      const actionText = action === 'interested' ? '👍 Marked as interested' : '👎 Dismissed'
      toast.success(actionText)
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      toast.error('Failed to submit feedback')
    } finally {
      setIsSubmittingFeedback(false)
    }
  }

  // Format price
  const formatPrice = (price) => {
    if (price === 0) return 'Free'
    if (price === null || price === undefined) return 'N/A'
    return `$${price.toFixed(2)}`
  }

  // Format playtime estimate
  const formatPlaytime = (minutes) => {
    if (!minutes) return 'N/A'
    if (minutes < 60) return `${Math.round(minutes)}m`
    const hours = Math.round(minutes / 60)
    return `${hours}h`
  }

  // Get score color
  const getScoreColor = (score) => {
    if (score >= 80) return '#4caf50'
    if (score >= 60) return '#ff9800'
    return '#f44336'
  }

  return (
    <div className="game-card">
      <div className="game-image">
        <img 
          src={game.header_image || '/placeholder-game.png'} 
          alt={game.name}
          onError={(e) => e.target.src = '/placeholder-game.png'}
          loading="lazy"
        />
        {game.is_on_sale && (
          <div className="sale-badge">ON SALE</div>
        )}
      </div>

      <div className="game-info">
        <h3 className="game-title">{game.name}</h3>
        <p className="game-developer">{game.developer || 'Unknown Developer'}</p>

        {/* Match Score */}
        <div className="game-score-container">
          <div 
            className="game-score" 
            style={{ '--score-color': getScoreColor(game.score) }}
          >
            <span className="score-value">{Math.round(game.score)}</span>
            <span className="score-label">/100</span>
          </div>
          <span className="score-text">Match Score</span>
        </div>

        {/* Price and Reviews Row */}
        <div className="game-meta">
          <div className="game-price">
            <span className="price-value">{formatPrice(game.price)}</span>
          </div>
          <div className="game-reviews">
            <span className="review-percentage">
              {game.review_score ? `${Math.round(game.review_score)}%` : 'N/A'}
            </span>
            <span className="review-count">
              ({game.total_reviews?.toLocaleString() || 0} reviews)
            </span>
          </div>
        </div>

        {/* Genres and Tags */}
        <div className="game-tags">
          {game.genres?.slice(0, 3).map((genre, idx) => (
            <span key={idx} className="tag tag-genre">{genre}</span>
          ))}
          {game.top_tags?.slice(0, 2).map((tag, idx) => (
            <span key={idx} className="tag tag-tag">{tag}</span>
          ))}
        </div>

        {/* Playtime Estimate */}
        {game.median_playtime && (
          <div className="game-playtime">
            <span className="playtime-label">Avg. Playtime:</span>
            <span className="playtime-value">{formatPlaytime(game.median_playtime)}</span>
          </div>
        )}

        {/* Expandable Explanation */}
        <div className="game-explanation">
          <button 
            className="explanation-toggle"
            onClick={() => setShowExplanation(!showExplanation)}
          >
            {showExplanation ? '▼' : '▶'} Why recommended?
          </button>
          {showExplanation && (
            <ScoreExplanation game={game} mode={mode} />
          )}
        </div>

        {/* Action Buttons */}
        <div className="game-actions">
          <button 
            className="btn btn-small btn-danger"
            onClick={() => handleFeedback('dismissed')}
            disabled={isSubmittingFeedback}
          >
            👎 Not Interested
          </button>
          <button 
            className="btn btn-small btn-success"
            onClick={() => handleFeedback('interested')}
            disabled={isSubmittingFeedback}
          >
            👍 Interested
          </button>
          <a 
            href={`https://store.steampowered.com/app/${game.appid}`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-small btn-primary"
          >
            🔗 View on Steam
          </a>
        </div>
      </div>
    </div>
  )
}

GameCard.propTypes = {
  game: PropTypes.shape({
    appid: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    header_image: PropTypes.string,
    developer: PropTypes.string,
    score: PropTypes.number.isRequired,
    price: PropTypes.number,
    is_on_sale: PropTypes.bool,
    review_score: PropTypes.number,
    total_reviews: PropTypes.number,
    genres: PropTypes.arrayOf(PropTypes.string),
    top_tags: PropTypes.arrayOf(PropTypes.string),
    median_playtime: PropTypes.number,
    ml_score: PropTypes.number,
    content_score: PropTypes.number,
    preference_score: PropTypes.number,
    review_component_score: PropTypes.number,
  }).isRequired,
  steamId: PropTypes.string.isRequired,
  mode: PropTypes.string.isRequired,
}

export default GameCard
