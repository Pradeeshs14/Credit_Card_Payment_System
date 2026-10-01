import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function AddCard() {
  const navigate = useNavigate()

  const [cardType, setCardType] = useState('')
  const [cardNumber, setCardNumber] = useState('')
  const [expiryMonth, setExpiryMonth] = useState('')
  const [expiryYear, setExpiryYear] = useState('')
  const [cvv, setCvv] = useState('')

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')

      await api.post(
        '/cards/',
        {
          card_type: cardType,
          card_number: cardNumber,
          cvv: cvv,
          expiry_month: Number(expiryMonth),
          expiry_year: Number(expiryYear),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setSuccess('Card added successfully.')

      setTimeout(() => {
        navigate('/dashboard')
      }, 1000)

    } catch (error) {
      const responseData = error.response?.data

      if (typeof responseData === 'object') {
        const firstError = Object.values(responseData)?.[0]

        if (Array.isArray(firstError)) {
          setError(firstError[0])
        } else {
          setError(String(firstError || 'Failed to add card.'))
        }
      } else {
        setError('Failed to add card.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">

        <h1 className="text-3xl font-bold text-center text-white mb-2">
          Add Card
        </h1>

        <p className="text-center text-slate-400 mb-8">
          Save your credit or debit card
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-300">
              Card Type
            </label>

            <select
              value={cardType}
              onChange={(event) => setCardType(event.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
            >
              <option value="" disabled>
                Select card type
              </option>

              <option value="CREDIT">
                Credit Card
              </option>

              <option value="DEBIT">
                Debit Card
              </option>
            </select>
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-300">
              Card Number
            </label>

            <input
              type="text"
              inputMode="numeric"
              value={cardNumber}
              onChange={(event) => setCardNumber(event.target.value)}
              placeholder="Enter card number"
              minLength="13"
              maxLength="19"
              required
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">

            <div>
              <label className="block mb-2 text-sm font-medium text-slate-300">
                Expiry Month
              </label>

              <input
                type="number"
                min="1"
                max="12"
                value={expiryMonth}
                onChange={(event) => setExpiryMonth(event.target.value)}
                placeholder="MM"
                required
                className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-slate-300">
                Expiry Year
              </label>

              <input
                type="number"
                value={expiryYear}
                onChange={(event) => setExpiryYear(event.target.value)}
                placeholder="YYYY"
                required
                className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>

          </div>

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-300">
              CVV
            </label>

            <input
              type="password"
              inputMode="numeric"
              value={cvv}
              onChange={(event) => setCvv(event.target.value)}
              maxLength="4"
              placeholder="CVV"
              required
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
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
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold cursor-pointer hover:bg-blue-500 hover:brightness-110 hover:-translate-y-0.5 hover:shadow-xl transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:brightness-100 disabled:hover:translate-y-0 disabled:hover:shadow-none"
          >
            {loading ? 'Adding Card...' : 'Add Card'}
          </button>

        </form>

        <p className="text-xs text-slate-500 text-center mt-5">
          Your full card number and CVV are never stored.
        </p>

      </div>

    </div>
  )
}

export default AddCard

