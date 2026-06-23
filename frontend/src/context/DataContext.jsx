import React, { createContext, useContext, useReducer } from 'react'

const initialState = {
  user: null,
  isAuthenticated: false,
  datasets: [],
  selectedDatasets: [],
  dashboardData: null,
  forecastData: null,
  segmentationData: null,
  insightsData: null,
  currentWorkspace: null,
}

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload, isAuthenticated: true }
    case 'LOGOUT':
      return { ...initialState }
    case 'SET_DATASETS':
      return { ...state, datasets: action.payload }
    case 'ADD_DATASET':
      return { ...state, datasets: [...state.datasets, action.payload] }
    case 'SELECT_DATASETS':
      return { ...state, selectedDatasets: action.payload }
    case 'SET_DASHBOARD_DATA':
      return { ...state, dashboardData: action.payload }
    case 'SET_FORECAST_DATA':
      return { ...state, forecastData: action.payload }
    case 'SET_SEGMENTATION_DATA':
      return { ...state, segmentationData: action.payload }
    case 'SET_INSIGHTS_DATA':
      return { ...state, insightsData: action.payload }
    case 'SET_WORKSPACE':
      return { ...state, currentWorkspace: action.payload }
    default:
      return state
  }
}

const DataContext = createContext()

export function DataProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  return (
    <DataContext.Provider value={{ state, dispatch }}>
      {children}
    </DataContext.Provider>
  )
}

export function useData() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within a DataProvider')
  }
  return context
}
