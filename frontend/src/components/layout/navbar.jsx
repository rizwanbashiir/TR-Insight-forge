import React from 'react'
import { Search, Bell, Settings } from 'lucide-react'

const Navbar = ({ user, workspace }) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search insights, datasets, customers..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 border border-slate-200 rounded px-1.5 py-0.5">
            ⌘K
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
        </button>
        <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
          <Settings className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 ml-2">
          <div className="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
            {user?.initials || 'AL'}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Navbar
