import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, BarChart2 } from 'lucide-react';
import './CTA.css';

const CTA = () => {
  return (
    <section className="cta-section container">
      <div className="cta-box flex flex-col items-center text-center">
        <Sparkles size={32} color="white" className="cta-icon" />
        <h2 className="cta-title">Decisions, accelerated.</h2>
        <p className="cta-subtitle">
          Join the teams replacing spreadsheets with an AI-native BI workspace.
        </p>
        <div className="flex gap-4 mt-8">
          <Link to="/signup" className="btn btn-white btn-lg text-primary">Start free trial</Link>
          <button className="btn btn-transparent btn-lg flex items-center gap-2 text-white">
            Live demo <BarChart2 size={18} />
          </button>
        </div>
      </div>
    </section>
  );
};

export default CTA;
