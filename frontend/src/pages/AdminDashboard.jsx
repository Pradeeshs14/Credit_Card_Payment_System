import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import api from '../services/api'

function AdminDashboard() {
  const navigate = useNavigate()

  const [summary, setSummary] = useState({
    total_payments: 0,
    successful_payments: 0,
    failed_payments: 0,
    pending_payments: 0,
    total_amount: 0,
    successful_amount: 0,
  })

  const [cards, setCards] = useState([])

  const [loading, setLoading] = useState(true)
  const [cardsLoading, setCardsLoading] = useState(true)

  const [error, setError] = useState('')
  const [cardError, setCardError] = useState('')

  const [selectedCard, setSelectedCard] = useState(null)
  const [activity, setActivity] = useState([])
  const [activityLoading, setActivityLoading] = useState(false)

 const [creditLimits, setCreditLimits] = useState({})
  const [updatingCardId, setUpdatingCardId] = useState(null)
  const [blockingCardId, setBlockingCardId] = useState(null)

  useEffect(() => {
    const loadAdminDashboard = async () => {
      try {
        const token = localStorage.getItem('access_token')

        if (!token) {
          navigate('/admin-login')
          return
        }

        const headers = {
          Authorization: `Bearer ${token}`,
        }

        // Check admin access
        const userResponse = await api.get(
          '/users/me/',
          {
            headers,
          }
        )

        if (!userResponse.data.is_staff) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          navigate('/admin-login')
          return
        }

        // Load payment summary
        const summaryResponse = await api.get(
          '/transactions/admin/summary/',
          {
            headers,
          }
        )

        setSummary(summaryResponse.data)

        // Load all cards
        const cardsResponse = await api.get(
          '/cards/admin/',
          {
            headers,
          }
        )

        setCards(cardsResponse.data)
      } catch (error) {
        console.error(
          'Failed to load admin dashboard:',
          error
        )

        if (
          error.response?.status === 401 ||
          error.response?.status === 403
        ) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          navigate('/admin-login')
          return
        }

        setError('Failed to load admin dashboard.')
      } finally {
        setLoading(false)
        setCardsLoading(false)
      }
    }

    loadAdminDashboard()
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    navigate('/admin-login')
  }

  const handleBlockToggle = async (card) => {
    try {
      setBlockingCardId(card.id)
      setCardError('')

      const token = localStorage.getItem('access_token')

      const response = await api.patch(
        `/cards/${card.id}/block/`,
        {
          is_blocked: !card.is_blocked,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setCards((currentCards) =>
        currentCards.map((currentCard) =>
          currentCard.id === card.id
            ? {
                ...currentCard,
                is_blocked:
                  response.data.is_blocked ??
                  !card.is_blocked,
              }
            : currentCard
        )
      )
    } catch (error) {
      console.error(
        'Failed to update card status:',
        error
      )

      if (
        error.response?.status === 401 ||
        error.response?.status === 403
      ) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/admin-login')
        return
      }

      setCardError(
        error.response?.data?.detail ||
          'Failed to update card status.'
      )
    } finally {
      setBlockingCardId(null)
    }
  }

  const handleCreditLimitUpdate = async (card) => {
    const newLimit = Number(creditLimits[card.id])

    if (!newLimit || newLimit <= 0) {
      setCardError(
        'Credit limit must be greater than zero.'
      )
      return
    }

    try {
      setUpdatingCardId(card.id)
      setCardError('')

      const token = localStorage.getItem('access_token')

      const response = await api.patch(
        `/cards/${card.id}/credit-limit/`,
        {
          credit_limit: newLimit,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setCards((currentCards) =>
        currentCards.map((currentCard) =>
          currentCard.id === card.id
            ? {
                ...currentCard,
                credit_limit:
                  response.data.credit_limit ??
                  newLimit,
              }
            : currentCard
        )
      )

      setCreditLimits((currentLimits) => ({
      ...currentLimits,
      [card.id]: '',
      }))
    } catch (error) {
      console.error(
        'Failed to update credit limit:',
        error
      )

      if (
        error.response?.status === 401 ||
        error.response?.status === 403
      ) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/admin-login')
        return
      }

      const backendError =
        error.response?.data?.credit_limit

      if (backendError) {
        setCardError(
          Array.isArray(backendError)
            ? backendError[0]
            : backendError
        )
      } else {
        setCardError(
          'Failed to update credit limit.'
        )
      }
    } finally {
      setUpdatingCardId(null)
    }
  }

  const handleViewActivity = async (card) => {
    try {
      setSelectedCard(card)
      setActivity([])
      setActivityLoading(true)
      setCardError('')

      const token = localStorage.getItem('access_token')

      const response = await api.get(
        `/transactions/admin/card/${card.id}/activity/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setActivity(response.data)
    } catch (error) {
      console.error(
        'Failed to load card activity:',
        error
      )

      if (
        error.response?.status === 401 ||
        error.response?.status === 403
      ) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/admin-login')
        return
      }

      setCardError(
        'Failed to load card activity.'
      )
    } finally {
      setActivityLoading(false)
    }
  }

  const closeActivity = () => {
    setSelectedCard(null)
    setActivity([])
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Navbar */}
      <nav className="bg-slate-900 border-b border-slate-800 px-6 py-4">

        <div className="max-w-7xl mx-auto flex items-center justify-between">

          <div>
            <h1 className="text-xl font-bold">
              Admin Dashboard
            </h1>

            <p className="text-xs text-slate-400 mt-1">
              Credit Card Management
            </p>
          </div>

          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg font-semibold transition"
          >
            Logout
          </button>

        </div>

      </nav>

      <main className="p-6 max-w-7xl mx-auto">

        {/* Payment Summary */}
        <section>

          <h2 className="text-3xl font-bold mb-2">
            Payment Summary
          </h2>

          <p className="text-slate-400 mb-8">
            Monitor payment activity and card management
          </p>

          {loading && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <p className="text-slate-400">
                Loading payment summary...
              </p>
            </div>
          )}

          {error && (
            <div className="bg-slate-900 border border-red-900 rounded-2xl p-6 mb-6">
              <p className="text-red-400">
                {error}
              </p>
            </div>
          )}

          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

              {/* Total Payments */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg hover:bg-slate-800 hover:-translate-y-1 hover:shadow-xl transition-all duration-300">

                <h3 className="text-slate-400">
                  Total Payments
                </h3>

                <p className="text-3xl font-bold mt-2">
                  {summary.total_payments}
                </p>

              </div>

              {/* Successful */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg hover:bg-slate-800 hover:-translate-y-1 hover:shadow-xl transition-all duration-300">

                <h3 className="text-slate-400">
                  Successful
                </h3>

                <p className="text-3xl font-bold text-green-400 mt-2">
                  {summary.successful_payments}
                </p>

              </div>

              {/* Failed */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg hover:bg-slate-800 hover:-translate-y-1 hover:shadow-xl transition-all duration-300">

                <h3 className="text-slate-400">
                  Failed
                </h3>

                <p className="text-3xl font-bold text-red-400 mt-2">
                  {summary.failed_payments}
                </p>

              </div>

              {/* Total Amount */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg hover:bg-slate-800 hover:-translate-y-1 hover:shadow-xl transition-all duration-300">

                <h3 className="text-slate-400">
                  Total Amount
                </h3>

                <p className="text-3xl font-bold mt-2">
                  ₹
                  {Number(
                    summary.total_amount
                  ).toLocaleString('en-IN')}
                </p>

              </div>

            </div>
          )}

        </section>


        {/* Card Management */}
        <section className="mt-12">

          <div className="flex items-center justify-between mb-6">

            <div>
              <h2 className="text-2xl font-bold">
                Card Management
              </h2>

              <p className="text-slate-400 mt-1">
                View and manage all customer cards
              </p>
            </div>

          </div>

          {cardError && (
            <div className="bg-red-950 border border-red-800 rounded-xl p-4 mb-6">
              <p className="text-red-300">
                {cardError}
              </p>
            </div>
          )}

          {cardsLoading ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <p className="text-slate-400">
                Loading cards...
              </p>
            </div>
          ) : cards.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <p className="text-slate-400">
                No cards found.
              </p>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">

              <div className="overflow-x-auto">

                <table className="w-full">

                  <thead className="bg-slate-800">

                    <tr>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        User
                      </th>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        Card
                      </th>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        Type
                      </th>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        Credit Limit
                      </th>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        Status
                      </th>

                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-300">
                        Actions
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {cards.map((card) => (

                      <tr
                        key={card.id}
                        className="border-t border-slate-800 hover:bg-slate-800/50 transition"
                      >

                        {/* User */}
                        <td className="px-6 py-5">

                          <p className="font-semibold">
                            {card.username}
                          </p>

                          <p className="text-sm text-slate-400">
                            {card.email}
                          </p>

                        </td>


                        {/* Card */}
                        <td className="px-6 py-5">

                          <p className="font-mono text-sm">
                            {card.masked_card_number}
                          </p>

                          <p className="text-xs text-slate-500 mt-1">
                            **** {card.last_four_digits}
                          </p>

                        </td>


                        {/* Card Type */}
                        <td className="px-6 py-5">

                          <span className="px-3 py-1 rounded-full bg-blue-950 text-blue-300 text-xs font-semibold">
                            {card.card_type}
                          </span>

                        </td>


                        {/* Credit Limit */}
                        <td className="px-6 py-5">

                          <p className="font-semibold mb-2">
                            ₹
                            {Number(
                              card.credit_limit
                            ).toLocaleString('en-IN')}
                          </p>

                          <div className="flex gap-2">

                            <input
                              type="number"
                              min="1"
                              placeholder="New limit"
                              value={creditLimits[card.id] || ''}
                              onChange={(event) => {
                              setCreditLimits((currentLimits) => ({
                              ...currentLimits,
                              [card.id]: event.target.value,
                             }))
                            }}
                              className="w-28 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
                            />

                            <button
                              onClick={() =>
                                handleCreditLimitUpdate(card)
                              }
                              disabled={
                                updatingCardId === card.id
                              }
                              className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed px-3 py-2 rounded-lg text-xs font-semibold transition"
                            >
                              {updatingCardId === card.id
                                ? 'Saving...'
                                : 'Update'}
                            </button>

                          </div>

                        </td>


                        {/* Status */}
                        <td className="px-6 py-5">

                          {card.is_blocked ? (
                            <span className="px-3 py-1 rounded-full bg-red-950 text-red-400 text-xs font-semibold">
                              Blocked
                            </span>
                          ) : (
                            <span className="px-3 py-1 rounded-full bg-green-950 text-green-400 text-xs font-semibold">
                              Active
                            </span>
                          )}

                        </td>


                        {/* Actions */}
                        <td className="px-6 py-5">

                          <div className="flex flex-col gap-2">

                            <button
                              onClick={() =>
                                handleBlockToggle(card)
                              }
                              disabled={
                                blockingCardId === card.id
                              }
                              className={
                                card.is_blocked
                                  ? 'bg-green-600 hover:bg-green-500 disabled:bg-slate-700 disabled:cursor-not-allowed px-4 py-2 rounded-lg text-xs font-semibold transition'
                                  : 'bg-red-600 hover:bg-red-500 disabled:bg-slate-700 disabled:cursor-not-allowed px-4 py-2 rounded-lg text-xs font-semibold transition'
                              }
                            >
                              {blockingCardId === card.id
                                ? 'Updating...'
                                : card.is_blocked
                                  ? 'Unblock'
                                  : 'Block'}
                            </button>


                            <button
                              onClick={() =>
                                handleViewActivity(card)
                              }
                              className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-xs font-semibold transition"
                            >
                              View Activity
                            </button>

                          </div>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>
          )}

        </section>

      </main>


      {/* Activity Modal */}
      {selectedCard && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">

          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[85vh] overflow-hidden">

            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-slate-800">

              <div>

                <h2 className="text-xl font-bold">
                  Card Activity
                </h2>

                <p className="text-sm text-slate-400 mt-1">
                  {selectedCard.username} —{' '}
                  {selectedCard.masked_card_number}
                </p>

              </div>

              <button
                onClick={closeActivity}
                className="text-slate-400 hover:text-white text-2xl transition"
              >
                ×
              </button>

            </div>


            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[65vh]">

              {activityLoading ? (
                <div className="py-10 text-center">
                  <p className="text-slate-400">
                    Loading card activity...
                  </p>
                </div>
              ) : activity.length === 0 ? (
                <div className="py-10 text-center">
                  <p className="text-slate-400">
                    No transaction activity found for this card.
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">

                  <table className="w-full">

                    <thead className="bg-slate-800">

                      <tr>

                        <th className="text-left px-4 py-3 text-xs font-semibold text-slate-300">
                          Transaction ID
                        </th>

                        <th className="text-left px-4 py-3 text-xs font-semibold text-slate-300">
                          Amount
                        </th>

                        <th className="text-left px-4 py-3 text-xs font-semibold text-slate-300">
                          Status
                        </th>

                        <th className="text-left px-4 py-3 text-xs font-semibold text-slate-300">
                          Date
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {activity.map((transaction) => (

                        <tr
                          key={transaction.id}
                          className="border-t border-slate-800"
                        >

                          <td className="px-4 py-4">

                            <p className="font-mono text-sm">
                              {transaction.transaction_id}
                            </p>

                          </td>

                          <td className="px-4 py-4 font-semibold">

                            ₹
                            {Number(
                              transaction.amount
                            ).toLocaleString('en-IN')}

                          </td>

                          <td className="px-4 py-4">

                            {transaction.status ===
                            'SUCCESS' ? (
                              <span className="px-3 py-1 rounded-full bg-green-950 text-green-400 text-xs font-semibold">
                                SUCCESS
                              </span>
                            ) : transaction.status ===
                              'FAILED' ? (
                              <span className="px-3 py-1 rounded-full bg-red-950 text-red-400 text-xs font-semibold">
                                FAILED
                              </span>
                            ) : (
                              <span className="px-3 py-1 rounded-full bg-yellow-950 text-yellow-400 text-xs font-semibold">
                                {transaction.status}
                              </span>
                            )}

                          </td>

                          <td className="px-4 py-4 text-sm text-slate-400">

                            {new Date(
                              transaction.created_at
                            ).toLocaleString('en-IN')}

                          </td>

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>
              )}

            </div>


            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-800 flex justify-end">

              <button
                onClick={closeActivity}
                className="bg-slate-700 hover:bg-slate-600 px-5 py-2 rounded-lg font-semibold transition"
              >
                Close
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  )
}

export default AdminDashboard