import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function Dashboard() {
  const navigate = useNavigate()

  const [cardCount, setCardCount] = useState(0)
  const [transactionCount, setTransactionCount] = useState(0)
  const [successfulCount, setSuccessfulCount] = useState(0)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const token = localStorage.getItem('access_token')

        const [cardsResponse, transactionsResponse] = await Promise.all([
          api.get('/cards/', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),

          api.get('/transactions/', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ])

        const cards = cardsResponse.data
        const transactions = transactionsResponse.data

        setCardCount(cards.length)
        setTransactionCount(transactions.length)

        const successfulPayments = transactions.filter(
          (transaction) => transaction.status === 'SUCCESS'
        )

        setSuccessfulCount(successfulPayments.length)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      }
    }

    loadDashboardData()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <nav className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">

          <h1 className="text-xl font-bold">
            Credit Card Payment System
          </h1>

          <button
            onClick={handleLogout}
            className="cursor-pointer bg-red-600 hover:bg-red-500 hover:brightness-110 hover:-translate-y-0.5 hover:shadow-lg px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ease-in-out"
          >
            Logout
          </button>

        </div>
      </nav>

      <main className="p-6 max-w-7xl mx-auto">

        <h2 className="text-3xl font-bold mb-2">
          Dashboard
        </h2>

        <p className="text-slate-400 mb-8">
          Manage your cards and payments
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
            <h3 className="text-slate-400">
              Saved Cards
            </h3>

            <p className="text-3xl font-bold mt-2">
              {cardCount}
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
            <h3 className="text-slate-400">
              Total Transactions
            </h3>

            <p className="text-3xl font-bold mt-2">
              {transactionCount}
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
            <h3 className="text-slate-400">
              Successful Payments
            </h3>

            <p className="text-3xl font-bold text-green-400 mt-2">
              {successfulCount}
            </p>
          </div>

        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">

          <button
            onClick={() => navigate('/add-card')}
            className="cursor-pointer bg-blue-600 hover:bg-blue-500 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl p-6 rounded-2xl text-left transition-all duration-300 ease-in-out"
          >
            <h3 className="text-xl font-bold">
              Add Card
            </h3>

            <p className="text-blue-100 mt-2">
              Add a new credit or debit card
            </p>
          </button>

          <button
            onClick={() => navigate('/payment')}
            className="cursor-pointer bg-green-600 hover:bg-green-500 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl p-6 rounded-2xl text-left transition-all duration-300 ease-in-out"
          >
            <h3 className="text-xl font-bold">
              Make Payment
            </h3>

            <p className="text-green-100 mt-2">
              Make a payment using your saved card
            </p>
          </button>

          <button
            onClick={() => navigate('/transactions')}
            className="cursor-pointer bg-purple-600 hover:bg-purple-500 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl p-6 rounded-2xl text-left transition-all duration-300 ease-in-out"
          >
            <h3 className="text-xl font-bold">
              Transaction History
            </h3>

            <p className="text-purple-100 mt-2">
              View your payment transactions
            </p>
          </button>

        </div>

      </main>
    </div>
  )
}

export default Dashboard

