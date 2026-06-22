import React from 'react'
import { TrendingUp, Users, MessageSquare, Shield } from 'lucide-react'

const features = [
  {
    icon: TrendingUp,
    title: 'AI Forecasting',
    description: 'Predict future sales trends with advanced time-series models. Confidence intervals and accuracy scoring built in.',
  },
  {
    icon: Users,
    title: 'Customer Intelligence',
    description: 'RFM segmentation surfaces Champions, Loyal, At-Risk, and Growth Opportunity cohorts automatically.',
  },
  {
    icon: MessageSquare,
    title: 'AI Data Assistant',
    description: 'Ask questions in natural language and get instant insights backed by your live dataset context.',
  },
  {
    icon: Shield,
    title: 'Multi-Tenant Workspaces',
    description: 'Isolated data, role-based access, and SOC-grade controls for every organization on the platform.',
  },
]

const FeaturesSection = () => {
  return (
    <section className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-3">Platform</p>
          <h2 className="text-4xl font-bold text-slate-900">
            Everything your team needs to{' '}
            <span className="text-primary-600">decide with data</span>
          </h2>
          <p className="text-lg text-slate-500 mt-4 max-w-2xl mx-auto">
            From ingestion to forecasting to natural-language analysis — one unified workspace.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <div key={feature.title} className="card p-6 hover:shadow-md transition-shadow">
                <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSection
