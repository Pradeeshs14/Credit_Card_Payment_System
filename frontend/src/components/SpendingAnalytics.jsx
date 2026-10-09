import { useEffect, useState } from 'react'
import {
ResponsiveContainer,
LineChart,
Line,
XAxis,
YAxis,
CartesianGrid,
Tooltip,
PieChart,
Pie,
Cell,
BarChart,
Bar,
} from 'recharts'
import api from '../services/api'

const CHART_COLORS = [
'#3b82f6',
'#8b5cf6',
'#10b981',
'#f59e0b',
'#ef4444',
'#06b6d4',
'#ec4899',
]

function SpendingAnalytics() {
const [monthly, setMonthly] = useState([])
const [categories, setCategories] = useState([])
const [utilization, setUtilization] = useState([])
const [startDate, setStartDate] = useState('')
const [endDate, setEndDate] = useState('')
const [loading, setLoading] = useState(true)
const [error, setError] = useState('')
const [exporting, setExporting] = useState('')

const formatCurrency = (value) =>
`₹${Number(value || 0).toLocaleString('en-IN', {
      maximumFractionDigits: 2,
    })}`

const loadAnalytics = async () => {
setLoading(true)
setError('')


try {
  const token = localStorage.getItem('access_token')

  if (!token) {
    setError('Your session has expired. Please log in again.')
    return
  }

  const config = {
    headers: { Authorization: `Bearer ${token}` },
    params: {
      ...(startDate ? { start_date: startDate } : {}),
      ...(endDate ? { end_date: endDate } : {}),
    },
  }

  const [monthlyResponse, categoryResponse, utilizationResponse] =
    await Promise.all([
      api.get('/transactions/analytics/monthly-spending/', config),
      api.get('/transactions/analytics/category-spending/', config),
      api.get('/transactions/analytics/credit-utilization/', config),
    ])

  setMonthly(Array.isArray(monthlyResponse.data) ? monthlyResponse.data : [])
  setCategories(
    Array.isArray(categoryResponse.data) ? categoryResponse.data : []
  )
  setUtilization(
    Array.isArray(utilizationResponse.data) ? utilizationResponse.data : []
  )
} catch (err) {
  console.error('Failed to load analytics:', err)
  setError(
    err.response?.status === 401
      ? 'Your session has expired. Please log in again.'
      : 'Unable to load analytics. Please try again.'
  )
} finally {
  setLoading(false)
}


}

useEffect(() => {
loadAnalytics()
// Initial load only; filters are applied by the Apply Filters button.
// eslint-disable-next-line react-hooks/exhaustive-deps
}, [])

const handleExport = async (format) => {
setExporting(format)
setError('')


try {
  const token = localStorage.getItem('access_token')
  const response = await api.get(
    `/transactions/analytics/export-${format}/`,
    {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        ...(startDate ? { start_date: startDate } : {}),
        ...(endDate ? { end_date: endDate } : {}),
      },
      responseType: 'blob',
    }
  )

  const blob = new Blob([response.data], {
    type: format === 'pdf' ? 'application/pdf' : 'text/csv',
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `spending_analytics.${format}`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
} catch (err) {
  console.error(`Failed to export ${format}:`, err)
  setError(`Unable to download the ${format.toUpperCase()} report.`)
} finally {
  setExporting('')
}


}

const cardClass =
'rounded-2xl border border-gray-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900'
const buttonClass =
'rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50'

return ( <section className="mt-10 space-y-6"> <div> <h2 className="text-2xl font-bold">Spending Analytics</h2> <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
Explore your successful transactions and credit utilization. </p> </div>


  <div className={`${cardClass} flex flex-wrap items-end gap-4`}>
    <div>
      <label
        htmlFor="analytics-start-date"
        className="mb-1 block text-sm text-slate-500"
      >
        Start date
      </label>
      <input
        id="analytics-start-date"
        type="date"
        value={startDate}
        max={endDate || undefined}
        onChange={(event) => setStartDate(event.target.value)}
        className="rounded-lg border border-gray-300 bg-transparent p-2 dark:border-slate-700"
      />
    </div>

    <div>
      <label
        htmlFor="analytics-end-date"
        className="mb-1 block text-sm text-slate-500"
      >
        End date
      </label>
      <input
        id="analytics-end-date"
        type="date"
        value={endDate}
        min={startDate || undefined}
        onChange={(event) => setEndDate(event.target.value)}
        className="rounded-lg border border-gray-300 bg-transparent p-2 dark:border-slate-700"
      />
    </div>

    <button
      type="button"
      onClick={loadAnalytics}
      disabled={loading}
      className={buttonClass}
    >
      {loading ? 'Loading...' : 'Apply Filters'}
    </button>

    <button
      type="button"
      onClick={() => {
        setStartDate('')
        setEndDate('')
        setTimeout(() => loadAnalytics(), 0)
      }}
      disabled={loading}
      className="rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-slate-700"
    >
      Clear Dates
    </button>

    <button
      type="button"
      onClick={() => handleExport('csv')}
      disabled={Boolean(exporting)}
      className={buttonClass}
    >
      {exporting === 'csv' ? 'Exporting...' : 'Export CSV'}
    </button>

    <button
      type="button"
      onClick={() => handleExport('pdf')}
      disabled={Boolean(exporting)}
      className={buttonClass}
    >
      {exporting === 'pdf' ? 'Exporting...' : 'Export PDF'}
    </button>
  </div>

  {error && (
    <div
      role="alert"
      className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-500"
    >
      {error}
    </div>
  )}

  {loading ? (
    <div className={cardClass}>Loading analytics...</div>
  ) : (
    <>
      <div className={cardClass}>
        <h3 className="mb-4 text-lg font-semibold">Monthly Spending</h3>
        {monthly.length === 0 ? (
          <p className="text-sm text-slate-500">
            No monthly spending data available.
          </p>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `₹${value}`} />
                <Tooltip
                  formatter={(value, name) => [
                    name === 'total_spending'
                      ? formatCurrency(value)
                      : value,
                    name === 'total_spending'
                      ? 'Total Spending'
                      : 'Transactions',
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="total_spending"
                  name="total_spending"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className={cardClass}>
          <h3 className="mb-4 text-lg font-semibold">
            Category-wise Spending
          </h3>
          {categories.length === 0 ? (
            <p className="text-sm text-slate-500">
              No category spending data available.
            </p>
          ) : (
            <>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories}
                      dataKey="total_spending"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label={({ category, percent }) =>
                        `${category || 'Other'} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {categories.map((item, index) => (
                        <Cell
                          key={`${item.category}-${index}`}
                          fill={CHART_COLORS[index % CHART_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => formatCurrency(value)}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-2">
                {categories.map((item, index) => (
                  <div
                    key={`${item.category}-${index}`}
                    className="flex items-center justify-between gap-3 text-sm"
                  >
                    <span className="flex items-center gap-2">
                      <span
                        className="h-3 w-3 rounded-full"
                        style={{
                          backgroundColor:
                            CHART_COLORS[index % CHART_COLORS.length],
                        }}
                      />
                      {item.category || 'Other'}
                    </span>
                    <span className="font-semibold">
                      {formatCurrency(item.total_spending)}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className={cardClass}>
          <h3 className="mb-4 text-lg font-semibold">
            Credit Utilization
          </h3>
          {utilization.length === 0 ? (
            <p className="text-sm text-slate-500">
              No cards with a valid credit limit were found.
            </p>
          ) : (
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={utilization} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    domain={[0, 100]}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="masked_card_number"
                    width={110}
                  />
                  <Tooltip
                    formatter={(value) => [`${value}%`, 'Utilization']}
                  />
                  <Bar
                    dataKey="utilization_percentage"
                    name="Utilization"
                    fill="#8b5cf6"
                    radius={[0, 6, 6, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </>
  )}
</section>


)
}

export default SpendingAnalytics
