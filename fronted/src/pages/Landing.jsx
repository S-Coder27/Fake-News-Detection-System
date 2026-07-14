import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-16 text-center">
      <h1 className="text-5xl font-black">Fake News Detection System</h1>
      <p className="mt-4 text-slate-300 max-w-2xl mx-auto">
        Detect misleading news with machine learning, history tracking, analytics, and admin controls.
      </p>
      <div className="mt-8 flex justify-center gap-4">
        <Link to="/register" className="px-5 py-3 rounded bg-blue-600">
          Get Started
        </Link>
        <Link to="/detect" className="px-5 py-3 rounded border border-white/20">
          Try Detection
        </Link>
      </div>
    </div>
  )
}