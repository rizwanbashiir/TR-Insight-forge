import React from 'react';
import './TrustedBy.css';

const TrustedBy = () => {
  return (
    <section className="trusted-by container">
      <p className="trusted-title">TRUSTED BY DATA TEAMS AT FAST-GROWING COMPANIES</p>
      <div className="trusted-logos flex items-center justify-between">
        <span className="logo-placeholder">NORTHWIND</span>
        <span className="logo-placeholder">ACME CO</span>
        <span className="logo-placeholder">LUMEN</span>
        <span className="logo-placeholder">HELIX</span>
        <span className="logo-placeholder">VANTAGE</span>
        <span className="logo-placeholder">AURORA</span>
      </div>
    </section>
  );
};

export default TrustedBy;
