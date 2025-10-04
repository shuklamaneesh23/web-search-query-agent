import { useState } from 'react'
import handleSubmit from './utils/handlesubmit.js';
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

        {answer && (
          <div className="mt-4">
            <div className="max-w-2xl mx-auto bg-gradient-to-br from-gray-50 to-white border border-gray-200 p-5 md:p-6 rounded-xl shadow-sm">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <span className="bg-indigo-100 text-indigo-800 p-2 rounded-lg">📄</span>
                <span>Summary</span>
              </h2>
              <div className="prose prose-indigo max-w-none text-gray-700 overflow-y-auto max-h-[60vh]">
                {answer.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-3 last:mb-0">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}