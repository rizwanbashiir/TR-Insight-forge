import React from 'react'
import { Crown, Heart, AlertTriangle, User } from 'lucide-react'
import { formatCurrency, formatNumber } from '../../utils/formatter'

const segments = [
  {
    name: 'Champions',
    icon: Crown,
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    customers: 1842,
    avgRecency: 12,
    avgFrequency: 24,
    avgMonetary: 8420,
    action: 'Reward loyalty · upsell premium',
  },
  {
    name: 'Loyal',
    icon: Heart,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    customers: 3211,
    avgRecency: 28,
    avgFrequency: 14,
    avgMonetary: 3120,
    action: 'Cross-sell · gather reviews',
  },
  {
    name: 'At Risk',
    icon: AlertTriangle,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    customers: 318,
    avgRecency: 92,
    avgFrequency: 18,
    avgMonetary: 4810,
    action: 'Trigger win-back campaign',
  },
  {
    name: 'Needs Attention',
    icon: User,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    customers: 1024,
    avgRecency: 64,
    avgFrequency: 6,
    avgMonetary: 910,
    action: 'Re-engage with offer',
  },
]

const SegmentTable = () => {
  return (
    <div className="card overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200">
        <h3 className="text-base font-semibold text-slate-900">Segment breakdown</h3>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100">
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Segment</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Customers</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Recency (days)</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Frequency</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Monetary</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Recommended Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {segments.map((segment) => {
            const Icon = segment.icon
            return (
              <tr key={segment.name} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg ${segment.iconBg} flex items-center justify-center`}>
                      <Icon className={`w-4 h-4 ${segment.iconColor}`} />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{segment.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-900">
                  {formatNumber(segment.customers)}
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-900">
                  {segment.avgRecency}
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-900">
                  {segment.avgFrequency}
                </td>
                <td className="px-6 py-4 text-right text-sm font-semibold text-slate-900">
                  {formatCurrency(segment.avgMonetary)}
                </td>
                <td className="px-6 py-4 text-sm text-slate-600">
                  {segment.action}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default SegmentTable
