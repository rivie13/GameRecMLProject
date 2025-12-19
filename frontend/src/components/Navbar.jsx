import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import apiClient from '../api/client'
import toast from 'react-hot-toast'

function Navbar() {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    checkAuth()
    
    // Listen for storage changes (e.g., login in another tab)
    const handleStorageChange = () => {
      checkAuth()
    }
    window.addEventListener('storage', handleStorageChange)
    
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const checkAuth = () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        setUser(JSON.parse(userStr))
      } catch (error) {
        console.error('Failed to parse user data:', error)
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }

  const handleLogout = async () => {
    try {
      await apiClient.post('/api/auth/logout')
      toast.success('Logged out successfully')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      setUser(null)
      navigate('/')
    }
  }

  const handleLogin = () => {
    // Redirect to backend Steam OAuth endpoint
    window.location.href = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/steam/login`
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">🎮</span>
          <span className="brand-text">GameRec AI</span>
        </Link>

        <div className="navbar-menu">
          {!isLoading && (
            <>
              {user ? (
                <>
                  <Link to={`/profile/${user.steam_id}`} className="nav-link">
                    Profile
                  </Link>
                  <Link to={`/recommendations/${user.steam_id}`} className="nav-link">
                    Recommendations
                  </Link>
                  <div className="nav-user">
                    {user.avatar_url && (
                      <img 
                        src={user.avatar_url} 
                        alt={user.username} 
                        className="user-avatar"
                      />
                    )}
                    <span className="user-name">{user.username}</span>
                  </div>
                  <button onClick={handleLogout} className="btn btn-secondary">
                    Logout
                  </button>
                </>
              ) : (
                <button onClick={handleLogin} className="btn btn-primary">
                  <span>Login with Steam</span>
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
