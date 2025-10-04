import { useState } from 'react'
import handleSubmit from './utils/handlesubmit.js';

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
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-4 bg-indigo-600 hover:bg-indigo-700 transition-all text-white font-semibold rounded-xl shadow-md text-base flex items-center justify-center disabled:opacity-80"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Thinking...
              </>
            ) : 'Submit'}
          </button>
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