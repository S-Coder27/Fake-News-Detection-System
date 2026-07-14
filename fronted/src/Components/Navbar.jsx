import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) =>
    location.pathname === path
      ? 'text-blue-400'
      : 'text-slate-300 hover:text-white';

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-lg bg-slate-900/80 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">

        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-3"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold">
            AI
          </div>

          <div>
            <h1 className="text-lg font-bold text-white">
              Fake News Detector
            </h1>

            <p className="text-xs text-slate-400">
              AI Credibility Analyzer
            </p>
          </div>
        </Link>

        {/* Menu */}
        <div className="flex items-center gap-6">

          <Link
            to="/"
            className={isActive('/')}
          >
            Home
          </Link>

          {user && (
            <>
              <Link
                to="/detect"
                className={isActive('/detect')}
              >
                Detect
              </Link>

              <Link
                to="/history"
                className={isActive('/history')}
              >
                History
              </Link>

              <Link
                to="/dashboard"
                className={isActive('/dashboard')}
              >
                Dashboard
              </Link>
            </>
          )}

          {!user ? (
            <>
              <Link
                to="/login"
                className="text-slate-300 hover:text-white"
              >
                Login
              </Link>

              <Link
                to="/register"
                className="px-5 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition"
              >
                Get Started
              </Link>
            </>
          ) : (
            <>
              <div className="hidden md:flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-xl">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold">
                  {user?.name?.charAt(0).toUpperCase()}
                </div>

                <span className="text-slate-200">
                  {user.name}
                </span>
              </div>

              <button
                onClick={logout}
                className="px-4 py-2 rounded-xl bg-red-600 text-white hover:bg-red-700 transition"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}