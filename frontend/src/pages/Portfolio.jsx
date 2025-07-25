import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { portfolioAPI, tradingAPI, forexAPI } from '../services/api'
import { TrendingUp, TrendingDown, RotateCcw, DollarSign, IndianRupee } from 'lucide-react'

const Portfolio = () => {
  const { user } = useUser()
  const [portfolio, setPortfolio] = useState(null)
  const [trades, setTrades] = useState([])
  const [exchangeRate, setExchangeRate] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [portfolioRes, tradesRes, rateRes] = await Promise.all([
        portfolioAPI.get(user.id),
        tradingAPI.getHistory(user.id),
        forexAPI.getExchangeRate()
      ])

      setPortfolio(portfolioRes.data)
      setTrades(tradesRes.data)
      setExchangeRate(rateRes.data)
    } catch (error) {
      console.error('Error fetching portfolio data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchData()
    }
  }, [user])

  const handleResetPortfolio = async () => {
    if (window.confirm('Are you sure you want to reset your portfolio? This will restore your balance to ₹1,00,000 and clear all USD holdings.')) {
      try {
        await portfolioAPI.reset(user.id)
        fetchData()
        alert('Portfolio reset successfully!')
      } catch (error) {
        alert('Error resetting portfolio: ' + (error.response?.data?.detail || error.message))
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  const totalValue = portfolio && exchangeRate 
    ? portfolio.inr_balance + (portfolio.usd_held * exchangeRate.rate)
    : 0

  const profitLoss = totalValue - 100000
  const profitLossPercentage = ((profitLoss / 100000) * 100).toFixed(2)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
        <button
          onClick={handleResetPortfolio}
          className="flex items-center space-x-2 px-4 py-2 bg-warning-600 text-white rounded-lg hover:bg-warning-700"
        >
          <RotateCcw size={16} />
          <span>Reset Portfolio</span>
        </button>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-full">
              <IndianRupee className="text-primary-600" size={24} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">INR Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                ₹{portfolio?.inr_balance?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-success-100 rounded-full">
              <DollarSign className="text-success-600" size={24} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">USD Holdings</p>
              <p className="text-2xl font-bold text-gray-900">
                ${portfolio?.usd_held?.toFixed(2) || '0.00'}
              </p>
              {exchangeRate && portfolio?.usd_held > 0 && (
                <p className="text-xs text-gray-500">
                  ≈ ₹{(portfolio.usd_held * exchangeRate.rate).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-warning-100 rounded-full">
              <IndianRupee className="text-warning-600" size={24} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ₹{totalValue.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className={`p-3 rounded-full ${profitLoss >= 0 ? 'bg-success-100' : 'bg-danger-100'}`}>
              {profitLoss >= 0 ? (
                <TrendingUp className="text-success-600" size={24} />
              ) : (
                <TrendingDown className="text-danger-600" size={24} />
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">P&L</p>
              <p className={`text-2xl font-bold ${profitLoss >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                {profitLoss >= 0 ? '+' : ''}₹{profitLoss.toLocaleString()}
              </p>
              <p className={`text-xs ${profitLoss >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                {profitLoss >= 0 ? '+' : ''}{profitLossPercentage}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Trade History */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Trade History</h2>
        </div>
        <div className="overflow-x-auto">
          {trades.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount (USD)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value (INR)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Portfolio After
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(trade.executed_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        trade.trade_type === 'BUY' 
                          ? 'bg-success-100 text-success-800' 
                          : 'bg-danger-100 text-danger-800'
                      }`}>
                        {trade.trade_type === 'BUY' ? (
                          <TrendingUp size={12} className="mr-1" />
                        ) : (
                          <TrendingDown size={12} className="mr-1" />
                        )}
                        {trade.trade_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${trade.amount_usd.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{trade.exchange_rate.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{trade.amount_inr.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="text-xs">
                        <div>INR: ₹{trade.inr_balance_after.toLocaleString()}</div>
                        <div>USD: ${trade.usd_held_after.toFixed(2)}</div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12">
              <TrendingUp size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No trades yet</h3>
              <p className="text-gray-500">Start trading to see your transaction history here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Portfolio