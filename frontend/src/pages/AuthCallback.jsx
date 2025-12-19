import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import apiClient from '../api/client'
import toast from 'react-hot-toast'

function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('Verifying your Steam login...')

  useEffect(() => {
    const handleCallback = () => {
      try {
        // Get query parameters from URL
        const token = searchParams.get('token')
        const userStr = searchParams.get('user')
        
        console.log('[AUTH_CALLBACK] Raw URL:', window.location.href)
        console.log('[AUTH_CALLBACK] Raw userStr from query:', userStr)
        
        if (!token || !userStr) {
          throw new Error('Missing authentication data')
        }
        
        // Parse user data
        const user = JSON.parse(decodeURIComponent(userStr))
        
        // Ensure steam_id is stored as string to avoid precision loss
        if (typeof user.steam_id === 'number') {
          console.warn('[AUTH_CALLBACK] WARNING: steam_id received as number, may have precision loss')
        }
        user.steam_id = String(user.steam_id)
        
        console.log('[AUTH_CALLBACK] Parsed user object:', user)
        console.log('[AUTH_CALLBACK] user.steam_id:', user.steam_id, 'type:', typeof user.steam_id)
        
        // Store token and user info
        localStorage.setItem('access_token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        console.log('[AUTH_CALLBACK] Stored in localStorage:', localStorage.getItem('user'))
        
        setStatus('Login successful! Redirecting...')
        toast.success(`Welcome back, ${user.username}!`)
        
        // Redirect to profile
        setTimeout(() => {
          console.log('[AUTH_CALLBACK] Navigating to /profile/' + user.steam_id)
          navigate(`/profile/${user.steam_id}`)
        }, 1000)
      } catch (error) {
        console.error('Auth callback error:', error)
        setStatus('Login failed. Redirecting...')
        toast.error('Steam login failed. Please try again.')
        
        setTimeout(() => {
          navigate('/')
        }, 2000)
      }
    }

    handleCallback()
  }, [navigate, searchParams])

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '80vh',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <div style={{
        fontSize: '3rem',
        animation: 'spin 1s linear infinite'
      }}>
        🎮
      </div>
      <h2 style={{
        fontFamily: 'var(--font-heading)',
        color: 'var(--color-text-primary)',
        fontSize: '1.5rem'
      }}>
        {status}
      </h2>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default AuthCallback
