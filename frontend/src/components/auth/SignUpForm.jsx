import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useData } from '../../context/DataContext'

const plans = [
  { name: 'Free', description: 'Try the platform', price: '$0' },
  { name: 'Growth', description: 'For growing teams', price: '$49/seat/mo', popular: true },
  { name: 'Enterprise', description: 'SSO, SLA, DPA', price: 'Custom' },
]

const SignUpForm = () => {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    firstName: 'Ada',
    lastName: 'Lovelace',
    email: 'ada@company.com',
    password: '',
    orgName: 'Acme Inc.',
    industry: 'SaaS',
    teamSize: '1-10',
    plan: 'Growth',
  })
  const navigate = useNavigate()
  const { dispatch } = useData()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleContinue = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      dispatch({
        type: 'SET_USER',
        payload: { name: `${formData.firstName} ${formData.lastName}`, initials: `${formData.firstName[0]}${formData.lastName[0]}`, role: 'Admin', email: formData.email },
      })
      dispatch({
        type: 'SET_WORKSPACE',
        payload: { name: formData.orgName, plan: formData.plan, seats: '12' },
      })
      localStorage.setItem('token', 'mock-token')
      navigate('/dashboard')
    }
  }

  const handleBack = () => {
    if (step > 1) setStep(step - 1)
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 gradient-blue items-end p-12 text-white relative overflow-hidden">
        <Link
  to="/"
  className="absolute top-8 left-8 flex items-center gap-2 hover:opacity-90 transition-opacity"
>
  <Sparkles className="w-5 h-5" />
  <span className="font-semibold">TR-Insight-Forge</span>
</Link>
        <div>
          <blockquote className="text-3xl font-bold leading-tight mb-6">
            "We replaced three BI tools and a data analyst in one quarter."
          </blockquote>
          <div>
            <p className="font-semibold">Maya Tanaka</p>
            <p className="text-white/70">VP of Analytics, Lumen</p>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Create your workspace</h2>
              <p className="text-sm text-slate-500 mt-1">Step {step} of 3 — {step === 1 ? 'Personal info' : step === 2 ? 'Organization' : 'Plan'}</p>
            </div>

            {/* Progress bar */}
            <div className="flex gap-2 mb-8">
              {[1, 2, 3].map((s) => (
                <div key={s} className={`h-1.5 flex-1 rounded-full ${s <= step ? 'bg-primary-600' : 'bg-slate-100'}`} />
              ))}
            </div>

            {/* Step 1: Personal Info */}
            {step === 1 && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">First name</label>
                    <input name="firstName" value={formData.firstName} onChange={handleChange} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Last name</label>
                    <input name="lastName" value={formData.lastName} onChange={handleChange} className="input-field" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Work email</label>
                  <input type="email" name="email" value={formData.email} onChange={handleChange} className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
                  <input type="password" name="password" value={formData.password} onChange={handleChange} placeholder="••••••••" className="input-field" />
                </div>
              </div>
            )}

            {/* Step 2: Organization */}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Organization name</label>
                  <input name="orgName" value={formData.orgName} onChange={handleChange} className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Industry</label>
                  <select name="industry" value={formData.industry} onChange={handleChange} className="input-field">
                    <option>SaaS</option>
                    <option>E-commerce</option>
                    <option>Retail</option>
                    <option>Manufacturing</option>
                    <option>Healthcare</option>
                    <option>Finance</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Team size</label>
                  <select name="teamSize" value={formData.teamSize} onChange={handleChange} className="input-field">
                    <option>1-10</option>
                    <option>11-50</option>
                    <option>51-200</option>
                    <option>200+</option>
                  </select>
                </div>
              </div>
            )}

            {/* Step 3: Plan */}
            {step === 3 && (
              <div className="space-y-3">
                {plans.map((plan) => (
                  <label
                    key={plan.name}
                    className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                      formData.plan === plan.name
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="plan"
                        value={plan.name}
                        checked={formData.plan === plan.name}
                        onChange={handleChange}
                        className="w-4 h-4 text-primary-600"
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-slate-900">{plan.name}</span>
                          {plan.popular && (
                            <span className="px-2 py-0.5 bg-primary-100 text-primary-600 text-xs rounded-full">Popular</span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500">{plan.description}</p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{plan.price}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-3 mt-6">
              {step > 1 && (
                <button onClick={handleBack} className="btn-secondary flex-1 py-3">
                  Back
                </button>
              )}
              <button onClick={handleContinue} className="btn-primary flex-1 py-3">
                {step === 3 ? 'Create workspace' : 'Continue'}
              </button>
            </div>

            <p className="text-center text-sm text-slate-500 mt-6">
              Already have an account? <Link to="/signin" className="text-primary-600 hover:text-primary-700 font-medium">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignUpForm
