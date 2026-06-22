import api from './api'

export const insightsService = {
  generateInsights: (data) => api.post('/insights', data),

  getInsightsHistory: () => api.get('/insights/history'),

  chat: (message, context) => api.post('/insights/chat', { message, context }),
}
