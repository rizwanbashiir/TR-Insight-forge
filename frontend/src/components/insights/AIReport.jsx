import React from 'react'
import { Sparkles, TrendingUp, AlertTriangle, Users } from 'lucide-react'

const insights = [
  {
    type: 'positive',
    icon: TrendingUp,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    title: 'Revenue trending +22% above forecast in EMEA.',
    description: 'Consider expanding sales capacity in the region.',
  },
  {
    type: 'warning',
    icon: AlertTriangle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    title: '318 customers entered At-Risk segment.',
    description: 'Trigger win-back automation this week.',
  },
  {
    type: 'info',
    icon: Users,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    title: 'Enterprise tier LTV up 14% QoQ.',
    description: 'Top driver: multi-year contract conversions.',
  },
]

const AIReport = () => {
  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary-600 text-white flex items-center justify-center">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-900">AI Insights</h3>
        </div>
      </div>
      <div className="space-y-3">
        {insights.map((insight, index) => {
          const Icon = insight.icon
          return (
            <div
              key={index}
              className={`p-4 rounded-xl ${insight.bgColor} border border-slate-100`}
            >
              <div className="flex items-start gap-3">
                <Icon className={`w-5 h-5 ${insight.color} mt-0.5 flex-shrink-0`} />
                <div>
                  <p className={`text-sm font-semibold ${insight.color}`}>{insight.title}</p>
                  <p className="text-sm text-slate-600 mt-1">{insight.description}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AIReport
