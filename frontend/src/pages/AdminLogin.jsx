import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function AdminLogin() {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (event) => {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      const response = await api.post('/users/login/', {
        username,
        password,
      })

      const token = response.data.access
      const refreshToken = response.data.refresh

      const userResponse = await api.get('/users/me/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!userResponse.data.is_staff) {
        setError('Admin access required.')
        setLoading(false)
        return
      }

      localStorage.setItem('access_token', token)
      localStorage.setItem('refresh_token', refreshToken)

      navigate('/admin')
    } catch (error) {
      console.error('Admin login failed:', error)

      if (error.response?.status === 401) {
        setError('Invalid admin username or password.')
      } else {
        setError('Unable to login. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-6">

      <div className="w-full max-w-md">

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">

          <div className="text-center mb-8">

            <h1 className="text-3xl font-bold">
              Admin Login
            </h1>

            <p className="text-slate-400 mt-2">
              Sign in to access the administration panel
            </p>

          </div>

          {error && (
            <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">

            <div>

              <label className="block text-sm font-medium text-slate-300 mb-2">
                Username
              </label>

              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white outline-none focus:border-blue-500"
                placeholder="Enter admin username"
              />

            </div>

            <div>

              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white outline-none focus:border-blue-500"
                placeholder="Enter admin password"
              />

            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed px-4 py-3 rounded-lg font-semibold transition"
            >
              {loading ? 'Signing in...' : 'Admin Login'}
            </button>

          </form>

          <button
            onClick={() => navigate('/')}
            className="w-full mt-4 text-slate-400 hover:text-white text-sm transition"
          >
            Back to User Login
          </button>

        </div>

      </div>

    </div>
  )
}

export default AdminLogin