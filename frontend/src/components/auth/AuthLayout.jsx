import React from 'react';
import { Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import './AuthLayout.css';

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-layout">
      {/* Left Column */}
      <div className="auth-left">
        <div className="auth-logo">
          <Link to="/" className="flex items-center gap-2 text-white">
            <div className="logo-icon bg-white/20 flex items-center justify-center rounded-full w-8 h-8">
              <Sparkles size={20} color="white" />
            </div>
            <span className="font-bold">TR-Insight-Forge</span>
          </Link>
        </div>
        
        <div className="auth-testimonial">
          <blockquote className="testimonial-text">
            "We replaced three BI tools and a data analyst in one quarter."
          </blockquote>
          <div className="testimonial-author">
            <div className="author-name">Maya Tanaka</div>
            <div className="author-role">VP of Analytics, Lumen</div>
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div className="auth-right">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
