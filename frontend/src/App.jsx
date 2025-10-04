import { useState } from 'react'
import handleSubmit from './utils/handlesubmit.js';
import AnswerSummary from './utils/AnswerSummary.jsx';
import CustomButton from './utils/coutomButtom.jsx';

export default function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 to-cyan-100 px-4 py-8">
      <div className="w-full max-w-2xl bg-white shadow-xl rounded-[2rem] p-6 md:p-8 border border-gray-100 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-cyan-600">
            🔍 Web Intelligence Agent
          </h1>
          <p className="text-gray-500 mt-2">Get concise answers to your complex questions</p>
        </div>

        <form onSubmit={(e) => handleSubmit(e, query, setLoading, setAnswer)} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Ask me anything…"
            className="flex-1 p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300 text-base shadow-sm transition-all placeholder:text-gray-400 text-black"
          />
          <CustomButton loading={loading} />
        </form>

        <AnswerSummary answer={answer} />
      </div>
    </div>
  )
}
