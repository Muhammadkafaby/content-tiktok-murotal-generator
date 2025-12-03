import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import Videos from './pages/Videos'
import Settings from './pages/Settings'
import TikTok from './pages/TikTok'

function App() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/generate', label: 'Generate', icon: '🎬' },
    { path: '/videos', label: 'Videos', icon: '📹' },
    { path: '/tiktok', label: 'TikTok', icon: '📱' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ]

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-emerald-800 text-white">
        <div className="p-6">
          <h1 className="text-xl font-bold">🕌 Quran Video</h1>
          <p className="text-emerald-200 text-sm">Generator</p>
        </div>
        <nav className="mt-6">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-6 py-3 hover:bg-emerald-700 ${
                location.pathname === item.path ? 'bg-emerald-700' : ''
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="ml-64 p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/videos" element={<Videos />} />
          <Route path="/tiktok" element={<TikTok />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
