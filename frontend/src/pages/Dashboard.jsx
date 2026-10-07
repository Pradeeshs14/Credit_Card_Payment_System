import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { dashboardApi } from '../services/api'

function Dashboard() {
  const navigate = useNavigate()

  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const token = localStorage.getItem('access_token')

        if (!token) {
          setError('Your session has expired. Please login again.')
          setLoading(false)
          return
        }

        const response = await dashboardApi.get('/dashboard/summary', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setDashboardData(response.data)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)

        if (error.response?.status === 401) {
          setError('Your session has expired. Please login again.')
        } else {
          setError('Unable to load dashboard data. Please try again.')
        }
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/')
  }

  const formatCurrency = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  const getStatusClass = (status) => {
    if (status === 'SUCCESS') {
      return 'bg-green-500/10 text-green-400 border border-green-500/20'
    }

    if (status === 'FAILED') {
      return 'bg-red-500/10 text-red-400 border border-red-500/20'
    }

    return 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
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
          Track your credit card spending and transactions
        </p>

        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-5 py-4 rounded-xl">
            {error}
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

            {[1, 2, 3, 4].map((item) => (
              <div
                key={item}
                className="bg-slate-900 border border-slate-800 p-6 rounded-2xl animate-pulse"
              >
                <div className="h-4 w-28 bg-slate-800 rounded mb-4"></div>
                <div className="h-8 w-36 bg-slate-800 rounded"></div>
              </div>
            ))}

          </div>
        ) : dashboardData ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                <h3 className="text-slate-400 text-sm">
                  Total Spent
                </h3>

                <p className="text-3xl font-bold mt-3">
                  {formatCurrency(dashboardData.total_amount_spent)}
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                <h3 className="text-slate-400 text-sm">
                  Available Credit
                </h3>

                <p className="text-3xl font-bold text-blue-400 mt-3">
                  {formatCurrency(dashboardData.available_credit_limit)}
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                <h3 className="text-slate-400 text-sm">
                  Total Transactions
                </h3>

                <p className="text-3xl font-bold mt-3">
                  {dashboardData.total_transactions}
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                <h3 className="text-slate-400 text-sm">
                  This Month Spending
                </h3>

                <p className="text-3xl font-bold text-purple-400 mt-3">
                  {formatCurrency(dashboardData.current_month_spending)}
                </p>
              </div>

            </div>

            <div className="mt-8 bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">

              <div className="p-6 border-b border-slate-800">
                <h3 className="text-xl font-bold">
                  Recent Transactions
                </h3>

                <p className="text-slate-400 text-sm mt-1">
                  Your latest 5 transactions
                </p>
              </div>

              {dashboardData.last_5_transactions.length === 0 ? (
                <div className="p-8 text-center text-slate-400">
                  No transactions found.
                </div>
              ) : (
                <div className="overflow-x-auto">

                  <table className="w-full">

                    <thead>
                      <tr className="text-left text-slate-400 text-sm border-b border-slate-800">
                        <th className="px-6 py-4">Amount</th>
                        <th className="px-6 py-4">Card</th>
                        <th className="px-6 py-4">Date</th>
                        <th className="px-6 py-4">Status</th>
                      </tr>
                    </thead>

                    <tbody>
                      {dashboardData.last_5_transactions.map(
                        (transaction, index) => (
                          <tr
                            key={`${transaction.date}-${index}`}
                            className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/50 transition"
                          >
                            <td className="px-6 py-4 font-semibold">
                              {formatCurrency(transaction.amount)}
                            </td>

                            <td className="px-6 py-4 text-slate-300">
                              {transaction.masked_card_number}
                            </td>

                            <td className="px-6 py-4 text-slate-400">
                              {formatDate(transaction.date)}
                            </td>

                            <td className="px-6 py-4">
                              <span
                                className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold ${getStatusClass(
                                  transaction.status
                                )}`}
                              >
                                {transaction.status}
                              </span>
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>

                  </table>

                </div>
              )}

            </div>
          </>
        ) : null}

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