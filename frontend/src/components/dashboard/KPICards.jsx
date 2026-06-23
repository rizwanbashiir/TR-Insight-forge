import React from 'react'
import { TrendingUp, TrendingDown, Minus, DollarSign, ShoppingCart, Users, Target } from 'lucide-react'
import { formatCurrency, formatNumber, getTrendColor } from '../../utils/formatter'

const kpiData = [
  {
    title: 'Total Revenue',
    value: 284219,
    change: 18.2,
    icon: DollarSign,
    iconBg: 'bg-success-50',
    iconColor: 'text-success-500',
    format: 'currency',
  },
  {
    title: 'Transactions',
    value: 48902,
    change: 9.4,
    icon: ShoppingCart,
    iconBg: 'bg-primary-50',
    iconColor: 'text-primary-500',
    format: 'number',
  },
  {
    title: 'Customers',
    value: 12438,
    change: 4.1,
    icon: Users,
    iconBg: 'bg-purple-50',
    iconColor: 'text-purple-500',
    format: 'number',
  },
  {
    title: 'Forecast Accuracy',
    value: 94.7,
    change: -0.3,
    icon: Target,
    iconBg: 'bg-warning-50',
    iconColor: 'text-warning-500',
    format: 'percent',
    suffix: '%',
  },
]

const KPICards = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiData.map((kpi, index) => {
        const Icon = kpi.icon
        const isPositive = kpi.change > 0
        const isNegative = kpi.change < 0

        return (
          <div key={index} className="kpi-card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                  {kpi.title}
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-2">
                  {kpi.format === 'currency'
                    ? formatCurrency(kpi.value)
                    : kpi.format === 'percent'
                    ? `${kpi.value}%`
                    : formatNumber(kpi.value)}
                </p>
                <div className="flex items-center gap-1 mt-2">
                  {isPositive && (
                    <TrendingUp className="w-3.5 h-3.5 text-success-600" />
                  )}
                  {isNegative && (
                    <TrendingDown className="w-3.5 h-3.5 text-danger-600" />
                  )}
                  {!isPositive && !isNegative && (
                    <Minus className="w-3.5 h-3.5 text-slate-400" />
                  )}
                  <span
                    className={`text-sm font-medium ${
                      isPositive
                        ? 'text-success-600'
                        : isNegative
                        ? 'text-danger-600'
                        : 'text-slate-500'
                    }`}
                  >
                    {isPositive ? '+' : ''}
                    {kpi.change}% vs last month
                  </span>
                </div>
              </div>
              <div className={`w-10 h-10 rounded-xl ${kpi.iconBg} flex items-center justify-center`}>
                <Icon className={`w-5 h-5 ${kpi.iconColor}`} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default KPICards
