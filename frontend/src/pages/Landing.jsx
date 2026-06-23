import React from 'react';
import Header from '../components/Header';
import Hero from '../components/Hero';
import TrustedBy from '../components/TrustedBy';
import Features from '../components/Features';
import Pricing from '../components/Pricing';
import CTA from '../components/CTA';
import Footer from '../components/layout/Footer';

const Landing = () => {
  return (
    <div className="app-container">
      <Header />
      <main>
        <Hero />
        <TrustedBy />
        <Features />
        <Pricing />
        <CTA />
      </main>
      <Footer />
    </div>
  );
};

export default Landing;
