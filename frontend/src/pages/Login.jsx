import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import api from '../services/api'

function Login() {
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

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)

      navigate('/dashboard')
    } catch (error) {
      setError(
        error.response?.data?.detail ||
        'Invalid username or password.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">

        <h1 className="text-3xl font-bold text-center text-white mb-2">
          Welcome Back
        </h1>

        <p className="text-center text-slate-400 mb-8">
          Login to your account
        </p>

        <form onSubmit={handleLogin} className="space-y-5">

          <div>

            <label className="block mb-2 text-sm font-medium text-slate-300">
              Username
            </label>

            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter username"
              required
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

          </div>

          <div>

            <label className="block mb-2 text-sm font-medium text-slate-300">
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter password"
              required
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

          </div>

          {error && (
            <p className="text-red-400 text-sm">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-500 transition disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

        </form>

        <p className="text-center text-slate-400 text-sm mt-6">
          Don't have an account?{' '}

          <button
            type="button"
            onClick={() => navigate('/register')}
            className="text-blue-400 hover:text-blue-300"
          >
            Register
          </button>
        </p>

        <div className="border-t border-slate-800 mt-6 pt-6">

          <button
            type="button"
            onClick={() => navigate('/admin-login')}
            className="w-full text-slate-400 hover:text-white text-sm transition"
          >
            Admin Login
          </button>

        </div>

      </div>

    </div>
  )
}

export default Login

