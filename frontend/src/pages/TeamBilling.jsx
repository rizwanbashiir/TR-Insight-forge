import React from 'react'
import { Plus, CreditCard, Shield, MoreHorizontal } from 'lucide-react'

const teamMembers = [
  { name: 'Ada Lovelace', email: 'ada@acme.com', initials: 'AL', role: 'Admin', status: 'Active' },
  { name: 'Grace Hopper', email: 'grace@acme.com', initials: 'GH', role: 'Analyst', status: 'Active' },
  { name: 'Alan Turing', email: 'alan@acme.com', initials: 'AT', role: 'Analyst', status: 'Active' },
  { name: 'Tim Berners-Lee', email: 'tim@acme.com', initials: 'TB', role: 'Viewer', status: 'Active' },
]

const TeamBilling = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-header">Team & Billing</h1>
          <p className="page-subheader">Manage your workspace, members, and subscription.</p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          Invite member
        </button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Plan Card */}
        <div className="lg:col-span-2 card p-6 bg-gradient-to-br from-slate-50 to-blue-50">
          <div className="flex items-start justify-between mb-6">
            <div>
              <span className="badge-blue mb-2 inline-block">Current plan</span>
              <h3 className="text-3xl font-bold text-slate-900 mt-2">Growth</h3>
              <p className="text-sm text-slate-500 mt-1">Renews on November 12, 2026 · $49/seat/mo</p>
            </div>
            <button className="btn-secondary text-sm">Manage subscription</button>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 uppercase">Seats Used</p>
              <p className="text-xl font-bold text-slate-900 mt-1">4 / 5</p>
              <div className="progress-bar mt-2">
                <div className="progress-bar-fill" style={{ width: '80%' }} />
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 uppercase">API Quota</p>
              <p className="text-xl font-bold text-slate-900 mt-1">682K / 1M</p>
              <div className="progress-bar mt-2">
                <div className="progress-bar-fill" style={{ width: '68%' }} />
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 uppercase">Storage</p>
              <p className="text-xl font-bold text-slate-900 mt-1">12.4 / 50 GB</p>
              <div className="progress-bar mt-2">
                <div className="progress-bar-fill" style={{ width: '25%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Payment Method */}
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <CreditCard className="w-5 h-5 text-slate-500" />
            <h3 className="text-base font-semibold text-slate-900">Payment method</h3>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <p className="text-sm font-semibold text-slate-900">•••• 4242</p>
              <p className="text-xs text-slate-500">Visa · Expires 04/28</p>
            </div>
            <span className="badge-green">Active</span>
          </div>
          <button className="btn-secondary w-full mt-3 text-sm">Update card</button>
          <div className="flex items-center gap-2 mt-3 text-xs text-slate-500">
            <Shield className="w-3 h-3" />
            Secured by Stripe · PCI DSS Level 1
          </div>
        </div>
      </div>

      {/* Team Members Table */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-base font-semibold text-slate-900">Team members</h3>
          <span className="text-sm text-slate-500">4 members</span>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Member</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 w-10"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {teamMembers.map((member) => (
              <tr key={member.email} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
                      {member.initials}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{member.name}</p>
                      <p className="text-xs text-slate-500">{member.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="badge-blue">{member.role}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="badge-green flex items-center gap-1 w-fit">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    {member.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="text-slate-400 hover:text-slate-600">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TeamBilling
