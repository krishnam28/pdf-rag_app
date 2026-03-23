import { useState } from 'react'
import UploadScreen from './components/UploadScreen'
import ChatScreen from './components/ChatScreen'

export default function App() {
  const [docId, setDocId] = useState(null)
  const [filename, setFilename] = useState('')
  const [fileUrl, setFileUrl] = useState(null)

  function handleUpload(id, name, file) {
    setDocId(id)
    setFilename(name)
    setFileUrl(URL.createObjectURL(file))
  }

  function handleReset() {
    if (fileUrl) URL.revokeObjectURL(fileUrl)
    setDocId(null)
    setFilename('')
    setFileUrl(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {!docId
        ? <UploadScreen onUpload={handleUpload} />
        : <ChatScreen docId={docId} filename={filename} fileUrl={fileUrl} onReset={handleReset} />
      }
    </div>
  )
}