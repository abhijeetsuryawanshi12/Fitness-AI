import { useEffect, useState } from 'react'
import api from '@/lib/api'

export default function Dashboard() {
  const [name, setName] = useState('')
  const [streak, setStreak] = useState<number | null>(null)
  const [tasksCount, setTasksCount] = useState(0)

  useEffect(() => {
    async function load() {
      const [{ data: me }, { data: tasks }] = await Promise.all([
        api.get('/profile/me'),
        api.get('/tasks/today')
      ])
      setName(me.name || me.email)
      setStreak(me.streak ?? 0)
      setTasksCount(tasks?.length || 0)
    }
    load()
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Welcome{ name ? `, ${name}` : '' }</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded shadow">
          <div className="text-gray-500 text-sm">Streak</div>
          <div className="text-3xl font-bold">{streak}</div>
        </div>
        <div className="p-4 bg-white rounded shadow">
          <div className="text-gray-500 text-sm">Today's Tasks</div>
          <div className="text-3xl font-bold">{tasksCount}</div>
        </div>
        <div className="p-4 bg-white rounded shadow">
          <div className="text-gray-500 text-sm">Server</div>
          <ServerStatus />
        </div>
      </div>
    </div>
  )
}

function ServerStatus() {
  const [status, setStatus] = useState('...')
  useEffect(() => {
    api.get('/').then(r => setStatus(r.data?.message || 'OK')).catch(() => setStatus('Down'))
  }, [])
  return <div className="text-xl">{status}</div>
} 