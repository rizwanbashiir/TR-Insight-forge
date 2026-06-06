import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import './Header.css';

const Header = () => {
  return (
    <header className="header container">
      <div className="header-logo flex items-center gap-2">
        <div className="logo-icon flex items-center justify-center">
          <Sparkles size={20} color="white" />
        </div>
        <div className="logo-text flex flex-col">
          <span className="brand-name">TR-Insight-Forge</span>
          <span className="brand-subtitle">AI BI PLATFORM</span>
        </div>
      </div>

      <nav className="header-nav">
        <a href="#features">Features</a>
        <a href="#pricing">Pricing</a>
        <Link to="/login">Sign in</Link>
      </nav>

      <div className="header-actions flex items-center gap-4">
        <Link to="/login" className="action-link">Sign in</Link>
        <Link to="/signup" className="btn btn-primary">Start free trial</Link>
      </div>
    </header>
  );
};

export default Header;
