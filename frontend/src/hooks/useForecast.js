import { useState, useCallback } from 'react'
import { forecastService } from '../services/forecastService'

export const useForecast = () => {
  const [forecastData, setForecastData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const runForecast = useCallback(async (datasetId, params) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await forecastService.runForecast(datasetId, params)
      setForecastData(response.data)
      return response.data
    } catch (err) {
      setError(err.message || 'Failed to run forecast')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearForecast = useCallback(() => {
    setForecastData(null)
    setError(null)
  }, [])

  return {
    forecastData,
    isLoading,
    error,
    runForecast,
    clearForecast,
  }
}
