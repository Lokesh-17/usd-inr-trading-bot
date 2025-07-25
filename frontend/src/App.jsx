import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { UserProvider } from './contexts/UserContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Trading from './pages/Trading'
import Portfolio from './pages/Portfolio'
import Chat from './pages/Chat'
import Login from './pages/Login'

function App() {
  return (
    <UserProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="trading" element={<Trading />} />
              <Route path="portfolio" element={<Portfolio />} />
              <Route path="chat" element={<Chat />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </UserProvider>
  )
}

export default App