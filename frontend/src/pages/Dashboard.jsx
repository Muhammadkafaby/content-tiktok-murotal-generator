import { useState, useEffect } from 'react'
import { statsApi, videosApi } from '../api'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [recentVideos, setRecentVideos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, videosRes] = await Promise.all([
        statsApi.get(),
        videosApi.list(1, 5)
      ])
      setStats(statsRes.data)
      setRecentVideos(videosRes.data.videos)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-10">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-xl lg:text-2xl font-bold mb-4 lg:mb-6">Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6 mb-6 lg:mb-8">
        <div className="bg-white rounded-lg shadow p-4 lg:p-6">
          <div className="text-2xl lg:text-3xl font-bold text-emerald-600">{stats?.total_videos || 0}</div>
          <div className="text-gray-500 text-sm lg:text-base">Total Videos</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 lg:p-6">
          <div className="text-2xl lg:text-3xl font-bold text-blue-600">{stats?.completed_videos || 0}</div>
          <div className="text-gray-500 text-sm lg:text-base">Completed</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 lg:p-6">
          <div className="text-2xl lg:text-3xl font-bold text-purple-600">{stats?.total_posted || 0}</div>
          <div className="text-gray-500 text-sm lg:text-base">Posted to TikTok</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 lg:p-6">
          <div className="text-2xl lg:text-3xl font-bold text-orange-600">{stats?.storage?.videos_size_mb || 0} MB</div>
          <div className="text-gray-500 text-sm lg:text-base">Storage Used</div>
        </div>
      </div>

      {/* Storage Warning */}
      {stats?.low_storage_warning && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          ⚠️ Low storage warning! Less than 1GB remaining.
        </div>
      )}

      {/* Recent Videos */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Recent Videos</h2>
        </div>
        <div className="p-4">
          {recentVideos.length === 0 ? (
            <p className="text-gray-500">No videos yet. Start generating!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[500px]">
                <thead>
                  <tr className="text-left text-gray-500 text-sm">
                    <th className="pb-2">Surah</th>
                    <th className="pb-2">Ayat</th>
                    <th className="pb-2 hidden sm:table-cell">Qari</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2 hidden sm:table-cell">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {recentVideos.map(video => (
                    <tr key={video.id} className="border-t">
                      <td className="py-2 text-sm lg:text-base">{video.surah_name}</td>
                      <td className="py-2 text-sm lg:text-base">{video.ayat}</td>
                      <td className="py-2 capitalize hidden sm:table-cell text-sm lg:text-base">{video.qari}</td>
                      <td className="py-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          video.status === 'completed' ? 'bg-green-100 text-green-800' :
                          video.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {video.status}
                        </span>
                      </td>
                      <td className="py-2 text-sm text-gray-500 hidden sm:table-cell">
                        {new Date(video.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
