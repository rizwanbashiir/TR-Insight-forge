import React from 'react';
import { TrendingUp, Users, MessageSquare, Building2 } from 'lucide-react';
import './Features.css';

const Features = () => {
  return (
    <section className="features container" id="features">
      <div className="features-header text-center flex flex-col items-center">
        <span className="section-label">PLATFORM</span>
        <h2 className="section-title">
          Everything your team needs to<br/>
          <span className="text-blue">decide with data</span>
        </h2>
        <p className="section-subtitle">
          From ingestion to forecasting to natural-language analysis — one unified workspace.
        </p>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon flex items-center justify-center">
            <TrendingUp size={24} color="var(--primary-blue)" />
          </div>
          <h3 className="feature-title">AI Forecasting</h3>
          <p className="feature-desc">
            Predict future sales trends with advanced time-series models. Confidence intervals and accuracy scoring built-in.
          </p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon flex items-center justify-center">
            <Users size={24} color="var(--primary-blue)" />
          </div>
          <h3 className="feature-title">Customer Intelligence</h3>
          <p className="feature-desc">
            RFM segmentation surfaces Champions, Loyal, At-Risk, and Growth Opportunity cohorts automatically.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon flex items-center justify-center">
            <MessageSquare size={24} color="var(--primary-blue)" />
          </div>
          <h3 className="feature-title">AI Data Assistant</h3>
          <p className="feature-desc">
            Ask questions in natural language and get instant insights backed by your live dataset context.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon flex items-center justify-center">
            <Building2 size={24} color="var(--primary-blue)" />
          </div>
          <h3 className="feature-title">Multi-Tenant Workspaces</h3>
          <p className="feature-desc">
            Isolated data, role-based access, and SOC-grade controls for every organization on the platform.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Features;
