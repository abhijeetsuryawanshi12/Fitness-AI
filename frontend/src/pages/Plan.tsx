import { useState } from 'react'
import api from '@/lib/api'

export default function Plan() {
  const [type, setType] = useState<'workout' | 'diet' | 'workout and diet'>('workout and diet')
  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function generate(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { data } = await api.post('/plan/generate', { type })
      setPlan(data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to generate plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Generate Plan</h1>
      <form onSubmit={generate} className="flex items-center gap-3 mb-4">
        <select className="border rounded px-3 py-2" value={type} onChange={e=>setType(e.target.value as any)}>
          <option value="workout">Workout</option>
          <option value="diet">Diet</option>
          <option value="workout and diet">Workout and Diet</option>
        </select>
        <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Generating...' : 'Generate'}</button>
      </form>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      {plan && (
        <div className="bg-white p-4 rounded shadow">
          <div className="font-semibold mb-2">Type: {plan.type}</div>
          <pre className="whitespace-pre-wrap text-sm text-gray-700">{JSON.stringify(plan.content, null, 2)}</pre>
        </div>
      )}
    </div>
  )
} 