import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import toast from 'react-hot-toast'
import GameCard from '../components/GameCard'
import FilterControls from '../components/FilterControls'

function Recommendations() {
  const { steamId } = useParams()
  const [recommendations, setRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({
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
  const [tempFilters, setTempFilters] = useState(filters)
  const [showFilters, setShowFilters] = useState(false)

  // Fetch recommendations when component mounts, steamId changes, or filters change
  useEffect(() => {
    fetchRecommendations()
  }, [steamId, filters])

  const fetchRecommendations = async () => {
    setIsLoading(true)
    try {
      // Convert genre_limits and tag_limits arrays to JSON
      const params = {}
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          if (key === 'genre_limits' && Array.isArray(value) && value.length > 0) {
            // Convert array of {genre, limit} to {genre: limit} object
            const genreObj = {}
            value.forEach(item => {
              if (item.genre && item.genre.trim() !== '') {
                genreObj[item.genre.trim()] = item.limit
              }
            })
            if (Object.keys(genreObj).length > 0) {
              params.genre_limits = JSON.stringify(genreObj)
            }
          } else if (key === 'tag_limits' && Array.isArray(value) && value.length > 0) {
            // Convert array of {tag, limit} to {tag: limit} object
            const tagObj = {}
            value.forEach(item => {
              if (item.tag && item.tag.trim() !== '') {
                tagObj[item.tag.trim()] = item.limit
              }
            })
            if (Object.keys(tagObj).length > 0) {
              params.tag_limits = JSON.stringify(tagObj)
            }
          } else if (key === 'series_limits' && Array.isArray(value) && value.length > 0) {
            // Convert array of {series, limit} to {series: limit} object
            const seriesObj = {}
            value.forEach(item => {
              if (item.series && item.series.trim() !== '') {
                seriesObj[item.series.trim()] = item.limit
              }
            })
            if (Object.keys(seriesObj).length > 0) {
              params.series_limits = JSON.stringify(seriesObj)
            }
          } else if (key === 'weight_ml' || key === 'weight_content' || key === 'weight_preference' || key === 'weight_review') {
            // Convert percentage to decimal (35 -> 0.35)
            params[key] = value / 100
          } else {
            params[key] = value
          }
        }
      })

      const response = await api.recommendations.get(steamId, params)
      // Backend returns array directly, not wrapped in {recommendations: []}
      const recs = Array.isArray(response.data) ? response.data : (response.data.recommendations || [])
      
      // Map backend field names to frontend expected names
      const mappedRecs = recs.map(game => ({
        ...game,
        score: game.hybrid_score || game.score || 0,
        review_score: game.review_percentage || game.review_score || 0,
        total_reviews: (game.positive_reviews || 0) + (game.negative_reviews || 0),
        genres: typeof game.genres === 'string' ? game.genres.split(',').map(g => g.trim()).filter(Boolean) : (game.genres || []),
        top_tags: typeof game.tags === 'string' ? Object.keys(JSON.parse(game.tags || '{}')).slice(0, 5) : (game.top_tags || []),
        ml_score: game.ml_score,
        content_score: game.content_score,
        preference_score: game.preference_score,
        review_component_score: game.review_score,
        weight_ml: game.weight_ml,
        weight_content: game.weight_content,
        weight_preference: game.weight_preference,
        weight_review: game.weight_review,
      }))
      
      console.log('[RECS] Raw response:', response.data)
      console.log('[RECS] Mapped recommendations:', mappedRecs)
      setRecommendations(mappedRecs)
      toast.success(`Loaded ${mappedRecs.length} recommendations`)
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
      toast.error('Failed to load recommendations')
      setRecommendations([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleApplyFilters = () => {
    setFilters(tempFilters)
    setShowFilters(false)
  }

  const getModeDescription = (mode) => {
    const descriptions = {
      hybrid: 'AI + Content + Preferences + Reviews',
      ml: 'Machine Learning predictions only',
      content: 'Based on similar games you love',
      preference: 'Tuned to your explicit preferences'
    }
    return descriptions[mode] || mode
  }

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading personalized recommendations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container recommendations-page">
      <div className="recommendations-header">
        <h1>🎮 Your Recommendations</h1>
        <p className="subtitle">
          {recommendations.length} games recommended using <strong>{filters.mode}</strong> mode
        </p>
        <p className="mode-description">
          {getModeDescription(filters.mode)}
        </p>
      </div>

      {/* Filter Toggle Button */}
      <div className="filter-toggle-container">
        <button 
          className="btn btn-secondary filter-toggle-btn"
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? '▼' : '▶'} {showFilters ? 'Hide' : 'Show'} Filters
        </button>
      </div>

      {/* Filter Controls (Collapsible) */}
      {showFilters && (
        <section className="filters-section">
          <FilterControls 
            filters={tempFilters}
            onFilterChange={setTempFilters}
            onApply={handleApplyFilters}
          />
        </section>
      )}

      {/* Recommendations Grid */}
      <section className="recommendations-grid">
        {recommendations.length === 0 ? (
          <div className="empty-state">
            <h2>No recommendations found</h2>
            <p>Try adjusting your filters to see more games.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowFilters(true)}
            >
              Adjust Filters
            </button>
          </div>
        ) : (
          <>
            <div className="recommendations-count">
              <p>Showing {recommendations.length} of {filters.limit} results</p>
            </div>
            <div className="game-cards-grid">
              {recommendations.map((game) => (
                <GameCard 
                  key={game.appid} 
                  game={game}
                  steamId={steamId}
                  mode={filters.mode}
                />
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  )
}

export default Recommendations
