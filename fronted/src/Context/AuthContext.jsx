import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (token && savedUser) setUser(JSON.parse(savedUser))
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', data.data.token)
    localStorage.setItem('user', JSON.stringify(data.data.user))
    setUser(data.data.user)
    return data
  }

  const register = async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    localStorage.setItem('token', data.data.token)
    localStorage.setItem('user', JSON.stringify(data.data.user))
    setUser(data.data.user)
    return data
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}