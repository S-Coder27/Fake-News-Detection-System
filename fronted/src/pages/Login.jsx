import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [err, setErr] = useState('')
  const nav = useNavigate()
  const { login } = useAuth()

  const submit = async (e) => {
    e.preventDefault()
    try {
      await login(form.email, form.password)
      nav('/dashboard')
    } catch (error) {
      setErr(error.response?.data?.message || 'Login failed')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto mt-16 glass rounded-2xl p-6">
      <h2 className="text-2xl font-bold">Login</h2>
      {err && <p className="text-red-400 mt-2">{err}</p>}
      <input
        className="mt-4 w-full p-3 rounded bg-slate-900"
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />
      <input
        type="password"
        className="mt-3 w-full p-3 rounded bg-slate-900"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />
      <button className="mt-5 w-full p-3 rounded bg-blue-600">Login</button>
      <p className="mt-3 text-sm">
        <Link to="/register">Create account</Link>
      </p>
    </form>
  )
}