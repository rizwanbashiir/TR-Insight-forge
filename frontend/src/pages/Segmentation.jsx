import React from 'react'
import { Users, Sparkles, Crown } from 'lucide-react'
import SegmentPyramid from '../components/segmentation/SegmentPyramid'
import SegmentTable from '../components/segmentation/SegmentTable'

const Segmentation = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-header">Customer Segments</h1>
        <p className="page-subheader">RFM-based segmentation powered by unsupervised learning.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="kpi-card">
          <p className="text-xs font-medium text-slate-500 uppercase">Total Customers</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">12,438</p>
          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center mt-3">
            <Users className="w-5 h-5 text-slate-500" />
          </div>
        </div>
        <div className="kpi-card">
          <p className="text-xs font-medium text-slate-500 uppercase">Silhouette Score</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">0.71</p>
          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center mt-3">
            <Sparkles className="w-5 h-5 text-slate-500" />
          </div>
        </div>
        <div className="kpi-card">
          <p className="text-xs font-medium text-slate-500 uppercase">Segments</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">4</p>
          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center mt-3">
            <Crown className="w-5 h-5 text-slate-500" />
          </div>
        </div>
      </div>

      <SegmentPyramid />
      <SegmentTable />
    </div>
  )
}

export default Segmentation
