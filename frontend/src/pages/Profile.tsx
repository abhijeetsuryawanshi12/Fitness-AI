import { useEffect, useState } from 'react'
import api from '@/lib/api'

export default function Profile() {
  const [profile, setProfile] = useState<any>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/profile/me').then(({data}) => setProfile(data))
  }, [])

  function set<K extends string>(key: K, value: any) {
    setProfile((p: any) => ({ ...p, [key]: value }))
  }

  async function save() {
    setSaving(true)
    try {
      const update = { name: profile.name, age: profile.age, gender: profile.gender }
      const { data } = await api.put('/profile/me', update)
      setProfile(data)
    } finally {
      setSaving(false)
    }
  }

  if (!profile) return <div>Loading...</div>

  return (
    <div className="max-w-xl space-y-3">
      <h1 className="text-2xl font-bold mb-2">Profile</h1>
      <label className="block">
        <div className="text-sm text-gray-600">Name</div>
        <input className="w-full border rounded px-3 py-2" value={profile.name || ''} onChange={e=>set('name', e.target.value)} />
      </label>
      <label className="block">
        <div className="text-sm text-gray-600">Age</div>
        <input type="number" className="w-full border rounded px-3 py-2" value={profile.age || ''} onChange={e=>set('age', Number(e.target.value))} />
      </label>
      <label className="block">
        <div className="text-sm text-gray-600">Gender</div>
        <input className="w-full border rounded px-3 py-2" value={profile.gender || ''} onChange={e=>set('gender', e.target.value)} />
      </label>
      <button onClick={save} disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded">
        {saving ? 'Saving...' : 'Save'}
      </button>
    </div>
  )
} 