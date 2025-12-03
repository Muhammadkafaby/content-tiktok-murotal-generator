import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export const videosApi = {
  list: (page = 1, limit = 10) => api.get(`/videos?page=${page}&limit=${limit}`),
  get: (id) => api.get(`/videos/${id}`),
  delete: (id) => api.delete(`/videos/${id}`),
  download: (id) => `/api/videos/${id}/download`
}

export const generateApi = {
  start: (count = 1) => api.post('/generate', { count }),
  status: () => api.get('/generate/status'),
  cancel: () => api.post('/generate/cancel')
}

export const settingsApi = {
  get: () => api.get('/settings'),
  update: (data) => api.put('/settings', data)
}

export const statsApi = {
  get: () => api.get('/stats')
}

export const tiktokApi = {
  login: () => api.post('/tiktok/login'),
  status: () => api.get('/tiktok/status'),
  post: (videoId) => api.post(`/tiktok/post/${videoId}`),
  history: () => api.get('/tiktok/history')
}

export default api
