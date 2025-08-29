import { useState } from 'react'
import api from '@/lib/api'
import { setToken } from '@/lib/auth'
import { useNavigate, Link } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const body = new URLSearchParams()
      body.append('username', email)
      body.append('password', password)
      const { data: tokenData } = await api.post('/auth/token', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      setToken(tokenData);

      // After setting the token, the API interceptor will automatically use it for the next call.
      const { data: userProfile } = await api.get('/profile/me');

      // A simple check: if 'age' is not set, the user hasn't completed onboarding.
      if (userProfile && (userProfile.age === null || userProfile.age === undefined)) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }

    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md bg-white/10 backdrop-blur-lg border border-white/20 p-8 rounded-2xl shadow-2xl">
      <h1 className="text-3xl font-bold mb-6 text-center text-white">Welcome Back</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input className="w-full bg-white/5 border border-white/20 rounded-lg p-3 text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input className="w-full bg-white/5 border border-white/20 rounded-lg p-3 text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        {error && <div className="text-red-400 bg-red-500/10 border border-red-500/20 p-3 rounded-lg text-sm">{error}</div>}
        <button disabled={loading} className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 disabled:opacity-50">
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
      <div className="text-sm text-center mt-6 text-slate-300">
        No account? <Link to="/register" className="font-medium text-blue-400 hover:underline">Register</Link>
      </div>
    </div>
  )
}