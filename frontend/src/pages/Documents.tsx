import { useEffect, useState } from 'react'
import api from '@/lib/api'

type Doc = { _id: string, filename: string, created_at?: string }

export default function Documents() {
  const [docs, setDocs] = useState<Doc[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  async function load() {
    const { data } = await api.get('/documents')
    setDocs(data)
  }

  useEffect(() => { load() }, [])

  async function upload() {
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      await api.post('/documents/upload', form)
      setFile(null)
      await load()
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Documents</h1>
      <div className="flex items-center gap-2">
        <input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0] || null)} />
        <button disabled={!file || uploading} onClick={upload} className="px-4 py-2 bg-blue-600 text-white rounded">{uploading ? 'Uploading...' : 'Upload PDF'}</button>
      </div>
      <ul className="space-y-2">
        {docs.map(d => (
          <li key={d._id} className="bg-white p-3 rounded shadow flex justify-between">
            <div>{d.filename}</div>
            <div className="text-xs text-gray-500">{d.created_at}</div>
          </li>
        ))}
      </ul>
    </div>
  )
} 