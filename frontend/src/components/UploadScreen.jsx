import { useState } from 'react'
import { uploadFile } from '../api'

export default function UploadScreen({ onUpload }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      // change only the onUpload call inside handleUpload()
      const data = await uploadFile(file)
      onUpload(data.document_id, data.filename, file)  // pass file as third arg
    } catch (e) {
      setError('Upload failed. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="bg-white rounded-2xl shadow-md p-10 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">PDF RAG App</h1>
        <p className="text-gray-500 mb-8">Upload a PDF or DOCX and ask questions about it</p>

        <label className="block w-full border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition">
          <input
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={e => setFile(e.target.files[0])}
          />
          {file
            ? <p className="text-blue-600 font-medium">{file.name}</p>
            : <p className="text-gray-400">Click to select a PDF or DOCX file</p>
          }
        </label>

        {error && <p className="text-red-500 text-sm mt-3">{error}</p>}

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="mt-6 w-full bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Processing...' : 'Upload and Analyse'}
        </button>
      </div>
    </div>
  )
}