import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, BarChart3 } from 'lucide-react'

const CTASection = () => {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="gradient-blue rounded-3xl p-12 text-center text-white">
          <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-4xl font-bold mb-4">Decisions, accelerated.</h2>
          <p className="text-lg text-white/80 mb-8 max-w-xl mx-auto">
            Join the teams replacing spreadsheets with an AI-native BI workspace.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/signup" className="px-6 py-3 bg-white text-primary-600 font-medium rounded-lg hover:bg-white/90 transition-colors">
              Start free trial
            </Link>
            <Link to="/signin" className="px-6 py-3 bg-white/10 text-white font-medium rounded-lg border border-white/20 hover:bg-white/20 transition-colors flex items-center gap-2">
              Live demo
              <BarChart3 className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

export default CTASection
