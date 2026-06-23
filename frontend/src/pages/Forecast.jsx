import React from 'react'
import { Play, Target, TrendingUp, Zap } from 'lucide-react'
import ForecastChart from '../components/forecast/ForecastChart'
import ForecastTable from '../components/forecast/ForecastTable'

const Forecast = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-header">Forecasting</h1>
        <p className="page-subheader">Generate AI-powered revenue forecasts with confidence intervals.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="card p-6">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Configure forecast</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Dataset</label>
              <select className="input-field">
                <option>orders_2024_q3.csv</option>
                <option>customers_master.xlsx</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Forecast horizon</label>
              <div className="flex items-center gap-4">
                <span className="text-xs text-slate-500">1mo</span>
                <input type="range" min="1" max="24" defaultValue="6" className="flex-1" />
                <span className="text-xs text-slate-500">24mo</span>
              </div>
              <p className="text-sm font-semibold text-slate-900 mt-1">6 months</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Model</label>
              <select className="input-field">
                <option>Auto (ensemble)</option>
                <option>ARIMA</option>
                <option>Prophet</option>
              </select>
            </div>
            <button className="btn-primary w-full py-3">
              <Play className="w-4 h-4 mr-2" />
              Run forecast
            </button>
          </div>
        </div>

        {/* Metrics & Chart */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="kpi-card">
              <p className="text-xs font-medium text-slate-500 uppercase">Accuracy</p>
              <p className="text-2xl font-bold text-slate-900 mt-2">94.7%</p>
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mt-3">
                <Target className="w-5 h-5 text-emerald-500" />
              </div>
            </div>
            <div className="kpi-card">
              <p className="text-xs font-medium text-slate-500 uppercase">MAPE</p>
              <p className="text-2xl font-bold text-slate-900 mt-2">5.3%</p>
              <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center mt-3">
                <TrendingUp className="w-5 h-5 text-primary-500" />
              </div>
            </div>
            <div className="kpi-card">
              <p className="text-xs font-medium text-slate-500 uppercase">Confidence</p>
              <p className="text-2xl font-bold text-slate-900 mt-2">95%</p>
              <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center mt-3">
                <Zap className="w-5 h-5 text-purple-500" />
              </div>
            </div>
          </div>
          <ForecastChart />
        </div>
      </div>
    </div>
  )
}

export default Forecast
