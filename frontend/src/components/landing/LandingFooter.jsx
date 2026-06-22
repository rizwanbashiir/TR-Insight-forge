import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'

const LandingFooter = () => {
  return (
    <footer className="border-t border-slate-200 py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-slate-900">TR-Insight-Forge</span>
            </div>
            <p className="text-sm text-slate-500">
              The AI-powered business intelligence platform for modern teams. Forecast, segment, and chat with your data.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-4">Product</h4>
            <ul className="space-y-2">
              {['Forecasting', 'Segmentation', 'AI Assistant', 'Integrations'].map((item) => (
                <li key={item}>
                  <Link to="#" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">{item}</Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-4">Company</h4>
            <ul className="space-y-2">
              {['About', 'Customers', 'Security', 'Contact'].map((item) => (
                <li key={item}>
                  <Link to="#" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">{item}</Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default LandingFooter
