import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function MakePayment() {
  const navigate = useNavigate()

  const [cards, setCards] = useState([])
  const [selectedCard, setSelectedCard] = useState('')
  const [amount, setAmount] = useState('')

  const [loadingCards, setLoadingCards] = useState(true)
  const [loadingPayment, setLoadingPayment] = useState(false)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const loadCards = async () => {
      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/cards/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setCards(response.data)
      } catch (error) {
        console.error('Failed to load cards:', error)
        setError('Failed to load saved cards.')
      } finally {
        setLoadingCards(false)
      }
    }

    loadCards()
  }, [])

  const handlePayment = async (event) => {
    event.preventDefault()

    setError('')
    setSuccess('')
    setLoadingPayment(true)

    try {
      const token = localStorage.getItem('access_token')

      const userResponse = await api.get('/users/me/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      const userId = userResponse.data.id

      const paymentResponse = await fetch(
        'http://127.0.0.1:8001/api/payments/',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            card_id: Number(selectedCard),
            amount: Number(amount),
          }),
        }
      )

      const paymentData = await paymentResponse.json()

      if (!paymentResponse.ok) {
        throw new Error(
          paymentData.detail || 'Payment failed.'
        )
      }

      if (paymentData.status === 'SUCCESS') {
        setSuccess(
          `Payment successful. Transaction ID: ${paymentData.transaction_id}`
        )
      } else {
        setError(
          `Payment failed. Transaction ID: ${paymentData.transaction_id}`
        )
      }

      setAmount('')
      setSelectedCard('')

    } catch (error) {
      console.error('Payment error:', error)
      setError(error.message || 'Payment failed.')
    } finally {
      setLoadingPayment(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">

        <h1 className="text-3xl font-bold text-center text-white mb-2">
          Make Payment
        </h1>

        <p className="text-center text-slate-400 mb-8">
          Make a secure payment
        </p>

        <form
          onSubmit={handlePayment}
          className="space-y-5"
        >

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-300">
              Select Card
            </label>

            {loadingCards ? (
              <p className="text-slate-400 text-sm">
                Loading cards...
              </p>
            ) : cards.length === 0 ? (
              <p className="text-red-400 text-sm">
                No saved cards found.
              </p>
            ) : (
              <select
                value={selectedCard}
                onChange={(event) => setSelectedCard(event.target.value)}
                required
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300 cursor-pointer"
              >
                <option value="" disabled>
                  Select a saved card
                </option>

                {cards.map((card) => (
                  <option key={card.id} value={card.id}>
                    {card.card_type} {card.masked_card_number}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-300">
              Amount
            </label>

            <input
              type="number"
              min="1"
              step="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              placeholder="Enter amount"
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
            disabled={
              loadingPayment ||
              loadingCards ||
              cards.length === 0
            }
            className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold cursor-pointer hover:bg-green-500 hover:brightness-110 hover:-translate-y-0.5 hover:shadow-xl transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:brightness-100 disabled:hover:translate-y-0 disabled:hover:shadow-none"
          >
            {loadingPayment ? 'Processing Payment...' : 'Pay Now'}
          </button>

        </form>

        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="w-full mt-4 text-slate-400 hover:text-white hover:brightness-125 cursor-pointer transition-all duration-300"
        >
          Back to Dashboard
        </button>

      </div>

    </div>
  )
}

export default MakePayment

