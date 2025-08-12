import { useEffect, useState } from 'react'
import { 
  Calendar, 
  Download, 
  TrendingUp, 
  Activity, 
  Clock, 
  Flame, 
  Target, 
  Award, 
  Zap,
  User,
  Scale,
  BarChart3,
  PieChart,
  Trophy,
  Share2,
  Filter,
  ChevronDown,
  Star,
  Camera
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell } from 'recharts'

type Summary = { 
  total_calories: number
  total_protein_g: number 
  total_carbs_g: number 
}

type ProgressData = {
  summary: Summary
  workoutStats: {
    totalWorkouts: number
    totalHours: number
    caloriesBurned: number
    currentStreak: number
    longestStreak: number
  }
  bodyMetrics: {
    currentWeight: number
    weightChange: number
    bodyFat?: number
    weightHistory: Array<{ date: string; weight: number }>
  }
  workoutTrends: Array<{ date: string; workouts: number; hours: number }>
  strengthProgress: Array<{ exercise: string; current: number; previous: number }>
  nutritionTrends: Array<{ date: string; calories: number; target: number; protein: number; carbs: number; fat: number }>
  achievements: Array<{ id: string; title: string; description: string; unlocked: boolean; date?: string }>
}

// Mock data generator
const generateMockData = (period: string): ProgressData => {
  const workoutTrends = Array.from({ length: 12 }, (_, i) => ({
    date: new Date(Date.now() - (11 - i) * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    workouts: Math.floor(Math.random() * 6) + 2,
    hours: Math.floor(Math.random() * 8) + 3
  }))

  const weightHistory = Array.from({ length: 8 }, (_, i) => ({
    date: new Date(Date.now() - (7 - i) * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    weight: 180 - (i * 0.5) + (Math.random() * 2 - 1)
  }))

  const nutritionTrends = Array.from({ length: 7 }, (_, i) => ({
    date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    calories: Math.floor(Math.random() * 500) + 1800,
    target: 2000,
    protein: Math.floor(Math.random() * 50) + 120,
    carbs: Math.floor(Math.random() * 100) + 200,
    fat: Math.floor(Math.random() * 30) + 60
  }))

  return {
    summary: {
      total_calories: 1850,
      total_protein_g: 125,
      total_carbs_g: 230
    },
    workoutStats: {
      totalWorkouts: 48,
      totalHours: 72,
      caloriesBurned: 12500,
      currentStreak: 12,
      longestStreak: 21
    },
    bodyMetrics: {
      currentWeight: 176.5,
      weightChange: -3.5,
      bodyFat: 14.2,
      weightHistory
    },
    workoutTrends,
    strengthProgress: [
      { exercise: 'Bench Press', current: 185, previous: 175 },
      { exercise: 'Squat', current: 225, previous: 210 },
      { exercise: 'Deadlift', current: 275, previous: 260 },
      { exercise: 'Overhead Press', current: 135, previous: 125 }
    ],
    nutritionTrends,
    achievements: [
      { id: '1', title: 'First Week', description: 'Complete your first week of workouts', unlocked: true, date: '2024-07-15' },
      { id: '2', title: 'Consistency King', description: '10 day workout streak', unlocked: true, date: '2024-08-01' },
      { id: '3', title: 'Strength Gains', description: 'Increase bench press by 10 lbs', unlocked: true, date: '2024-08-05' },
      { id: '4', title: 'Marathon Runner', description: '100 total workouts', unlocked: false },
      { id: '5', title: 'Nutrition Master', description: 'Track macros for 30 days', unlocked: false }
    ]
  }
}

const CounterAnimation = ({ end, duration = 2000, suffix = '' }: { end: number; duration?: number; suffix?: string }) => {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let start = 0
    const increment = end / (duration / 16)
    const timer = setInterval(() => {
      start += increment
      if (start >= end) {
        setCount(end)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, 16)

    return () => clearInterval(timer)
  }, [end, duration])

  return <span>{count.toLocaleString()}{suffix}</span>
}

export default function FitnessProgress() {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly')
  const [data, setData] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(false)
  const [dateRange, setDateRange] = useState('This Week')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedMetric, setSelectedMetric] = useState('workouts')

  const load = async (p = period) => {
    setLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800))
    const mockData = generateMockData(p)
    setData(mockData)
    setLoading(false)
  }

  useEffect(() => {
    load()
  }, [])

  const handlePeriodChange = (newPeriod: typeof period) => {
    setPeriod(newPeriod)
    load(newPeriod)
  }

  const handleExport = () => {
    // Mock export functionality
    alert('Export functionality would download progress report as PDF/CSV')
  }

  const macroData = data ? [
    { name: 'Protein', value: data.summary.total_protein_g, color: '#3B82F6' },
    { name: 'Carbs', value: data.summary.total_carbs_g, color: '#10B981' },
    { name: 'Fat', value: Math.round(data.summary.total_calories * 0.25 / 9), color: '#F59E0B' }
  ] : []

  const workoutCategories = [
    { name: 'Strength', value: 45, color: '#6366F1' },
    { name: 'Cardio', value: 30, color: '#EC4899' },
    { name: 'Mobility', value: 25, color: '#10B981' }
  ]

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading your progress...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">
              My Fitness Journey
            </h1>
            <p className="text-gray-600 mt-2">Track your progress and celebrate your achievements</p>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Date Range Selector */}
            <div className="relative">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm border hover:shadow-md transition-all"
              >
                <Calendar className="w-4 h-4" />
                <span>{dateRange}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {showFilters && (
                <div className="absolute top-full mt-2 right-0 bg-white rounded-xl shadow-lg border p-2 min-w-[150px] z-10">
                  {['Today', 'This Week', 'This Month', 'Last 3 Months', 'Custom Range'].map((range) => (
                    <button
                      key={range}
                      onClick={() => {
                        setDateRange(range)
                        setShowFilters(false)
                      }}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      {range}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Export Button */}
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-600 to-blue-600 text-white rounded-xl hover:from-teal-700 hover:to-blue-700 transition-all transform hover:scale-105 shadow-lg"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Hero Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {data && [
            { title: 'Total Workouts', value: data.workoutStats.totalWorkouts, icon: Activity, color: 'from-blue-500 to-blue-600', suffix: '' },
            { title: 'Hours Trained', value: data.workoutStats.totalHours, icon: Clock, color: 'from-purple-500 to-purple-600', suffix: 'h' },
            { title: 'Calories Burned', value: data.workoutStats.caloriesBurned, icon: Flame, color: 'from-red-500 to-red-600', suffix: '' },
            { title: 'Current Streak', value: data.workoutStats.currentStreak, icon: Target, color: 'from-green-500 to-green-600', suffix: ' days' },
            { title: 'Weight Change', value: Math.abs(data.bodyMetrics.weightChange), icon: Scale, color: 'from-teal-500 to-teal-600', suffix: ' lbs' },
            { title: 'Body Fat', value: data.bodyMetrics.bodyFat || 0, icon: User, color: 'from-indigo-500 to-indigo-600', suffix: '%' }
          ].map((metric, index) => (
            <div key={metric.title} className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden">
              <div className={`bg-gradient-to-r ${metric.color} p-4`}>
                <div className="flex items-center justify-between text-white">
                  <metric.icon className="w-6 h-6" />
                  <Zap className="w-4 h-4 opacity-70" />
                </div>
              </div>
              <div className="p-4">
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  <CounterAnimation end={metric.value} suffix={metric.suffix} />
                </div>
                <div className="text-sm text-gray-600">{metric.title}</div>
                <div className="w-full bg-gray-200 rounded-full h-1 mt-2">
                  <div 
                    className={`bg-gradient-to-r ${metric.color} h-1 rounded-full transition-all duration-1000`}
                    style={{ width: '75%' }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column - Workout Progress */}
          <div className="xl:col-span-2 space-y-6">
            {/* Workout Trends Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Workout Progress</h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedMetric('workouts')}
                    className={`px-3 py-1 rounded-lg text-sm transition-all ${
                      selectedMetric === 'workouts' 
                        ? 'bg-teal-100 text-teal-700' 
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Workouts
                  </button>
                  <button
                    onClick={() => setSelectedMetric('hours')}
                    className={`px-3 py-1 rounded-lg text-sm transition-all ${
                      selectedMetric === 'hours' 
                        ? 'bg-teal-100 text-teal-700' 
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Hours
                  </button>
                </div>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data?.workoutTrends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#6b7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6b7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey={selectedMetric} 
                      stroke="url(#gradient)" 
                      strokeWidth={3}
                      dot={{ fill: '#0d9488', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: '#0d9488' }}
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#0d9488" />
                        <stop offset="100%" stopColor="#3b82f6" />
                      </linearGradient>
                    </defs>
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Strength Progress */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Strength Progress</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.strengthProgress}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="exercise" 
                      stroke="#6b7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6b7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Bar dataKey="previous" fill="#e5e7eb" name="Previous" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="current" fill="url(#barGradient)" name="Current" radius={[4, 4, 0, 0]} />
                    <defs>
                      <linearGradient id="barGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#0d9488" />
                        <stop offset="100%" stopColor="#3b82f6" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Nutrition Trends */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Daily Calorie Trends</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data?.nutritionTrends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#6b7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6b7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="target" 
                      stroke="#e5e7eb" 
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      name="Target"
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="calories" 
                      stroke="#10b981" 
                      strokeWidth={3}
                      name="Consumed"
                      dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: '#10b981' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Right Column - Body Metrics & Additional Info */}
          <div className="space-y-6">
            {/* Body Metrics */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Weight Progress</h2>
              <div className="h-48 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data?.bodyMetrics.weightHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#6b7280"
                      fontSize={10}
                    />
                    <YAxis 
                      stroke="#6b7280" 
                      fontSize={10}
                      domain={['dataMin - 2', 'dataMax + 2']}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="weight" 
                      stroke="#8b5cf6" 
                      strokeWidth={3}
                      dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: '#8b5cf6' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Change:</span>
                <span className={`font-semibold ${data && data.bodyMetrics.weightChange < 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {data?.bodyMetrics.weightChange}lbs
                </span>
              </div>
            </div>

            {/* Macro Breakdown */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Macro Breakdown</h2>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={macroData}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      dataKey="value"
                    >
                      {macroData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2">
                {macroData.map((macro) => (
                  <div key={macro.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: macro.color }}
                      ></div>
                      <span className="text-sm text-gray-600">{macro.name}</span>
                    </div>
                    <span className="text-sm font-semibold">{macro.value}g</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Workout Categories */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Workout Types</h2>
              <div className="space-y-4">
                {workoutCategories.map((category) => (
                  <div key={category.name}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">{category.name}</span>
                      <span className="text-sm font-semibold">{category.value}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full transition-all duration-1000"
                        style={{ 
                          width: `${category.value}%`,
                          backgroundColor: category.color
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Achievements */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Achievements</h2>
                <Trophy className="w-6 h-6 text-yellow-500" />
              </div>
              <div className="space-y-3">
                {data?.achievements.slice(0, 4).map((achievement) => (
                  <div 
                    key={achievement.id} 
                    className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                      achievement.unlocked 
                        ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200' 
                        : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                      achievement.unlocked ? 'bg-yellow-500' : 'bg-gray-300'
                    }`}>
                      {achievement.unlocked ? (
                        <Star className="w-5 h-5 text-white" />
                      ) : (
                        <Award className="w-5 h-5 text-gray-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`font-medium text-sm ${
                        achievement.unlocked ? 'text-gray-900' : 'text-gray-500'
                      }`}>
                        {achievement.title}
                      </div>
                      <div className="text-xs text-gray-500">{achievement.description}</div>
                      {achievement.date && (
                        <div className="text-xs text-yellow-600 mt-1">
                          Unlocked {achievement.date}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Insights */}
            <div className="bg-gradient-to-r from-teal-500 to-blue-500 rounded-xl shadow-sm p-6 text-white">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-6 h-6" />
                <h2 className="text-xl font-semibold">AI Insights</h2>
              </div>
              <p className="text-teal-100 mb-4">
                "You've improved your bench press by 15% in the last 3 months! Keep your protein intake consistent to hit your next strength goal."
              </p>
              <div className="bg-white/20 rounded-lg p-3">
                <div className="text-sm font-medium mb-2">Next Month Goals:</div>
                <ul className="text-sm text-teal-100 space-y-1">
                  <li>• Increase squat by 5-10 lbs</li>
                  <li>• Maintain 12+ day streak</li>
                  <li>• Focus on mobility work</li>
                </ul>
              </div>
            </div>

            {/* Share Progress */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Share Your Progress</h2>
              <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl hover:from-pink-600 hover:to-rose-600 transition-all">
                <Share2 className="w-4 h-4" />
                Share on Social Media
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}