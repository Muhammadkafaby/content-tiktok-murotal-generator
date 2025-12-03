import { useState, useEffect } from 'react'
import { settingsApi } from '../api'

function Settings() {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const qariOptions = [
    { value: 'alafasy', label: 'Mishary Rashid Alafasy' },
    { value: 'abdulbasit', label: 'Abdul Basit Abdul Samad' },
    { value: 'sudais', label: 'Abdurrahman As-Sudais' },
    { value: 'husary', label: 'Mahmoud Khalil Al-Husary' },
    { value: 'minshawi', label: 'Mohamed Siddiq El-Minshawi' },
  ]

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const res = await settingsApi.get()
      setSettings(res.data)
    } catch (err) {
      console.error('Failed to load settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await settingsApi.update(settings)
      alert('Settings saved!')
    } catch (err) {
      alert('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  if (loading) {
    return <div className="text-center py-10">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="space-y-6">
        {/* Qari Selection */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">🎙️ Qari Selection</h2>
          <select
            value={settings.qari}
            onChange={(e) => updateSetting('qari', e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            {qariOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Schedule Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">⏰ Auto-Generate Schedule</h2>
          
          <div className="flex items-center gap-4 mb-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.schedule_enabled}
                onChange={(e) => updateSetting('schedule_enabled', e.target.checked)}
                className="w-5 h-5"
              />
              Enable scheduled generation
            </label>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-600 mb-1">Time (daily)</label>
              <input
                type="time"
                value={settings.schedule_time}
                onChange={(e) => updateSetting('schedule_time', e.target.value)}
                className="border rounded px-3 py-2 w-full"
              />
            </div>
            <div>
              <label className="block text-gray-600 mb-1">Videos per day</label>
              <input
                type="number"
                min="1"
                max="50"
                value={settings.videos_per_day}
                onChange={(e) => updateSetting('videos_per_day', parseInt(e.target.value))}
                className="border rounded px-3 py-2 w-full"
              />
            </div>
          </div>
        </div>

        {/* Caption Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">✍️ Caption Settings</h2>
          
          <div className="mb-4">
            <label className="block text-gray-600 mb-1">Caption Mode</label>
            <select
              value={settings.caption_mode}
              onChange={(e) => updateSetting('caption_mode', e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="template">Template (Simple)</option>
              <option value="ai">AI Generated (OpenAI)</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-600 mb-1">Hashtags</label>
            <input
              type="text"
              value={settings.tiktok_hashtags}
              onChange={(e) => updateSetting('tiktok_hashtags', e.target.value)}
              className="w-full border rounded px-3 py-2"
              placeholder="#quran #murotal #islamic"
            />
          </div>
        </div>

        {/* TikTok Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">📱 TikTok Auto-Post</h2>
          
          <div className="flex items-center gap-4 mb-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.tiktok_auto_post}
                onChange={(e) => updateSetting('tiktok_auto_post', e.target.checked)}
                className="w-5 h-5"
              />
              Auto-post to TikTok after generation
            </label>
          </div>

          <div>
            <label className="block text-gray-600 mb-1">Delay between posts (minutes)</label>
            <input
              type="number"
              min="1"
              value={settings.tiktok_post_delay}
              onChange={(e) => updateSetting('tiktok_post_delay', parseInt(e.target.value))}
              className="border rounded px-3 py-2 w-32"
            />
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : '💾 Save Settings'}
        </button>
      </div>
    </div>
  )
}

export default Settings
