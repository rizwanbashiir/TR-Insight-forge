import React from 'react'

const companies = ['NORTHWIND', 'ACME CO', 'LUMEN', 'HELIX', 'VANTAGE', 'AURORA']

const LogoCloud = () => {
  return (
    <section className="py-12 border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6">
        <p className="text-center text-xs text-slate-400 uppercase tracking-widest mb-8">
          Trusted by data teams at fast-growing companies
        </p>
        <div className="flex items-center justify-center gap-12 flex-wrap">
          {companies.map((company) => (
            <span key={company} className="text-lg font-bold text-slate-300 tracking-wider">
              {company}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}

export default LogoCloud
