import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const data = [
  { region: 'AMER', revenue: 140 },
  { region: 'EMEA', revenue: 100 },
  { region: 'APAC', revenue: 65 },
  { region: 'LATAM', revenue: 35 },
]

const RegionChart = () => {
  return (
    <div className="card p-6">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">Regional performance</h3>
        <p className="text-sm text-slate-500 mt-0.5">Revenue by region (K USD)</p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="region"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 12 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            domain={[0, 160]}
            ticks={[0, 40, 80, 120, 160]}
          />
          <Tooltip
            cursor={{ fill: '#f1f5f9' }}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Bar
            dataKey="revenue"
            fill="#3b82f6"
            radius={[6, 6, 0, 0]}
            maxBarSize={80}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default RegionChart
