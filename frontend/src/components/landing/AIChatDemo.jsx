import React from 'react'
import { Sparkles } from 'lucide-react'

const AIChatDemo = () => {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-3">
              AI Intelligence Hub
            </p>
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Ask anything. Get the answer, with the chart.
            </h2>
            <p className="text-lg text-slate-500 mb-8">
              Our RAG-powered assistant grounds every response in your live datasets. Stream answers, render tables and charts, and trace the reasoning behind every number.
            </p>
            <ul className="space-y-3">
              {[
                'Active dataset context pills',
                'Markdown, tables, code & syntax highlighting',
                'Streaming responses with citations',
                'Suggested prompts that learn your domain',
              ].map((item) => (
                <li key={item} className="flex items-center gap-3 text-sm text-slate-700">
                  <span className="w-5 h-5 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center text-xs">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="px-3 py-1 bg-slate-100 rounded-full text-xs text-slate-600">orders_2024.csv</span>
              <span className="px-3 py-1 bg-slate-100 rounded-full text-xs text-slate-600">customers.parquet</span>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 mb-4">
              <p className="text-sm text-slate-700">What drove the Q3 revenue spike?</p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-primary-600" />
                <span className="text-sm font-medium text-primary-600">Insight Assistant</span>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">
                Q3 revenue grew <span className="font-semibold">+27.4% YoY</span>. <span className="font-semibold">68%</span> of the lift came from the Enterprise segment, primarily the EMEA region. Top 3 contributing customers: Helix, Aurora, Lumen.
              </p>
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-200">
                <div>
                  <p className="text-xs text-slate-500">YOY</p>
                  <p className="text-sm font-semibold text-slate-900">+27.4%</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Enterprise</p>
                  <p className="text-sm font-semibold text-slate-900">68%</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">EMEA</p>
                  <p className="text-sm font-semibold text-slate-900">+41%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default AIChatDemo
