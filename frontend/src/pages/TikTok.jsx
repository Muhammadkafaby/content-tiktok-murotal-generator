import { useState, useEffect } from 'react'
import { tiktokApi } from '../api'

function TikTok() {
  const [status, setStatus] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCookieModal, setShowCookieModal] = useState(false)
  const [cookiesJson, setCookiesJson] = useState('')
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statusRes, historyRes] = await Promise.all([
        tiktokApi.status(),
        tiktokApi.history()
      ])
      setStatus(statusRes.data)
      setHistory(historyRes.data.history || [])
    } catch (err) {
      console.error('Failed to load TikTok data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    setShowCookieModal(true)
  }

  const handleUploadCookies = async () => {
    if (!cookiesJson.trim()) {
      alert('Please paste your cookies JSON')
      return
    }

    setUploading(true)
    try {
      const res = await tiktokApi.uploadCookies(cookiesJson)
      if (res.data.logged_in) {
        alert('Login successful!')
        setShowCookieModal(false)
        setCookiesJson('')
        loadData()
      } else {
        alert(res.data.message || 'Login failed. Please check your cookies.')
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to upload cookies')
    } finally {
      setUploading(false)
    }
  }

  const handleLogout = async () => {
    if (!confirm('Are you sure you want to logout from TikTok?')) return
    
    try {
      await tiktokApi.logout()
      alert('Logged out successfully')
      loadData()
    } catch (err) {
      alert('Failed to logout')
    }
  }

  if (loading) {
    return <div className="text-center py-10">Loading...</div>
  }


  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">TikTok Integration</h1>

      {/* Login Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Account Status</h2>
        
        {status?.logged_in ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">✓</span>
              </div>
              <div>
                <div className="font-semibold text-emerald-600">Connected</div>
                <div className="text-gray-500">@{status.username || 'TikTok User'}</div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="text-red-600 hover:text-red-800 text-sm"
            >
              Logout
            </button>
          </div>
        ) : (
          <div>
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">❌</span>
              </div>
              <div>
                <div className="font-semibold text-gray-600">Not Connected</div>
                <div className="text-gray-500">Login to enable auto-posting</div>
              </div>
            </div>
            <button
              onClick={handleLogin}
              className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
            >
              🎵 Login to TikTok
            </button>
          </div>
        )}
      </div>

      {/* Cookie Upload Modal */}
      {showCookieModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Login to TikTok</h3>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">To login, follow these steps:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Install "EditThisCookie" or "Cookie-Editor" browser extension</li>
                <li>Login to TikTok in your browser</li>
                <li>Export cookies as JSON from the extension</li>
                <li>Paste the JSON below</li>
              </ol>
            </div>

            <textarea
              value={cookiesJson}
              onChange={(e) => setCookiesJson(e.target.value)}
              placeholder='Paste cookies JSON here...'
              className="w-full h-40 border rounded p-2 text-sm font-mono"
            />

            <div className="flex gap-2 mt-4">
              <button
                onClick={handleUploadCookies}
                disabled={uploading}
                className="flex-1 bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700 disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Upload Cookies'}
              </button>
              <button
                onClick={() => setShowCookieModal(false)}
                className="px-4 py-2 border rounded hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}


      {/* Posting History */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Posting History</h2>
        </div>
        <div className="p-4">
          {history.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No posts yet</p>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-500 text-sm">
                  <th className="pb-2">Video</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Posted</th>
                </tr>
              </thead>
              <tbody>
                {history.map(post => (
                  <tr key={post.id} className="border-t">
                    <td className="py-2">{post.video_id?.slice(0, 8)}...</td>
                    <td className="py-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        post.status === 'success' ? 'bg-green-100 text-green-800' :
                        post.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {post.status}
                      </span>
                    </td>
                    <td className="py-2 text-sm text-gray-500">
                      {post.posted_at ? new Date(post.posted_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default TikTok
