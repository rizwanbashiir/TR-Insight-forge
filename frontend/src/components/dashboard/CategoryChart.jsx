import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts'

const data = [
  { name: 'Enterprise', value: 42, color: '#3b82f6' },
  { name: 'Mid-market', value: 31, color: '#6366f1' },
  { name: 'SMB', value: 18, color: '#10b981' },
  { name: 'Self-serve', value: 9, color: '#f59e0b' },
]

const CategoryChart = () => {
  return (
    <div className="card p-6">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">Sales distribution</h3>
        <p className="text-sm text-slate-500 mt-0.5">By customer segment</p>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="space-y-2 mt-2">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-slate-600">{item.name}</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default CategoryChart
