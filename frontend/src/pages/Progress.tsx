import { useEffect, useState } from 'react'
import api from '@/lib/api'

type Summary = { total_calories: number, total_protein_g: number, total_carbs_g: number }

export default function Progress() {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily')
  const [summary, setSummary] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(false)

  async function load(p = period) {
    setLoading(true)
    const { data } = await api.get(`/progress/me?period=${p}`)
    setSummary(data.summary)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Progress</h1>
      <div className="flex gap-2 items-center">
        <select className="border rounded px-3 py-2" value={period} onChange={e=>{ const p = e.target.value as any; setPeriod(p); load(p) }}>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
        {loading && <span className="text-sm text-gray-500">Loading...</span>}
      </div>
      {summary && (
        <div className="grid md:grid-cols-3 gap-4">
          <Card title="Calories" value={summary.total_calories} />
          <Card title="Protein (g)" value={summary.total_protein_g} />
          <Card title="Carbs (g)" value={summary.total_carbs_g} />
        </div>
      )}
    </div>
  )
}

function Card({ title, value }: { title: string, value: number }) {
  return (
    <div className="p-4 bg-white rounded shadow">
      <div className="text-gray-500 text-sm">{title}</div>
      <div className="text-3xl font-bold">{Math.round(value)}</div>
    </div>
  )
} 