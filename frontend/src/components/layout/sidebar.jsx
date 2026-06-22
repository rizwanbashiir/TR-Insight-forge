import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Upload,
  TrendingUp,
  Users,
  MessageSquare,
  CreditCard,
  LogOut,
  ChevronDown,
  Building2,
} from 'lucide-react'
import { useData } from '../../context/DataContext'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/uploads', label: 'Uploads', icon: Upload },
  { path: '/forecasting', label: 'Forecasting', icon: TrendingUp },
  { path: '/segments', label: 'Customer Segments', icon: Users },
  { path: '/ai-chat', label: 'AI Chat', icon: MessageSquare },
  { path: '/team-billing', label: 'Team & Billing', icon: CreditCard },
]

const Sidebar = () => {
  const location = useLocation()
  const { state, dispatch } = useData()

  const handleLogout = () => {
    localStorage.removeItem('token')
    dispatch({ type: 'LOGOUT' })
    window.location.href = '/signin'
  }

  return (
    <aside className="w-64 h-screen bg-sidebar-bg border-r border-slate-200 flex flex-col fixed left-0 top-0 z-40">
      {/* Workspace Selector */}
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-slate-100 cursor-pointer transition-colors">
          <div className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center">
            <Building2 className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-900 truncate">
              {state.currentWorkspace?.name || 'Acme Inc.'}
            </p>
            <p className="text-xs text-slate-500">
              {state.currentWorkspace?.plan || 'Growth'} · {state.currentWorkspace?.seats || '12'} seats
            </p>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={isActive ? 'nav-link-active' : 'nav-link'}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
            {state.user?.initials || 'AL'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900">
              {state.user?.name || 'Ada Lovelace'}
            </p>
            <p className="text-xs text-success-600 font-medium">
              {state.user?.role || 'Admin'}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
