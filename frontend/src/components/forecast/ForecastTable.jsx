import React from 'react'
import { formatCurrency } from '../../utils/formatter'

const ForecastTable = () => {
  const forecastData = [
    { month: 'Dec 2024', forecast: 75000, lower: 65000, upper: 85000 },
    { month: 'Jan 2025', forecast: 82000, lower: 70000, upper: 98000 },
    { month: 'Feb 2025', forecast: 88000, lower: 72000, upper: 108000 },
    { month: 'Mar 2025', forecast: 95000, lower: 75000, upper: 118000 },
    { month: 'Apr 2025', forecast: 102000, lower: 78000, upper: 128000 },
    { month: 'May 2025', forecast: 108000, lower: 80000, upper: 138000 },
  ]

  return (
    <div className="card overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200">
        <h3 className="text-base font-semibold text-slate-900">Forecast details</h3>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100">
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Month</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Forecast</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Lower (95%)</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Upper (95%)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {forecastData.map((row, index) => (
            <tr key={index} className="hover:bg-slate-50">
              <td className="px-6 py-3 text-sm font-medium text-slate-900">{row.month}</td>
              <td className="px-6 py-3 text-sm text-slate-900 text-right">{formatCurrency(row.forecast)}</td>
              <td className="px-6 py-3 text-sm text-slate-500 text-right">{formatCurrency(row.lower)}</td>
              <td className="px-6 py-3 text-sm text-slate-500 text-right">{formatCurrency(row.upper)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ForecastTable
