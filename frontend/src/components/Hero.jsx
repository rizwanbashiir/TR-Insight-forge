import React from 'react';
import { Link } from 'react-router-dom';
import { Check, Activity, Users, Target } from 'lucide-react';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero container">
      <div className="hero-content flex flex-col justify-center">
        <div className="badge">
          <span className="badge-dot"></span>
          Now with GPT-powered Insights Hub
        </div>
        <h1 className="hero-title">
          Transform<br/>
          business data into<br/>
          <span className="text-blue">actionable<br/>intelligence.</span>
        </h1>
        <p className="hero-subtitle">
          Upload datasets, forecast future revenue, identify customer segments, and chat with your data using AI — all in one enterprise-grade workspace.
        </p>
        <div className="hero-actions flex items-center gap-4">
          <Link to="/signup" className="btn btn-primary btn-lg flex items-center gap-2">Start free trial <span style={{fontWeight: 'bold'}}>→</span></Link>
          <button className="btn btn-outline btn-lg">Book demo</button>
        </div>
        <div className="hero-trust flex items-center gap-4">
          <span className="trust-item"><Check size={16} color="#10b981" /> SOC 2 Type II</span>
          <span className="trust-item"><Check size={16} color="#10b981" /> GDPR ready</span>
          <span className="trust-item"><Check size={16} color="#10b981" /> No credit card</span>
        </div>
      </div>

      <div className="hero-visual flex items-center justify-center">
        <div className="dashboard-mock glass-panel flex flex-col gap-4">
          <div className="mock-top flex gap-4">
            <div className="mock-card">
              <div className="flex justify-between items-start mb-2">
                <span className="mock-label">REVENUE</span>
                <Activity size={14} color="#10b981" />
              </div>
              <div className="mock-value">$284K</div>
              <div className="flex items-center gap-1 mt-1 mock-change success">
                <span style={{fontSize: '10px'}}>↗</span> +18.2%
              </div>
            </div>
            <div className="mock-card">
              <div className="flex justify-between items-start mb-2">
                <span className="mock-label">CUSTOMERS</span>
                <Users size={14} color="#3b82f6" />
              </div>
              <div className="mock-value">12,438</div>
              <div className="flex items-center gap-1 mt-1 mock-change success">
                <span style={{fontSize: '10px'}}>↗</span> +4.1%
              </div>
            </div>
            <div className="mock-card">
              <div className="flex justify-between items-start mb-2">
                <span className="mock-label">FORECAST ACC.</span>
                <Target size={14} color="#8b5cf6" />
              </div>
              <div className="mock-value">94.7%</div>
              <div className="flex items-center gap-1 mt-1 mock-change success">
                <span style={{fontSize: '10px'}}>↗</span> +2.3%
              </div>
            </div>
          </div>
          <div className="mock-chart">
            <div className="flex justify-between items-center mb-4">
              <div>
                <div className="mock-chart-title">Revenue forecast</div>
                <div className="mock-chart-subtitle">8-month horizon - 95% CI</div>
              </div>
              <span className="live-badge">Live</span>
            </div>
            <div className="chart-placeholder">
              <svg viewBox="0 0 400 100" className="chart-svg">
                <path d="M 0 80 Q 50 85 100 70 T 200 60 T 300 40 T 400 30" fill="none" stroke="var(--primary-blue)" strokeWidth="3" />
                <path d="M 0 80 Q 50 85 100 70 T 200 60 T 300 40 T 400 30 L 400 100 L 0 100 Z" fill="url(#blue-grad)" opacity="0.2" />
                <defs>
                  <linearGradient id="blue-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--primary-blue)" />
                    <stop offset="100%" stopColor="white" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="chart-labels flex justify-between">
                <span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span><span>Aug</span>
              </div>
            </div>
          </div>
          <div className="mock-insight flex gap-4 items-start">
            <div className="insight-icon"><Sparkles size={16} color="white" /></div>
            <div>
              <div className="insight-title">AI Insight</div>
              <div className="insight-text">Q3 revenue is projected to grow 22% driven by Enterprise segment. 318 at-risk customers detected.</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Internal Sparkles component since it's used inside Hero
const Sparkles = ({size, color}) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
)

export default Hero;
