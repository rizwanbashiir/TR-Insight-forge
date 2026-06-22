import React, { useState } from 'react'
import { Send, Paperclip, Sparkles } from 'lucide-react'

const chatHistory = [
  { id: 1, title: 'Q3 revenue drivers' },
  { id: 2, title: 'Churn risk customers' },
  { id: 3, title: 'EMEA forecast' },
  { id: 4, title: 'Top SKUs August' },
  { id: 5, title: 'Cohort retention' },
]

const sampleMessages = [
  {
    role: 'user',
    content: 'What were the top 3 drivers of revenue growth last quarter?',
  },
  {
    role: 'assistant',
    content: `Q3 revenue grew **+27.4% YoY**, driven by:

1. **Enterprise segment** — contributed 68% of net new revenue
2. **EMEA region expansion** — +41% YoY, fastest-growing region
3. **Multi-year contract conversions** — 14% LTV lift

| Driver | Contribution |
|---|---|
| Enterprise | 68% |
| EMEA | 22% |
| Renewals | 10% |`,
  },
]

const suggestedPrompts = [
  'Analyze monthly sales trends',
  'Forecast next quarter revenue',
  'Identify top customers by LTV',
  'Explain revenue anomalies',
]

const Insights = () => {
  const [message, setMessage] = useState('')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-header">AI Intelligence Hub</h1>
        <p className="page-subheader">Ask anything. Grounded in your live datasets.</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Chat History Sidebar */}
        <div className="card p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Chat History</p>
          <div className="space-y-1">
            {chatHistory.map((chat) => (
              <button
                key={chat.id}
                className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-700 hover:bg-slate-50 transition-colors"
              >
                {chat.title}
              </button>
            ))}
          </div>
          <button className="w-full mt-3 px-3 py-2 text-sm text-slate-500 hover:bg-slate-50 rounded-lg transition-colors">
            + New chat
          </button>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3 card flex flex-col min-h-[600px]">
          {/* Context pills */}
          <div className="px-4 py-3 border-b border-slate-100 flex items-center gap-2">
            <span className="text-sm text-slate-500">Context:</span>
            <span className="px-2 py-1 bg-primary-50 text-primary-600 text-xs rounded-full">orders_2024_q3.csv</span>
            <span className="px-2 py-1 bg-primary-50 text-primary-600 text-xs rounded-full">customers_master.xlsx</span>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {sampleMessages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center mr-3 flex-shrink-0">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-2xl p-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-slate-50 text-slate-900'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">
                    {msg.content}
                  </div>
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center ml-3 flex-shrink-0">
                    <span className="text-xs font-semibold text-slate-600">AL</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Suggested Prompts */}
          <div className="px-4 py-2 flex items-center gap-2 flex-wrap">
            {suggestedPrompts.map((prompt) => (
              <button
                key={prompt}
                className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-full text-xs text-slate-600 hover:bg-slate-100 transition-colors flex items-center gap-1"
              >
                <Sparkles className="w-3 h-3" />
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-100">
            <div className="flex items-center gap-3 bg-slate-50 rounded-xl px-4 py-3">
              <button className="text-slate-400 hover:text-slate-600">
                <Paperclip className="w-5 h-5" />
              </button>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask anything about your data..."
                className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
                onKeyPress={(e) => e.key === 'Enter' && console.log('send')}
              />
              <button className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center hover:bg-primary-700 transition-colors">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Insights
