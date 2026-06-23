import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import HeroSection from '../components/landing/HeroSection'
import LogoCloud from '../components/landing/LogoCloud'
import FeaturesSection from '../components/landing/FeaturesSection'
import AIChatDemo from '../components/landing/AIChatDemo'
import PricingSection from '../components/landing/PricingSection'
import CTASection from '../components/landing/CTASection'
import LandingFooter from '../components/landing/LandingFooter'
import Footer from '../components/layout/Footer'

const Home = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href="#top" className="flex items-center gap-2">
  <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
    <Sparkles className="w-4 h-4 text-white" />
  </div>
  <div>
    <span className="font-bold text-slate-900">TR-Insight-Forge</span>
    <span className="block text-[10px] text-slate-500 -mt-1">AI BI PLATFORM</span>
  </div>
</a>
          <div className="hidden md:flex items-center gap-8">
  <a href="#features" className="text-sm text-slate-600 hover:text-slate-900">
    Features
  </a>

  <a href="#demo" className="text-sm text-slate-600 hover:text-slate-900">
    Demo
  </a>

  <a href="#pricing" className="text-sm text-slate-600 hover:text-slate-900">
    Pricing
  </a>

  <a href="#contact" className="text-sm text-slate-600 hover:text-slate-900">
    Contact
  </a>
</div>
          <div className="flex items-center gap-3">
            <Link to="/signin" className="hidden sm:block text-sm text-slate-600 hover:text-slate-900">Sign in</Link>
            <Link to="/signup" className="btn-primary text-sm">Start free trial</Link>
          </div>
        </div>
      </nav>

      <main>
        <HeroSection />
        <LogoCloud />
        <section id="features">
  <FeaturesSection />
</section>
        <section id="demo">
  <AIChatDemo />
</section>
        <section id="pricing">
  <PricingSection />
</section>
        <CTASection />
      </main>

      {/* <LandingFooter /> */}
      <Footer />
    </div>
  )
}

export default Home
