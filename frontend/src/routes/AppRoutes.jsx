import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useData } from '../context/DataContext'

// Layout
import Navbar from '../components/layout/Navbar'
import Sidebar from '../components/layout/Sidebar'
import Footer from '../components/layout/Footer'

// Landing & Auth
import Home from '../pages/Home'
import SignInForm from '../components/auth/SignInForm'
import SignUpForm from '../components/auth/SignUpForm'

// App Pages
import Dashboard from '../pages/Dashboard'
import Upload from '../pages/Upload'
import Forecast from '../pages/Forecast'
import Segmentation from '../pages/Segmentation'
import Insights from '../pages/Insights'
import TeamBilling from '../pages/TeamBilling'

const AppLayout = ({ children }) => {
  const { state } = useData()

  // For demo purposes, always authenticated. In production, check token
  const isAuthenticated = state.isAuthenticated || localStorage.getItem('token')

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 ml-64">
        <Navbar user={state.user} workspace={state.currentWorkspace} />
        <main className="p-6 pt-20 pb-12">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  )
}

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Home />} />
      <Route path="/signin" element={<SignInForm />} />
      <Route path="/signup" element={<SignUpForm />} />

      {/* Protected App Routes */}
      <Route
        path="/dashboard"
        element={
          <AppLayout>
            <Dashboard />
          </AppLayout>
        }
      />
      <Route
        path="/uploads"
        element={
          <AppLayout>
            <Upload />
          </AppLayout>
        }
      />
      <Route
        path="/forecasting"
        element={
          <AppLayout>
            <Forecast />
          </AppLayout>
        }
      />
      <Route
        path="/segments"
        element={
          <AppLayout>
            <Segmentation />
          </AppLayout>
        }
      />
      <Route
        path="/ai-chat"
        element={
          <AppLayout>
            <Insights />
          </AppLayout>
        }
      />
      <Route
        path="/team-billing"
        element={
          <AppLayout>
            <TeamBilling />
          </AppLayout>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default AppRoutes
