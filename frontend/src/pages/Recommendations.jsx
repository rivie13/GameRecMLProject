import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import toast from 'react-hot-toast'

function Recommendations() {
  const { steamId } = useParams()
  const [recommendations, setRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({
    mode: 'hybrid',
    limit: 20,
    min_reviews: 5000,
    min_review_score: 70,
    sfw_only: true,
    exclude_early_access: true,
  })

  useEffect(() => {
    fetchRecommendations()
  }, [steamId, filters])

  const fetchRecommendations = async () => {
    setIsLoading(true)
    try {
      const response = await api.recommendations.get(steamId, filters)
      setRecommendations(response.data.recommendations || [])
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
      toast.error('Failed to load recommendations')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading recommendations...</div>
      </div>
    )
  }

  return (
    <div className="page-container recommendations-page">
      <div className="recommendations-header">
        <h1>Your Recommendations</h1>
        <p className="subtitle">
          {recommendations.length} games recommended based on {filters.mode} mode
        </p>
      </div>

      <section className="filters-section">
        <h3>Filters</h3>
        <p className="section-note">Filter controls coming in Week 3...</p>
        {/* Filter components will be added in Week 3 */}
      </section>

      <section className="recommendations-grid">
        {recommendations.length === 0 ? (
          <div className="empty-state">
            <p>No recommendations found. Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="game-cards-grid">
            {recommendations.map((game) => (
              <div key={game.appid} className="game-card">
                <div className="game-image">
                  <img 
                    src={game.header_image || '/placeholder-game.png'} 
                    alt={game.name}
                    onError={(e) => e.target.src = '/placeholder-game.png'}
                  />
                </div>
                <div className="game-info">
                  <h3 className="game-title">{game.name}</h3>
                  <div className="game-score">
                    <span className="score-value">{Math.round(game.score)}/100</span>
                    <span className="score-label">Match</span>
                  </div>
                  <p className="game-developer">{game.developer || 'Unknown'}</p>
                  <div className="game-tags">
                    {game.genres?.slice(0, 3).map((genre, idx) => (
                      <span key={idx} className="tag">{genre}</span>
                    ))}
                  </div>
                  <div className="game-actions">
                    <a 
                      href={`https://store.steampowered.com/app/${game.appid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-small btn-primary"
                    >
                      View on Steam
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default Recommendations
