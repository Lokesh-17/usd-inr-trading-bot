import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { portfolioAPI, forexAPI, tradingAPI } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, IndianRupee, Activity } from 'lucide-react'

const Dashboard = () => {
  const { user } = useUser()
  const [portfolio, setPortfolio] = useState(null)
  const [exchangeRate, setExchangeRate] = useState(null)
  const [recentTrades, setRecentTrades] = useState([])
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [portfolioRes, rateRes, tradesRes, chartRes] = await Promise.all([
          portfolioAPI.get(user.id),
          forexAPI.getExchangeRate(),
          tradingAPI.getHistory(user.id),
          forexAPI.getChartData('60min', 'compact')
        ])

        setPortfolio(portfolioRes.data)
        setExchangeRate(rateRes.data)
        setRecentTrades(tradesRes.data.slice(0, 5))
        
        // Format chart data
        const formattedChartData = chartRes.data.data.slice(0, 24).reverse().map(item => ({
          time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          rate: item.close
        }))
        setChartData(formattedChartData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      fetchDashboardData()
    }
  }, [user])

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

  const profitLoss = totalValue - 100000 // Starting amount
  const profitLossPercentage = ((profitLoss / 100000) * 100).toFixed(2)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
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
            <div className="p-2 bg-success-100 rounded-lg">
              <DollarSign className="text-success-600" size={24} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">USD Holdings</p>
              <p className="text-2xl font-bold text-gray-900">
                ${portfolio?.usd_held?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-warning-100 rounded-lg">
              <Activity className="text-warning-600" size={24} />
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
            <div className={`p-2 rounded-lg ${profitLoss >= 0 ? 'bg-success-100' : 'bg-danger-100'}`}>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Exchange Rate Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            USD/INR Rate (Last 24 Hours)
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={['dataMin - 0.1', 'dataMax + 0.1']} />
                <Tooltip 
                  formatter={(value) => [`₹${value.toFixed(2)}`, 'Rate']}
                />
                <Line 
                  type="monotone" 
                  dataKey="rate" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Trades */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Trades
          </h2>
          <div className="space-y-3">
            {recentTrades.length > 0 ? (
              recentTrades.map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      trade.trade_type === 'BUY' ? 'bg-success-100' : 'bg-danger-100'
                    }`}>
                      {trade.trade_type === 'BUY' ? (
                        <TrendingUp className="text-success-600" size={16} />
                      ) : (
                        <TrendingDown className="text-danger-600" size={16} />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {trade.trade_type} ${trade.amount_usd}
                      </p>
                      <p className="text-xs text-gray-500">
                        @ ₹{trade.exchange_rate.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      ₹{trade.amount_inr.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(trade.executed_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity size={48} className="mx-auto mb-4 opacity-50" />
                <p>No trades yet</p>
                <p className="text-sm">Start trading to see your history here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard