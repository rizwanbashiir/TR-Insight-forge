import React from 'react';
import { Link } from 'react-router-dom';
import { Check } from 'lucide-react';
import './Pricing.css';

const Pricing = () => {
  return (
    <section className="pricing container" id="pricing">
      <div className="pricing-header text-center flex flex-col items-center">
        <span className="section-label">PRICING</span>
        <h2 className="section-title">Plans for every stage</h2>
        <p className="section-subtitle">
          Start free. Scale when you're ready. Switch plans anytime.
        </p>
      </div>

      <div className="pricing-grid">
        {/* Free Plan */}
        <div className="pricing-card">
          <div className="plan-name">Free</div>
          <div className="plan-desc">For exploring the platform.</div>
          <div className="plan-price flex items-baseline">
            <span className="price-amount">₹0</span>
          </div>
          <Link to="/signup" className="btn btn-outline btn-block mt-4 mb-8">Get started</Link>
          
          <ul className="plan-features">
            <li><Check size={16} color="#10b981" /> 1 workspace</li>
            <li><Check size={16} color="#10b981" /> Up to 5K rows / dataset</li>
            <li><Check size={16} color="#10b981" /> Basic forecasting</li>
            <li><Check size={16} color="#10b981" /> Community support</li>
          </ul>
        </div>

        {/* Growth Plan */}
        <div className="pricing-card popular">
          <div className="popular-badge">Most popular</div>
          <div className="plan-name">Growth</div>
          <div className="plan-desc">For growing data teams.</div>
          <div className="plan-price flex items-baseline">
            <span className="price-amount">₹3,999</span>
            <span className="price-period">/seat/mo</span>
          </div>
          <Link to="/signup" className="btn btn-primary btn-block mt-4 mb-8">Get started</Link>
          
          <ul className="plan-features">
            <li><Check size={16} color="#10b981" /> Unlimited datasets</li>
            <li><Check size={16} color="#10b981" /> Advanced forecasting & RFM</li>
            <li><Check size={16} color="#10b981" /> AI Assistant (1M tokens)</li>
            <li><Check size={16} color="#10b981" /> Priority support</li>
            <li><Check size={16} color="#10b981" /> 5 team members included</li>
          </ul>
        </div>

        {/* Enterprise Plan */}
        <div className="pricing-card">
          <div className="plan-name">Enterprise</div>
          <div className="plan-desc">For regulated organizations.</div>
          <div className="plan-price flex items-baseline">
            <span className="price-amount text-primary">Custom</span>
          </div>
          <Link to="/signup" className="btn btn-outline btn-block mt-4 mb-8">Contact sales</Link>
          
          <ul className="plan-features">
            <li><Check size={16} color="#10b981" /> SSO & SAML</li>
            <li><Check size={16} color="#10b981" /> Dedicated tenant</li>
            <li><Check size={16} color="#10b981" /> Unlimited seats</li>
            <li><Check size={16} color="#10b981" /> SLA & DPA</li>
            <li><Check size={16} color="#10b981" /> Custom integrations</li>
          </ul>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
