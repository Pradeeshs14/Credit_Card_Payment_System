import { useEffect, useState } from 'react'
import api from '../services/api'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/transactions/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setTransactions(response.data)
      } catch (error) {
        console.error('Failed to load transactions:', error)
        setError('Failed to load transactions.')
      } finally {
        setLoading(false)
      }
    }

    loadTransactions()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">

      <div className="max-w-6xl mx-auto">

        <h1 className="text-3xl font-bold mb-2">
          Transaction History
        </h1>

        <p className="text-slate-400 mb-8">
          View your payment transactions
        </p>

        {loading && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <p className="text-slate-400">
              Loading transactions...
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

        {!loading && !error && transactions.length === 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <p className="text-slate-400">
              No transactions found.
            </p>
          </div>
        )}

        {!loading && !error && transactions.length > 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-x-auto">

            <table className="w-full text-left">

              <thead className="bg-slate-800">

                <tr>

                  <th className="px-6 py-4 text-slate-300">
                    Transaction ID
                  </th>

                  <th className="px-6 py-4 text-slate-300">
                    Card
                  </th>

                  <th className="px-6 py-4 text-slate-300">
                    Amount
                  </th>

                  <th className="px-6 py-4 text-slate-300">
                    Status
                  </th>

                  <th className="px-6 py-4 text-slate-300">
                    Date
                  </th>

                </tr>

              </thead>

              <tbody>

                {transactions.map((transaction) => (

                  <tr
                    key={transaction.id}
                    className="border-t border-slate-800 hover:bg-slate-800/70 hover:brightness-110 transition-all duration-300 ease-in-out cursor-default"
                  >

                    <td className="px-6 py-4 font-medium">
                      {transaction.transaction_id}
                    </td>

                    <td className="px-6 py-4 text-slate-300">
                    {transaction.card_masked}
                    </td>

                    <td className="px-6 py-4 font-medium">
                      ₹{Number(transaction.amount).toLocaleString('en-IN', {
                        minimumFractionDigits: 2,
                      })}
                    </td>

                    <td
                      className={`px-6 py-4 font-medium ${
                        transaction.status === 'SUCCESS'
                          ? 'text-green-400'
                          : transaction.status === 'FAILED'
                            ? 'text-red-400'
                            : 'text-yellow-400'
                      }`}
                    >
                      {transaction.status}
                    </td>

                    <td className="px-6 py-4 text-slate-300">
                      {new Date(
                        transaction.created_at
                      ).toLocaleDateString('en-IN')}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  )
}

export default Transactions

