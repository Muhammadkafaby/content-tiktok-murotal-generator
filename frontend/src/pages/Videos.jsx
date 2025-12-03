import { useState, useEffect } from 'react'
import { videosApi, tiktokApi } from '../api'

function Videos() {
  const [videos, setVideos] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [captionModal, setCaptionModal] = useState(null)
  const [captionLoading, setCaptionLoading] = useState(false)
  const [copied, setCopied] = useState(false)
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
    setCaptionLoading(true)
    try {
      const res = await tiktokApi.getCaption(video.id)
      setCaptionModal({
        video,
        caption: res.data.caption,
        downloadUrl: res.data.download_url
      })
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate caption')
    } finally {
      setCaptionLoading(false)
    }
  }

  const handleCopyCaption = async () => {
    if (captionModal?.caption) {
      await navigator.clipboard.writeText(captionModal.caption)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownloadVideo = () => {
    if (captionModal?.video) {
      window.open(videosApi.download(captionModal.video.id), '_blank')
    }
  }

  const closeModal = () => {
    setCaptionModal(null)
    setCopied(false)
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <h1 className="text-xl lg:text-2xl font-bold mb-4 lg:mb-6">Videos ({total})</h1>

      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : videos.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-10 text-center text-gray-500">
          No videos yet. Go to Generate to create some!
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
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
                      disabled={captionLoading}
                      className="w-full py-2 rounded text-sm bg-black text-white hover:bg-gray-800 disabled:opacity-50"
                    >
                      {captionLoading ? 'Loading...' : '🎵 Post to TikTok'}
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

      {/* Caption Modal */}
      {captionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Post to TikTok</h2>
                <button onClick={closeModal} className="text-gray-500 hover:text-gray-700 text-2xl">
                  ×
                </button>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600 mb-2">
                  <span className="font-semibold">{captionModal.video.surah_name}</span> - Ayat {captionModal.video.ayat}
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Caption (Copy this to TikTok)
                </label>
                <textarea
                  readOnly
                  value={captionModal.caption}
                  className="w-full h-48 p-3 border rounded-lg bg-gray-50 text-sm resize-none"
                />
              </div>

              <div className="flex flex-col gap-3">
                <button
                  onClick={handleCopyCaption}
                  className={`w-full py-3 rounded-lg font-medium transition-colors ${
                    copied 
                      ? 'bg-green-600 text-white' 
                      : 'bg-emerald-600 text-white hover:bg-emerald-700'
                  }`}
                >
                  {copied ? '✓ Copied!' : '📋 Copy Caption'}
                </button>
                
                <button
                  onClick={handleDownloadVideo}
                  className="w-full py-3 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700"
                >
                  ⬇️ Download Video
                </button>

                <a
                  href="https://www.tiktok.com/upload"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-3 rounded-lg font-medium bg-black text-white hover:bg-gray-800 text-center"
                >
                  🎵 Open TikTok Upload
                </a>
              </div>

              <p className="text-xs text-gray-500 mt-4 text-center">
                1. Copy caption → 2. Download video → 3. Upload to TikTok manually
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Videos
