import api from './api'

export const uploadService = {
  uploadFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  getDatasets: () => api.get('/datasets'),

  deleteDataset: (id) => api.delete(`/datasets/${id}`),

  parseFile: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = e.target.result
          resolve(data)
        } catch (err) {
          reject(err)
        }
      }
      reader.onerror = reject
      reader.readAsText(file)
    })
  },
}
