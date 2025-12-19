import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import Profile from './pages/Profile'
import Recommendations from './pages/Recommendations'
import AuthCallback from './pages/AuthCallback'

function App() {
  return (
    <div className="app">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e2329',
            color: '#c7d5e0',
            border: '1px solid #374151',
          },
          success: {
            iconTheme: {
              primary: '#5ba32b',
              secondary: '#1e2329',
            },
          },
          error: {
            iconTheme: {
              primary: '#cd2a2a',
              secondary: '#1e2329',
            },
          },
        }}
      />
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/profile/:steamId" element={<Profile />} />
          <Route path="/recommendations/:steamId" element={<Recommendations />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App
