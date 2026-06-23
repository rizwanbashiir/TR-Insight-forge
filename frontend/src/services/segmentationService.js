import api from './api'

export const segmentationService = {
  runSegmentation: (datasetId, params) => 
    api.post('/segmentation', { datasetId, ...params }),

  getSegmentationHistory: () => api.get('/segmentation/history'),
}
