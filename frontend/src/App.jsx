import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import Videos from './pages/Videos'
import Settings from './pages/Settings'
import TikTok from './pages/TikTok'

function App() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/generate', label: 'Generate', icon: '🎬' },
    { path: '/videos', label: 'Videos', icon: '📹' },
    { path: '/tiktok', label: 'TikTok', icon: '📱' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ]

  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-emerald-800 text-white z-40 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 mr-2 hover:bg-emerald-700 rounded"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-bold">🕌 Quran Video</h1>
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 w-64 bg-emerald-800 text-white z-50
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">🕌 Quran Video</h1>
              <p className="text-emerald-200 text-sm">Generator</p>
            </div>
            <button 
              onClick={closeSidebar}
              className="lg:hidden p-1 hover:bg-emerald-700 rounded"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <nav className="mt-6">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              onClick={closeSidebar}
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
      <div className="lg:ml-64 pt-16 lg:pt-0 p-4 lg:p-8">
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
