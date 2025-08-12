import { useState } from 'react'
import api from '@/lib/api'

export default function Food() {
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function analyze() {
    setLoading(true)
    setError(null)
    try {
      if (file) {
        const form = new FormData()
        form.append('image_file', file)
        const { data } = await api.post('/food/analyze', form)
        setResult(data.analysis)
      } else if (url.trim()) {
        const form = new FormData()
        form.append('image_url', url)
        const { data } = await api.post('/food/analyze', form)
        setResult(data.analysis)
      } else {
        setError('Provide a file or URL')
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to analyze')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-2xl font-bold">Food Analyzer</h1>
      <div className="bg-white p-4 rounded shadow space-y-3">
        <div>
          <div className="text-sm text-gray-600">Upload image</div>
          <input type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0] || null)} />
        </div>
        <div>
          <div className="text-sm text-gray-600">or Image URL</div>
          <input className="w-full border rounded px-3 py-2" placeholder="https://..." value={url} onChange={e=>setUrl(e.target.value)} />
        </div>
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={analyze} disabled={loading}>{loading ? 'Analyzing...' : 'Analyze'}</button>
      </div>
      {result && (
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Result</h2>
          <pre className="whitespace-pre-wrap text-sm">{result}</pre>
        </div>
      )}
    </div>
  )
} 