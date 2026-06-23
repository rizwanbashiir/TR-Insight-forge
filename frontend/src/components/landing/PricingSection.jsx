import React from 'react'
import { Link } from 'react-router-dom'
import { Check } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    description: 'For exploring the platform.',
    price: '$0',
    period: '',
    button: 'Get started',
    buttonStyle: 'btn-secondary',
    features: ['1 workspace', 'Up to 5K rows / dataset', 'Basic forecasting', 'Community support'],
  },
  {
    name: 'Growth',
    description: 'For growing data teams.',
    price: '$49',
    period: '/seat/mo',
    button: 'Get started',
    buttonStyle: 'btn-primary',
    popular: true,
    features: ['Unlimited datasets', 'Advanced forecasting & RFM', 'AI Assistant (1M tokens)', 'Priority support', '5 team members included'],
  },
  {
    name: 'Enterprise',
    description: 'For regulated organizations.',
    price: 'Custom',
    period: '',
    button: 'Contact sales',
    buttonStyle: 'btn-secondary',
    features: ['SSO & SAML', 'Dedicated tenant', 'Unlimited seats', 'SLA & DPA', 'Custom integrations'],
  },
]

const PricingSection = () => {
  return (
    <section className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <p className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-3">Pricing</p>
          <h2 className="text-4xl font-bold text-slate-900">Plans for every stage</h2>
          <p className="text-lg text-slate-500 mt-4">Start free. Scale when you're ready. Switch plans anytime.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div key={plan.name} className={`card p-6 relative ${plan.popular ? 'ring-2 ring-primary-500' : ''}`}>
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="px-3 py-1 bg-primary-600 text-white text-xs font-medium rounded-full">
                    Most popular
                  </span>
                </div>
              )}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-slate-900">{plan.name}</h3>
                <p className="text-sm text-slate-500 mt-1">{plan.description}</p>
              </div>
              <div className="mb-6">
                <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                <span className="text-sm text-slate-500">{plan.period}</span>
              </div>
              <Link to="/signup" className={`${plan.buttonStyle} w-full mb-6`}>
                {plan.button}
              </Link>
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-slate-700">
                    <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PricingSection
