import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="p-10">Loading...</div>
  return user?.isAdmin ? children : <Navigate to="/dashboard" replace />
}