import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import toast from 'react-hot-toast'

function Profile() {
  const { steamId } = useParams()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)

  useEffect(() => {
    // Get logged-in user's Steam ID from localStorage
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      toast.error('Please log in first')
      navigate('/')
      return
    }

    const user = JSON.parse(userStr)
    
    // If URL steam ID doesn't match logged-in user, redirect to correct profile
    // Compare as strings since steam_id is stored as string
    if (steamId && String(steamId) !== String(user.steam_id)) {
      console.log(`Redirecting from ${steamId} to ${user.steam_id}`)
      navigate(`/profile/${user.steam_id}`, { replace: true })
      return
    }

    fetchProfile(user.steam_id)
    fetchStats(user.steam_id)
  }, [steamId, navigate])

  const fetchProfile = async (id) => {
    try {
      console.log('[PROFILE] Fetching profile for Steam ID:', id)
      const response = await api.profile.get(id)
      console.log('[PROFILE] Profile response:', response.data)
      setProfile(response.data)
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      toast.error('Failed to load profile')
    }
  }

  const fetchStats = async (id) => {
    try {
      console.log('[PROFILE] Fetching stats for Steam ID:', id)
      const response = await api.profile.getStats(id)
      console.log('[PROFILE] Stats response:', response.data)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      toast.error('Failed to load statistics')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSync = async () => {
    setIsSyncing(true)
    try {
      await api.profile.sync(steamId)
      toast.success('Library synced successfully!')
      // Refresh data
      fetchProfile()
      fetchStats()
    } catch (error) {
      console.error('Sync failed:', error)
      toast.error('Failed to sync library')
    } finally {
      setIsSyncing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading profile...</div>
      </div>
    )
  }

  return (
    <div className="page-container profile-page">
      <div className="profile-header">
        <h1>Gaming Profile</h1>
        <button 
          onClick={handleSync} 
          disabled={isSyncing}
          className="btn btn-secondary"
        >
          {isSyncing ? 'Syncing...' : '🔄 Sync Library'}
        </button>
      </div>

      {profile && stats && (
        <>
          <section className="stats-overview">
            <div className="stat-card">
              <div className="stat-value">{stats.total_games || 0}</div>
              <div className="stat-label">Games Owned</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_playtime_hours || 0}</div>
              <div className="stat-label">Hours Played</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.top_genre || 'N/A'}</div>
              <div className="stat-label">Top Genre</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.gaming_style || 'Explorer'}</div>
              <div className="stat-label">Gaming Style</div>
            </div>
          </section>

          <section className="visualizations-section">
            <h2>Your Gaming Analytics</h2>
            <p className="section-note">Visualizations coming in Week 3...</p>
            {/* Visualization components will be added in Week 3 */}
          </section>
        </>
      )}
    </div>
  )
}

export default Profile
