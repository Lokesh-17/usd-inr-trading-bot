import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { tradingAPI, forexAPI, portfolioAPI } from '../services/api'
import { ComposedChart, Candlestick, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, IndianRupee, RefreshCw } from 'lucide-react'

const Trading = () => {
  const { user } = useUser()
  const [portfolio, setPortfolio] = useState(null)
  const [exchangeRate, setExchangeRate] = useState(null)
  const [chartData, setChartData] = useState([])
  const [interval, setInterval] = useState('5min')
  const [tradeAmount, setTradeAmount] = useState(100)
  const [loading, setLoading] = useState(false)
  const [tradeLoading, setTradeLoading] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [portfolioRes, rateRes, chartRes] = await Promise.all([
        portfolioAPI.get(user.id),
        forexAPI.getExchangeRate(),
        forexAPI.getChartData(interval, 'compact')
      ])

      setPortfolio(portfolioRes.data)
      setExchangeRate(rateRes.data)
      
      // Format chart data for candlestick
      const formattedData = chartRes.data.data.slice(0, 50).reverse().map((item, index) => ({
        time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))
      setChartData(formattedData)
    } catch (error) {
      console.error('Error fetching trading data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchData()
    }
  }, [user, interval])

  const executeTrade = async (tradeType) => {
    setTradeLoading(true)
    try {
      await tradingAPI.executeTrade(user.id, {
        trade_type: tradeType,
        amount_usd: tradeAmount
      })
      
      // Refresh portfolio data
      const portfolioRes = await portfolioAPI.get(user.id)
      setPortfolio(portfolioRes.data)
      
      alert(`${tradeType} order executed successfully!`)
    } catch (error) {
      alert(`Error executing trade: ${error.response?.data?.detail || error.message}`)
    } finally {
      setTradeLoading(false)
    }
  }

  const canBuy = portfolio && exchangeRate && (portfolio.inr_balance >= tradeAmount * exchangeRate.rate)
  const canSell = portfolio && (portfolio.usd_held >= tradeAmount)

  if (!portfolio || !exchangeRate) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Trading</h1>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trading Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Current Rate */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Rate</h2>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">
                ₹{exchangeRate.rate.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                USD/INR
              </p>
            </div>
          </div>

          {/* Portfolio Summary */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Portfolio</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <IndianRupee size={16} className="text-primary-600" />
                  <span className="text-sm font-medium">INR Balance</span>
                </div>
                <span className="font-bold">₹{portfolio.inr_balance.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <DollarSign size={16} className="text-success-600" />
                  <span className="text-sm font-medium">USD Holdings</span>
                </div>
                <span className="font-bold">${portfolio.usd_held.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Trading Form */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Execute Trade</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount (USD)
                </label>
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={tradeAmount}
                  onChange={(e) => setTradeAmount(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Cost: ₹{(tradeAmount * exchangeRate.rate).toLocaleString()}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => executeTrade('BUY')}
                  disabled={!canBuy || tradeLoading}
                  className="flex items-center justify-center space-x-2 px-4 py-3 bg-success-600 text-white rounded-lg hover:bg-success-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TrendingUp size={16} />
                  <span>Buy USD</span>
                </button>
                <button
                  onClick={() => executeTrade('SELL')}
                  disabled={!canSell || tradeLoading}
                  className="flex items-center justify-center space-x-2 px-4 py-3 bg-danger-600 text-white rounded-lg hover:bg-danger-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TrendingDown size={16} />
                  <span>Sell USD</span>
                </button>
              </div>

              {!canBuy && (
                <p className="text-xs text-danger-600">
                  Insufficient INR balance for this trade
                </p>
              )}
              {!canSell && (
                <p className="text-xs text-danger-600">
                  Insufficient USD holdings for this trade
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                USD/INR Chart
              </h2>
              <select
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="1min">1 Minute</option>
                <option value="5min">5 Minutes</option>
                <option value="15min">15 Minutes</option>
                <option value="30min">30 Minutes</option>
                <option value="60min">1 Hour</option>
              </select>
            </div>
            
            <div className="h-96">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis domain={['dataMin - 0.5', 'dataMax + 0.5']} />
                    <Tooltip 
                      formatter={(value, name) => {
                        if (name === 'close') return [`₹${value.toFixed(2)}`, 'Close']
                        return [`₹${value.toFixed(2)}`, name]
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="close" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={false}
                      name="close"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Trading