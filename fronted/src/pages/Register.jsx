import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [err, setErr] = useState('')
  const nav = useNavigate()
  const { register } = useAuth()

  const submit = async (e) => {
    e.preventDefault()
    try {
      await register(form)
      nav('/dashboard')
    } catch (error) {
      setErr(error.response?.data?.message || 'Register failed')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto mt-16 glass rounded-2xl p-6">
      <h2 className="text-2xl font-bold">Register</h2>
      {err && <p className="text-red-400 mt-2">{err}</p>}
      <input
        className="mt-4 w-full p-3 rounded bg-slate-900"
        placeholder="Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
      />
      <input
        className="mt-3 w-full p-3 rounded bg-slate-900"
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
      <button className="mt-5 w-full p-3 rounded bg-blue-600">Register</button>
      <p className="mt-3 text-sm">
        <Link to="/login">Already have an account?</Link>
      </p>
    </form>
  )
}