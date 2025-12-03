import { useState, useEffect } from 'react'
import { videosApi, tiktokApi } from '../api'

function Videos() {
  const [videos, setVideos] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const limit = 10

  useEffect(() => {
    loadVideos()
  }, [page])

  const loadVideos = async () => {
    setLoading(true)
    try {
      const res = await videosApi.list(page, limit)
      setVideos(res.data.videos)
      setTotal(res.data.total)
    } catch (err) {
      console.error('Failed to load videos:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this video?')) return
    try {
      await videosApi.delete(id)
      loadVideos()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const handlePostToTikTok = async (video) => {
    if (!confirm(`Post "${video.surah_name} - Ayat ${video.ayat}" to TikTok?`)) return
    
    try {
      const res = await tiktokApi.post(video.id)
      alert(res.data.message || 'Posted to TikTok!')
      loadVideos()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to post to TikTok')
    }
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Videos ({total})</h1>

      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : videos.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-10 text-center text-gray-500">
          No videos yet. Go to Generate to create some!
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map(video => (
              <div key={video.id} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="bg-emerald-100 h-40 flex items-center justify-center">
                  <span className="text-4xl">🕌</span>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold">{video.surah_name}</h3>
                  <p className="text-gray-500 text-sm">Ayat {video.ayat}</p>
                  <p className="text-gray-400 text-xs mt-1">
                    {video.duration?.toFixed(1)}s • {(video.file_size / 1024 / 1024).toFixed(1)} MB
                  </p>
                  
                  <div className="flex flex-col gap-2 mt-4">
                    <div className="flex gap-2">
                      <a
                        href={videosApi.download(video.id)}
                        className="flex-1 bg-emerald-600 text-white text-center py-2 rounded text-sm hover:bg-emerald-700"
                      >
                        Download
                      </a>
                      <button
                        onClick={() => handleDelete(video.id)}
                        className="px-4 py-2 bg-red-100 text-red-600 rounded text-sm hover:bg-red-200"
                      >
                        🗑️
                      </button>
                    </div>
                    <button
                      onClick={() => handlePostToTikTok(video)}
                      disabled={video.tiktok_posted}
                      className={`w-full py-2 rounded text-sm ${
                        video.tiktok_posted 
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                          : 'bg-black text-white hover:bg-gray-800'
                      }`}
                    >
                      {video.tiktok_posted ? '✓ Posted to TikTok' : '🎵 Post to TikTok'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Videos
