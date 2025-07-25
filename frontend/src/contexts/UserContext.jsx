import React, { createContext, useContext, useState, useEffect } from 'react'
import { userAPI } from '../services/api'

const UserContext = createContext()

export const useUser = () => {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is stored in localStorage
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        setUser(userData)
      } catch (error) {
        console.error('Error parsing stored user data:', error)
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (userData) => {
    try {
      // In a real app, you'd validate credentials here
      // For demo purposes, we'll create a user if they don't exist
      let response
      try {
        response = await userAPI.get(userData.id || 1)
      } catch (error) {
        if (error.response?.status === 404) {
          // User doesn't exist, create them
          response = await userAPI.create({
            username: userData.username,
            email: userData.email
          })
        } else {
          throw error
        }
      }
      
      const user = response.data
      setUser(user)
      localStorage.setItem('user', JSON.stringify(user))
      return user
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}