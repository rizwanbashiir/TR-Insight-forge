import React from 'react'

const segments = [
  { name: 'Champions', color: '#10b981' },
  { name: 'Loyal', color: '#3b82f6' },
  { name: 'At Risk', color: '#ef4444' },
  { name: 'Needs Attention', color: '#f59e0b' },
]

const SegmentPyramid = () => {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Segment clusters</h3>
          <p className="text-sm text-slate-500 mt-0.5">Recency × Frequency · bubble size = Monetary</p>
        </div>
        <div className="flex items-center gap-4">
          {segments.map((segment) => (
            <div key={segment.name} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: segment.color }} />
              <span className="text-xs text-slate-500">{segment.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Scatter plot simulation with bubbles */}
      <div className="relative h-80 bg-white rounded-lg border border-slate-100">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((tick) => (
            <g key={tick}>
              <line x1={tick} y1="0" x2={tick} y2="100" stroke="#f1f5f9" strokeWidth="0.5" strokeDasharray="2" />
              <line x1="0" y1={100 - tick} x2="100" y2={100 - tick} stroke="#f1f5f9" strokeWidth="0.5" strokeDasharray="2" />
            </g>
          ))}

          {/* Sample bubbles */}
          <circle cx="15" cy="85" r="3" fill="#ef4444" opacity="0.7" />
          <circle cx="25" cy="75" r="2" fill="#3b82f6" opacity="0.7" />
          <circle cx="35" cy="65" r="4" fill="#10b981" opacity="0.7" />
          <circle cx="45" cy="55" r="2.5" fill="#f59e0b" opacity="0.7" />
          <circle cx="55" cy="80" r="3" fill="#ef4444" opacity="0.7" />
          <circle cx="65" cy="45" r="3.5" fill="#10b981" opacity="0.7" />
          <circle cx="75" cy="70" r="2" fill="#3b82f6" opacity="0.7" />
          <circle cx="85" cy="60" r="2.5" fill="#f59e0b" opacity="0.7" />
          <circle cx="20" cy="50" r="3" fill="#3b82f6" opacity="0.7" />
          <circle cx="30" cy="40" r="2" fill="#10b981" opacity="0.7" />
          <circle cx="40" cy="90" r="2.5" fill="#f59e0b" opacity="0.7" />
          <circle cx="50" cy="30" r="3" fill="#10b981" opacity="0.7" />
          <circle cx="60" cy="85" r="2" fill="#ef4444" opacity="0.7" />
          <circle cx="70" cy="35" r="3.5" fill="#3b82f6" opacity="0.7" />
          <circle cx="80" cy="75" r="2" fill="#f59e0b" opacity="0.7" />
          <circle cx="90" cy="50" r="2.5" fill="#10b981" opacity="0.7" />
        </svg>

        {/* Axis labels */}
        <div className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-slate-400">Recency</div>
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs text-slate-400">Frequency</div>
      </div>
    </div>
  )
}

export default SegmentPyramid
