import { useState } from 'react'
import { queryDocument } from '../api'

const TASKS = [
  { value: 'qa',        label: 'Question & Answer' },
  { value: 'summarise', label: 'Summarise' },
  { value: 'extract',   label: 'Extract Action Items' },
  { value: 'explain',   label: 'Explain Simply' },
]

export default function ChatScreen({ docId, filename, fileUrl, onReset }) {
  const [question, setQuestion] = useState('')
  const [task, setTask] = useState('qa')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleQuery() {
    if (!question.trim()) return
    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])
    try {
      const data = await queryDocument(docId, question, task)
      setAnswer(data.answer)
      setSources(data.sources)
    } catch (e) {
      setError('Query failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">

      {/* Left — PDF viewer */}
      <div className="w-1/2 border-r border-gray-200 bg-white flex flex-col">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <p className="text-sm font-medium text-gray-700 truncate">{filename}</p>
          <button onClick={onReset} className="text-xs text-blue-600 hover:underline ml-4 shrink-0">
            Upload new
          </button>
        </div>
        <iframe
          src={fileUrl}
          className="flex-1 w-full"
          title="PDF Viewer"
        />
      </div>

      {/* Right — Chat */}
      <div className="w-1/2 flex flex-col h-screen overflow-y-auto">
        <div className="p-6 flex flex-col gap-4">
          <h1 className="text-lg font-bold text-gray-800">Ask the document</h1>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
            <select
              value={task}
              onChange={e => setTask(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
            >
              {TASKS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>

            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleQuery()}
              placeholder="Ask anything about the document..."
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-300"
            />

            <button
              onClick={handleQuery}
              disabled={!question.trim() || loading}
              className="mt-3 w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          {answer && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">{answer}</p>
              {sources.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {sources.map(p => (
                    <span key={p} className="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full font-medium">
                      Page {p}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

    </div>
  )
}
