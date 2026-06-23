import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const data = [
  { month: 'Jan', historical: 32, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Feb', historical: 38, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Mar', historical: 45, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Apr', historical: 55, forecast: null, ciUpper: null, ciLower: null },
  { month: 'May', historical: 58, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Jun', historical: 56, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Jul', historical: 60, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Aug', historical: 65, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Sep', historical: 62, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Oct', historical: 68, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Nov', historical: 72, forecast: null, ciUpper: null, ciLower: null },
  { month: 'Dec', historical: null, forecast: 75, ciUpper: 85, ciLower: 65 },
  { month: 'Jan', historical: null, forecast: 82, ciUpper: 98, ciLower: 70 },
  { month: 'Feb', historical: null, forecast: 88, ciUpper: 108, ciLower: 72 },
  { month: 'Mar', historical: null, forecast: 95, ciUpper: 118, ciLower: 75 },
  { month: 'Apr', historical: null, forecast: 102, ciUpper: 128, ciLower: 78 },
  { month: 'May', historical: null, forecast: 108, ciUpper: 138, ciLower: 80 },
  { month: 'Jun', historical: null, forecast: 115, ciUpper: 148, ciLower: 82 },
]

const ForecastChart = () => {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Revenue forecast</h3>
          <p className="text-sm text-slate-500 mt-0.5">Historical · Forecast · 95% confidence interval</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span className="text-xs text-slate-500">Historical</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span className="text-xs text-slate-500">Forecast</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-200" />
            <span className="text-xs text-slate-500">CI</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="month"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            domain={[0, 120]}
            ticks={[0, 30, 60, 90, 120]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Line
            type="monotone"
            dataKey="historical"
            stroke="#10b981"
            strokeWidth={2.5}
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#8b5cf6"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="ciUpper"
            stroke="#c4b5fd"
            strokeWidth={0}
            fill="#c4b5fd"
            fillOpacity={0.2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="ciLower"
            stroke="#c4b5fd"
            strokeWidth={0}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ForecastChart
