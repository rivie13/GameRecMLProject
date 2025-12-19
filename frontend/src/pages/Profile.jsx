import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import toast from 'react-hot-toast'

function Profile() {
  const { steamId } = useParams()
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)

  useEffect(() => {
    fetchProfile()
    fetchStats()
  }, [steamId])

  const fetchProfile = async () => {
    try {
      const response = await api.profile.get(steamId)
      setProfile(response.data)
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.profile.getStats(steamId)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
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
              <div className="stat-value">{stats.total_hours || 0}</div>
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
