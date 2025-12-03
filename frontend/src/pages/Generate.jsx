import { useState, useEffect } from 'react'
import { generateApi } from '../api'

function Generate() {
  const [count, setCount] = useState(1)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const checkStatus = async () => {
    try {
      const res = await generateApi.status()
      setStatus(res.data)
    } catch (err) {
      console.error('Failed to check status:', err)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      await generateApi.start(count)
      checkStatus()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start generation')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    try {
      await generateApi.cancel()
      checkStatus()
    } catch (err) {
      alert('Failed to cancel')
    }
  }

  const isRunning = status?.status === 'running'
  const job = status?.current_job

  return (
    <div>
      <h1 className="text-xl lg:text-2xl font-bold mb-4 lg:mb-6">Generate Videos</h1>

      {/* Generate Form */}
      <div className="bg-white rounded-lg shadow p-4 lg:p-6 mb-4 lg:mb-6">
        <h2 className="text-base lg:text-lg font-semibold mb-4">New Generation</h2>
        
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-4">
          <label className="text-gray-600 text-sm lg:text-base">Number of videos:</label>
          <input
            type="number"
            min="1"
            max="50"
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value) || 1)}
            className="border rounded px-3 py-2 w-full sm:w-24"
            disabled={isRunning}
          />
        </div>

        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
          <button
            onClick={handleGenerate}
            disabled={loading || isRunning}
            className="bg-emerald-600 text-white px-6 py-3 sm:py-2 rounded hover:bg-emerald-700 disabled:opacity-50 w-full sm:w-auto"
          >
            {loading ? 'Starting...' : '🎬 Generate'}
          </button>
          
          {isRunning && (
            <button
              onClick={handleCancel}
              className="bg-red-600 text-white px-6 py-3 sm:py-2 rounded hover:bg-red-700 w-full sm:w-auto"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Current Job Status */}
      {job && (
        <div className="bg-white rounded-lg shadow p-4 lg:p-6">
          <h2 className="text-base lg:text-lg font-semibold mb-4">Current Job</h2>
          
          <div className="mb-4">
            <div className="flex justify-between mb-2 text-sm lg:text-base">
              <span>Progress</span>
              <span>{job.completed} / {job.count} ({job.progress}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 lg:h-4">
              <div
                className="bg-emerald-600 h-3 lg:h-4 rounded-full transition-all"
                style={{ width: `${job.progress}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 lg:gap-4 text-center">
            <div>
              <div className="text-xl lg:text-2xl font-bold text-green-600">{job.completed}</div>
              <div className="text-gray-500 text-xs lg:text-sm">Completed</div>
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold text-red-600">{job.failed}</div>
              <div className="text-gray-500 text-xs lg:text-sm">Failed</div>
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold text-blue-600">{job.count - job.completed - job.failed}</div>
              <div className="text-gray-500 text-xs lg:text-sm">Remaining</div>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            Status: <span className="capitalize font-medium">{job.status}</span>
          </div>
        </div>
      )}

      {!job && status?.status === 'idle' && (
        <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
          No generation in progress. Start a new one above!
        </div>
      )}
    </div>
  )
}

export default Generate
