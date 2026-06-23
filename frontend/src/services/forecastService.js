import api from './api'

export const forecastService = {
  runForecast: (datasetId, params) => 
    api.post('/forecast', { datasetId, ...params }),

  getForecastHistory: () => api.get('/forecast/history'),

  exportForecast: (forecastId) => 
    api.get(`/forecast/${forecastId}/export`, { responseType: 'blob' }),
}
