import { useEffect, useState } from 'react'
import api from '@/lib/api'

type Task = {
  _id: string
  name: string
  type: 'workout' | 'diet' | string
  completed: boolean
  task_date?: string
}

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    const { data } = await api.get('/tasks/today')
    setTasks(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function toggle(task: Task) {
    await api.put(`/tasks/${task._id}/toggle_completion`)
    await load()
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Today's Tasks</h1>
      <ul className="space-y-2">
        {tasks.map(t => (
          <li key={t._id} className="bg-white p-3 rounded shadow flex items-center justify-between">
            <div>
              <div className="font-semibold">{t.name}</div>
              <div className="text-xs text-gray-500">{t.type}</div>
            </div>
            <button onClick={() => toggle(t)} className={`px-3 py-1 rounded text-sm ${t.completed ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
              {t.completed ? 'Completed' : 'Mark Complete'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
} 