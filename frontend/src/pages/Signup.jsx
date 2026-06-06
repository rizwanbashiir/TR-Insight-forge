import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check } from 'lucide-react';
import AuthLayout from '../components/auth/AuthLayout';
import './AuthForm.css';

const Signup = () => {
  const [step, setStep] = useState(1);
  const [selectedPlan, setSelectedPlan] = useState('growth');

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  return (
    <AuthLayout>
      <div className="auth-card glass-panel">
        <h2 className="auth-title">Create your workspace</h2>
        <p className="auth-subtitle">
          Step {step} of 3 — {step === 1 ? 'Personal info' : step === 2 ? 'Organization' : 'Plan'}
        </p>

        <div className="wizard-progress">
          <div className={`progress-segment ${step >= 1 ? 'active' : ''}`}></div>
          <div className={`progress-segment ${step >= 2 ? 'active' : ''}`}></div>
          <div className={`progress-segment ${step >= 3 ? 'active' : ''}`}></div>
        </div>

        {step === 1 && (
          <form className="auth-form" onSubmit={(e) => { e.preventDefault(); nextStep(); }}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">First name</label>
                <input type="text" id="firstName" placeholder="Ada" required />
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Last name</label>
                <input type="text" id="lastName" placeholder="Lovelace" required />
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="workEmail">Work email</label>
              <input type="email" id="workEmail" placeholder="ada@company.com" required />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input type="password" id="password" placeholder="••••••••" required />
            </div>
            
            <button type="submit" className="btn btn-primary btn-block auth-submit">Continue</button>
          </form>
        )}

        {step === 2 && (
          <form className="auth-form" onSubmit={(e) => { e.preventDefault(); nextStep(); }}>
            <div className="form-group">
              <label htmlFor="orgName">Organization name</label>
              <input type="text" id="orgName" placeholder="Acme Inc." required />
            </div>
            
            <div className="form-group">
              <label htmlFor="industry">Industry</label>
              <select id="industry" required>
                <option value="saas">SaaS</option>
                <option value="ecommerce">E-commerce</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="teamSize">Team size</label>
              <select id="teamSize" required>
                <option value="1-10">1-10</option>
                <option value="11-50">11-50</option>
                <option value="51-200">51-200</option>
                <option value="201+">201+</option>
              </select>
            </div>
            
            <div className="flex gap-4 mt-4">
              <button type="button" className="btn btn-outline" onClick={prevStep} style={{flex: 1}}>Back</button>
              <button type="submit" className="btn btn-primary" style={{flex: 2}}>Continue</button>
            </div>
          </form>
        )}

        {step === 3 && (
          <form className="auth-form" onSubmit={(e) => { e.preventDefault(); alert('Workspace created!'); }}>
            <div className="plan-selector">
              <div 
                className={`plan-option ${selectedPlan === 'free' ? 'selected' : ''}`}
                onClick={() => setSelectedPlan('free')}
              >
                <div className="plan-info">
                  <div className="plan-name">Free</div>
                  <div className="plan-desc">Try the platform</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="plan-price">$0</span>
                  {selectedPlan === 'free' && <Check size={18} color="var(--primary-blue)" />}
                </div>
              </div>

              <div 
                className={`plan-option ${selectedPlan === 'growth' ? 'selected' : ''}`}
                onClick={() => setSelectedPlan('growth')}
              >
                <div className="plan-info">
                  <div className="plan-name">Growth <span className="popular-tag">Popular</span></div>
                  <div className="plan-desc">For growing teams</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="plan-price">$49/seat/mo</span>
                  {selectedPlan === 'growth' && <Check size={18} color="var(--primary-blue)" />}
                </div>
              </div>

              <div 
                className={`plan-option ${selectedPlan === 'enterprise' ? 'selected' : ''}`}
                onClick={() => setSelectedPlan('enterprise')}
              >
                <div className="plan-info">
                  <div className="plan-name">Enterprise</div>
                  <div className="plan-desc">SSO, SLA, DPA</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="plan-price">Custom</span>
                  {selectedPlan === 'enterprise' && <Check size={18} color="var(--primary-blue)" />}
                </div>
              </div>
            </div>

            <div className="flex gap-4 mt-4">
              <button type="button" className="btn btn-outline" onClick={prevStep} style={{flex: 1}}>Back</button>
              <button type="submit" className="btn btn-primary" style={{flex: 2}}>Create workspace</button>
            </div>
          </form>
        )}

        <div className="auth-footer">
          Already have an account? <Link to="/login" className="auth-link">Sign in</Link>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Signup;
