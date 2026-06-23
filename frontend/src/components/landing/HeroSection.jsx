import React from 'react'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 to-blue-50 pt-20 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-white rounded-full border border-slate-200 shadow-sm mb-6">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-sm text-slate-600">Now with GPT-powered Insights Hub</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
              Transform business data into{' '}
              <span className="text-primary-600">actionable intelligence.</span>
            </h1>
            <p className="text-lg text-slate-500 mt-6 max-w-lg">
              Upload datasets, forecast future revenue, identify customer segments, and chat with your data using AI — all in one enterprise-grade workspace.
            </p>
            <div className="flex items-center gap-4 mt-8">
              <Link to="/signup" className="btn-primary px-6 py-3 text-base">
                Start free trial
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
              <Link to="/signin" className="btn-secondary px-6 py-3 text-base">
                Book demo
              </Link>
            </div>
          </div>
          <div className="relative">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 p-6">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase">Revenue</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">$284K</p>
                  <p className="text-xs text-emerald-600 mt-1">↑ +18.2%</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase">Customers</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">12,438</p>
                  <p className="text-xs text-emerald-600 mt-1">↑ +4.1%</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase">Forecast Acc.</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">94.7%</p>
                  <p className="text-xs text-emerald-600 mt-1">↑ +2.3%</p>
                </div>
              </div>
              <div className="bg-slate-50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-slate-900">Revenue forecast</p>
                  <span className="text-xs text-slate-500">8-month horizon · 95% CI</span>
                </div>
                <div className="h-32 flex items-end gap-1">
                  {[40, 42, 38, 55, 60, 68, 78, 92].map((h, i) => (
                    <div key={i} className="flex-1 bg-primary-500 rounded-t" style={{ height: `${h}%`, opacity: 0.7 + i * 0.04 }} />
                  ))}
                </div>
                <div className="flex justify-between mt-2 text-xs text-slate-400">
                  <span>Feb</span>
                  <span>Apr</span>
                  <span>Jun</span>
                  <span>Aug</span>
                </div>
              </div>
              <div className="mt-4 flex items-start gap-3 bg-slate-50 rounded-xl p-4">
                <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">AI Insight</p>
                  <p className="text-sm text-slate-500 mt-1">Q3 revenue is projected to grow 22% driven by Enterprise segment. 318 at-risk customers detected.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSection
