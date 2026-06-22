import { useState, useCallback } from 'react'
import { insightsService } from '../services/insightsService'

export const useInsights = () => {
  const [insights, setInsights] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const generateInsights = useCallback(async (data) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await insightsService.generateInsights(data)
      setInsights(response.data)
      return response.data
    } catch (err) {
      setError(err.message || 'Failed to generate insights')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const sendChat = useCallback(async (message, context) => {
    setIsLoading(true)
    try {
      const response = await insightsService.chat(message, context)
      const newMessage = {
        id: Date.now(),
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString(),
      }
      setChatHistory((prev) => [...prev, newMessage])
      return response.data
    } catch (err) {
      setError(err.message || 'Failed to send message')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const addUserMessage = useCallback((message) => {
    const newMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }
    setChatHistory((prev) => [...prev, newMessage])
  }, [])

  const clearChat = useCallback(() => {
    setChatHistory([])
  }, [])

  return {
    insights,
    chatHistory,
    isLoading,
    error,
    generateInsights,
    sendChat,
    addUserMessage,
    clearChat,
  }
}
