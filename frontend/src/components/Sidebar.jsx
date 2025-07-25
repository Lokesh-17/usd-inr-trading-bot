import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  BarChart3, 
  TrendingUp, 
  Wallet, 
  MessageCircle,
  Home
} from 'lucide-react'

const Sidebar = () => {
  const navItems = [
    {
      name: 'Dashboard',
      path: '/',
      icon: Home,
    },
    {
      name: 'Trading',
      path: '/trading',
      icon: TrendingUp,
    },
    {
      name: 'Portfolio',
      path: '/portfolio',
      icon: Wallet,
    },
    {
      name: 'Chat',
      path: '/chat',
      icon: MessageCircle,
    },
  ]

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <BarChart3 className="text-primary-600" size={24} />
          <span className="text-lg font-bold text-gray-900">TradingBot</span>
        </div>
      </div>
      
      <nav className="mt-8">
        <div className="px-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <item.icon size={20} />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}

export default Sidebar