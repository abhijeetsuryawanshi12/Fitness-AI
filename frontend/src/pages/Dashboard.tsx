import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  Target, 
  Droplets, 
  Moon, 
  Dumbbell, 
  Apple, 
  TrendingUp, 
  CheckCircle2, 
  MessageSquare, 
  Award,
  Users,
  Zap,
  Heart,
  Calendar,
  Clock,
  Flame,
  Brain
} from 'lucide-react'

// Mock API - replace with your actual API calls
const api = {
  get: (endpoint) => {
    const mockData = {
      '/profile/me': { data: { name: 'Alex Johnson', email: 'alex@example.com', streak: 12 } },
      '/tasks/today': { data: Array.from({ length: 6 }, (_, i) => ({ id: i, title: `Task ${i + 1}`, completed: i < 3 })) },
      '/': { data: { message: 'Connected' } }
    }
    return Promise.resolve(mockData[endpoint] || { data: {} })
  }
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.5, ease: "easeOut" }
  }
}

const pulseVariants = {
  pulse: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut"
    }
  }
}

// Animated Counter Component
function AnimatedCounter({ value, duration = 1000 }) {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    let start = 0
    const end = parseInt(value)
    if (start === end) return
    
    let totalMilSecDur = parseInt(duration)
    let incrementTime = (totalMilSecDur / end) * 1000
    
    let timer = setInterval(() => {
      start += 1
      setCount(String(start))
      if (start === end) clearInterval(timer)
    }, incrementTime)
    
    return () => clearInterval(timer)
  }, [value, duration])
  
  return <span>{count}</span>
}

// Progress Ring Component
function ProgressRing({ progress, size = 120, strokeWidth = 8, color = "rgb(59, 130, 246)" }) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgb(229, 231, 235)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-gray-800">{progress}%</span>
      </div>
    </div>
  )
}

// Metric Card Component
function MetricCard({ icon: Icon, title, value, unit, color, progress, trend }) {
  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 relative overflow-hidden group"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-5 group-hover:opacity-10 transition-opacity`} />
      
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl bg-gradient-to-br ${color} shadow-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {trend && (
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${
            trend > 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
          }`}>
            <TrendingUp className={`w-3 h-3 ${trend < 0 ? 'rotate-180' : ''}`} />
            <span>{Math.abs(trend)}%</span>
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <p className="text-gray-500 text-sm font-medium">{title}</p>
        <div className="flex items-baseline space-x-1">
          <motion.span 
            className="text-3xl font-bold text-gray-800"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <AnimatedCounter value={value} />
          </motion.span>
          {unit && <span className="text-gray-500 text-sm">{unit}</span>}
        </div>
        
        {progress !== undefined && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className={`h-2 rounded-full bg-gradient-to-r ${color}`}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 1, delay: 0.5 }}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// AI Chat Panel
function AIChatPanel() {
  const [messages, setMessages] = useState([
    { type: 'ai', content: "Good morning! Ready for today's workout? I've prepared a custom plan based on your progress." },
    { type: 'suggestion', content: 'Suggested workout: Upper Body Strength (45 min)', action: 'View Plan' }
  ])

  return (
    <motion.div
      variants={itemVariants}
      className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 shadow-lg border border-blue-100"
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800">AI Fitness Coach</h3>
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="w-2 h-2 bg-green-400 rounded-full"
        />
      </div>
      
      <div className="space-y-3 mb-4">
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.2 }}
            className={`p-3 rounded-xl text-sm ${
              msg.type === 'ai' 
                ? 'bg-white shadow-sm text-gray-700' 
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
            }`}
          >
            {msg.content}
            {msg.action && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="mt-2 px-3 py-1 bg-white bg-opacity-20 rounded-lg text-xs hover:bg-opacity-30 transition-all"
              >
                {msg.action}
              </motion.button>
            )}
          </motion.div>
        ))}
      </div>
      
      <div className="flex space-x-2">
        <input
          type="text"
          placeholder="Ask your AI coach..."
          className="flex-1 px-4 py-2 bg-white rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all"
        >
          <MessageSquare className="w-4 h-4" />
        </motion.button>
      </div>
    </motion.div>
  )
}

// Task Tracker
function TaskTracker({ tasks }) {
  const completedTasks = tasks?.filter(task => task.completed).length || 0
  const totalTasks = tasks?.length || 0
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <motion.div
      variants={itemVariants}
      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">Today's Tasks</h3>
        <div className="text-sm text-gray-500">{completedTasks}/{totalTasks}</div>
      </div>
      
      <div className="flex items-center justify-center mb-6">
        <ProgressRing progress={Math.round(progress)} size={100} />
      </div>
      
      <div className="space-y-3">
        {tasks?.slice(0, 4).map((task, idx) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`flex items-center space-x-3 p-3 rounded-xl transition-all ${
              task.completed ? 'bg-green-50' : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <CheckCircle2 className={`w-5 h-5 ${
                task.completed ? 'text-green-500' : 'text-gray-300'
              }`} />
            </motion.div>
            <span className={`flex-1 text-sm ${
              task.completed ? 'text-green-700 line-through' : 'text-gray-700'
            }`}>
              {task.title}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

// Achievement Badge
function AchievementBadge({ icon: Icon, title, description, unlocked = false }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, rotate: unlocked ? [0, -5, 5, 0] : 0 }}
      className={`p-4 rounded-xl border-2 transition-all ${
        unlocked 
          ? 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-orange-50' 
          : 'border-gray-200 bg-gray-50'
      }`}
    >
      <div className={`p-2 rounded-lg inline-block mb-2 ${
        unlocked ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-gray-300'
      }`}>
        <Icon className={`w-4 h-4 ${unlocked ? 'text-white' : 'text-gray-500'}`} />
      </div>
      <h4 className={`text-sm font-semibold mb-1 ${unlocked ? 'text-gray-800' : 'text-gray-500'}`}>
        {title}
      </h4>
      <p className={`text-xs ${unlocked ? 'text-gray-600' : 'text-gray-400'}`}>
        {description}
      </p>
    </motion.div>
  )
}

function ServerStatus() {
  const [status, setStatus] = useState('Connecting...')
  const [isOnline, setIsOnline] = useState(false)
  
  useEffect(() => {
    api.get('/').then(r => {
      setStatus(r.data?.message || 'Connected')
      setIsOnline(true)
    }).catch(() => {
      setStatus('Offline')
      setIsOnline(false)
    })
  }, [])

  return (
    <div className="flex items-center space-x-2">
      <motion.div
        animate={isOnline ? { scale: [1, 1.2, 1] } : {}}
        transition={{ repeat: Infinity, duration: 2 }}
        className={`w-3 h-3 rounded-full ${
          isOnline ? 'bg-green-400' : 'bg-red-400'
        }`}
      />
      <span className="text-sm font-medium">{status}</span>
    </div>
  )
}

export default function Dashboard() {
  const [userData, setUserData] = useState({
    name: '',
    streak: 0,
    tasks: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [{ data: me }, { data: tasks }] = await Promise.all([
          api.get('/profile/me'),
          api.get('/tasks/today')
        ])
        setUserData({
          name: me.name || me.email.split('@')[0],
          streak: me.streak ?? 0,
          tasks: tasks || []
        })
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1 }}
          className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Hero Section */}
      <motion.div 
        variants={itemVariants}
        className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 rounded-3xl p-8 text-white overflow-hidden"
      >
        <div className="absolute inset-0 bg-black opacity-10" />
        <motion.div
          animate={{ 
            backgroundPosition: ['0% 0%', '100% 100%'],
            opacity: [0.1, 0.3, 0.1]
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute inset-0 bg-gradient-to-br from-white to-transparent"
        />
        
        <div className="relative z-10">
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-4xl font-bold mb-2"
          >
            Welcome back{userData.name ? `, ${userData.name}` : ''}! 🎯
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-blue-100 text-lg mb-6"
          >
            You're crushing your fitness goals! Keep up the momentum.
          </motion.p>
          
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Flame className="w-6 h-6 text-orange-300" />
              <span className="text-2xl font-bold">{userData.streak}</span>
              <span className="text-blue-100">day streak</span>
            </div>
            <ServerStatus />
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <Activity className="w-6 h-6 mr-2 text-blue-600" />
          Today's Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            icon={Target}
            title="Calories Burned"
            value={850}
            unit="kcal"
            color="from-red-500 to-pink-600"
            progress={68}
            trend={12}
          />
          <MetricCard
            icon={Dumbbell}
            title="Workout Minutes"
            value={45}
            unit="min"
            color="from-blue-500 to-indigo-600"
            progress={75}
            trend={8}
          />
          <MetricCard
            icon={Droplets}
            title="Water Intake"
            value={6}
            unit="glasses"
            color="from-cyan-500 to-blue-600"
            progress={60}
            trend={-5}
          />
          <MetricCard
            icon={Moon}
            title="Sleep Quality"
            value={8.2}
            unit="hrs"
            color="from-indigo-500 to-purple-600"
            progress={82}
            trend={15}
          />
        </div>
      </motion.div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* AI Recommendations */}
        <div className="lg:col-span-2">
          <AIChatPanel />
        </div>

        {/* Tasks */}
        <div>
          <TaskTracker tasks={userData.tasks} />
        </div>
      </div>

      {/* Progress Charts */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Weight Progress
          </h3>
          <div className="h-48 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl flex items-center justify-center">
            <div className="text-center text-gray-600">
              <TrendingUp className="w-12 h-12 mx-auto mb-2 text-green-500" />
              <p>Chart visualization here</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Heart className="w-5 h-5 mr-2 text-red-600" />
            Heart Rate Zones
          </h3>
          <div className="h-48 bg-gradient-to-br from-red-50 to-pink-50 rounded-xl flex items-center justify-center">
            <div className="text-center text-gray-600">
              <Heart className="w-12 h-12 mx-auto mb-2 text-red-500" />
              <p>Heart rate data visualization</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Achievements */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <Award className="w-6 h-6 mr-2 text-yellow-600" />
          Recent Achievements
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AchievementBadge
            icon={Flame}
            title="7-Day Streak"
            description="Completed 7 days in a row"
            unlocked={true}
          />
          <AchievementBadge
            icon={Dumbbell}
            title="Strength Hero"
            description="100 workouts completed"
            unlocked={true}
          />
          <AchievementBadge
            icon={Droplets}
            title="Hydration Master"
            description="Perfect hydration week"
            unlocked={false}
          />
          <AchievementBadge
            icon={Users}
            title="Community Star"
            description="Top 10% this month"
            unlocked={false}
          />
        </div>
      </motion.div>
    </motion.div>
  )
}