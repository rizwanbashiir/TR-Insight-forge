import React from 'react';
import { Sparkles } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer container">
      <div className="footer-grid">
        <div className="footer-brand">
          <div className="flex items-center gap-2 mb-4">
            <div className="logo-icon flex items-center justify-center">
              <Sparkles size={20} color="white" />
            </div>
            <span className="brand-name">TR-Insight-Forge</span>
          </div>
          <p className="footer-desc">
            The AI-powered business intelligence platform for modern teams. Forecast, segment, and chat with your data.
          </p>
        </div>

        <div className="footer-links">
          <h4 className="link-title">Product</h4>
          <a href="#">Forecasting</a>
          <a href="#">Segmentation</a>
          <a href="#">AI Assistant</a>
          <a href="#">Integrations</a>
        </div>

        <div className="footer-links">
          <h4 className="link-title">Company</h4>
          <a href="#">About</a>
          <a href="#">Customers</a>
          <a href="#">Security</a>
          <a href="#">Contact</a>
        </div>
      </div>

      <div className="footer-bottom flex justify-between items-center">
        <span className="copyright">&copy; 2026 TR-Insight-Forge, Inc. All rights reserved.</span>
        <div className="legal-links flex gap-4">
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="#">DPA</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
