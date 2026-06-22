import React from 'react'
import { Download, Plus } from 'lucide-react'
import KPICards from '../components/dashboard/KPICards'
import RevenueChart from '../components/dashboard/RevenueChart'
import CategoryChart from '../components/dashboard/CategoryChart'
import RegionChart from '../components/dashboard/RegionChart'
import AIReport from '../components/insights/AIReport'

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-header">Dashboard</h1>
          <p className="page-subheader">Welcome back, Ada. Here's what's happening today.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            New analysis
          </button>
        </div>
      </div>

      <KPICards />

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevenueChart />
        </div>
        <div>
          <CategoryChart />
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RegionChart />
        </div>
        <div>
          <AIReport />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
