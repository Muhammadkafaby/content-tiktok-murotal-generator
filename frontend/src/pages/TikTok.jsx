import { useState, useEffect } from 'react'
import { tiktokApi } from '../api'

function TikTok() {
  const [status, setStatus] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

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
    try {
      const res = await tiktokApi.login()
      alert(res.data.message || 'Please complete login in browser')
      loadData()
    } catch (err) {
      alert('Failed to initiate login')
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
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
              <span className="text-2xl">✓</span>
            </div>
            <div>
              <div className="font-semibold text-emerald-600">Connected</div>
              <div className="text-gray-500">@{status.username}</div>
            </div>
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
                  <th className="pb-2">Link</th>
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
                      {new Date(post.posted_at).toLocaleString()}
                    </td>
                    <td className="py-2">
                      {post.tiktok_url && (
                        <a
                          href={post.tiktok_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          View
                        </a>
                      )}
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
