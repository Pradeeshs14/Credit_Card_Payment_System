import { useEffect, useState } from 'react'
import api from '../services/api'

function AdminDashboard() {
  const [summary, setSummary] = useState({
    total_payments: 0,
    successful_payments: 0,
    failed_payments: 0,
    pending_payments: 0,
    total_amount: 0,
    successful_amount: 0,
  })

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadSummary = async () => {
      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get(
          '/transactions/admin/summary/',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )

        setSummary(response.data)
      } catch (error) {
        console.error('Failed to load admin summary:', error)
        setError('Failed to load payment summary.')
      } finally {
        setLoading(false)
      }
    }

    loadSummary()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <nav className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="max-w-7xl mx-auto">

          <h1 className="text-xl font-bold">
            Admin Dashboard
          </h1>

        </div>
      </nav>

      <main className="p-6 max-w-7xl mx-auto">

        <h2 className="text-3xl font-bold mb-2">
          Payment Summary
        </h2>

        <p className="text-slate-400 mb-8">
          Monitor daily payment activity
        </p>

        {loading && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <p className="text-slate-400">
              Loading payment summary...
            </p>
          </div>
        )}

        {error && (
          <div className="bg-slate-900 border border-red-900 rounded-2xl p-6">
            <p className="text-red-400">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg cursor-default hover:bg-slate-800 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-in-out">

              <h3 className="text-slate-400">
                Total Payments
              </h3>

              <p className="text-3xl font-bold mt-2">
                {summary.total_payments}
              </p>

            </div>

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg cursor-default hover:bg-slate-800 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-in-out">

              <h3 className="text-slate-400">
                Successful
              </h3>

              <p className="text-3xl font-bold text-green-400 mt-2">
                {summary.successful_payments}
              </p>

            </div>

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg cursor-default hover:bg-slate-800 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-in-out">

              <h3 className="text-slate-400">
                Failed
              </h3>

              <p className="text-3xl font-bold text-red-400 mt-2">
                {summary.failed_payments}
              </p>

            </div>

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg cursor-default hover:bg-slate-800 hover:brightness-110 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-in-out">

              <h3 className="text-slate-400">
                Total Amount
              </h3>

              <p className="text-3xl font-bold mt-2">
                ₹{Number(summary.total_amount).toLocaleString('en-IN')}
              </p>

            </div>

          </div>
        )}

      </main>
    </div>
  )
}

export default AdminDashboard

