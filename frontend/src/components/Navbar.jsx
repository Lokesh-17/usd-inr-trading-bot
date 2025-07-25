import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { forexAPI } from '../services/api'
import { RefreshCw, LogOut } from 'lucide-react'

const Navbar = () => {
  const { user, logout } = useUser()
  const [exchangeRate, setExchangeRate] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchExchangeRate = async () => {
    setLoading(true)
    try {
      const response = await forexAPI.getExchangeRate()
      setExchangeRate(response.data)
    } catch (error) {
      console.error('Error fetching exchange rate:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExchangeRate()
    // Refresh rate every 5 minutes
    const interval = setInterval(fetchExchangeRate, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">
              USD/INR Trading Bot
            </h1>
            
            {/* Exchange Rate Display */}
            <div className="flex items-center space-x-2 bg-primary-50 px-3 py-1 rounded-lg">
              <span className="text-sm font-medium text-primary-700">
                USD/INR:
              </span>
              {exchangeRate ? (
                <span className="text-sm font-bold text-primary-900">
                  ₹{exchangeRate.rate.toFixed(2)}
                </span>
              ) : (
                <span className="text-sm text-gray-500">Loading...</span>
              )}
              <button
                onClick={fetchExchangeRate}
                disabled={loading}
                className="p-1 hover:bg-primary-100 rounded transition-colors"
              >
                <RefreshCw 
                  size={14} 
                  className={`text-primary-600 ${loading ? 'animate-spin' : ''}`} 
                />
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Welcome, <span className="font-medium">{user?.username}</span>
            </div>
            <button
              onClick={logout}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar