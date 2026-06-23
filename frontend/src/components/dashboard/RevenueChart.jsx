import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const data = [
  { month: 'Jan', actual: 32, forecast: 30 },
  { month: 'Feb', actual: 40, forecast: 38 },
  { month: 'Mar', actual: 38, forecast: 40 },
  { month: 'Apr', actual: 55, forecast: 50 },
  { month: 'May', actual: 60, forecast: 58 },
  { month: 'Jun', actual: 68, forecast: 65 },
  { month: 'Jul', actual: 78, forecast: 75 },
  { month: 'Aug', actual: 92, forecast: 88 },
]

const RevenueChart = () => {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Revenue trends</h3>
          <p className="text-sm text-slate-500 mt-0.5">Actual vs forecast (last 8 months)</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-primary-600" />
            <span className="text-xs text-slate-500">Actual</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span className="text-xs text-slate-500">Forecast</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <defs>
            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.02} />
            </linearGradient>
          </defs>
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
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Area
            type="monotone"
            dataKey="actual"
            stroke="#3b82f6"
            strokeWidth={2.5}
            fill="url(#colorActual)"
          />
          <Area
            type="monotone"
            dataKey="forecast"
            stroke="#8b5cf6"
            strokeWidth={2}
            strokeDasharray="5 5"
            fill="url(#colorForecast)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default RevenueChart
