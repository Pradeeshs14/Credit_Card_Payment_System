import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function Register() {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRegister = async (event) => {
    event.preventDefault()

    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await api.post('/users/register/', {
        username,
        email,
        password,
      })

      setSuccess('Account created successfully.')

      setTimeout(() => {
        navigate('/')
      }, 1000)

    } catch (error) {
      const responseData = error.response?.data

      if (typeof responseData === 'object') {
        const firstError = Object.values(responseData)?.[0]

        if (Array.isArray(firstError)) {
          setError(firstError[0])
        } else {
          setError(String(firstError || 'Registration failed.'))
        }
      } else {
        setError('Registration failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">

        <h1 className="text-3xl font-bold text-center text-white mb-2">
          Create Account
        </h1>

        <p className="text-center text-slate-400 mb-8">
          Create your account to get started
        </p>

        <form
          onSubmit={handleRegister}
          className="space-y-5"
        >

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
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter email"
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
              minLength="8"
              required
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm">
              {error}
            </p>
          )}

          {success && (
            <p className="text-green-400 text-sm">
              {success}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-500 transition disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>

        </form>

        <p className="text-center text-slate-400 text-sm mt-6">
          Already have an account?{' '}

          <button
            type="button"
            onClick={() => navigate('/')}
            className="text-blue-400 hover:text-blue-300"
          >
            Login
          </button>
        </p>

      </div>

    </div>
  )
}

export default Register

