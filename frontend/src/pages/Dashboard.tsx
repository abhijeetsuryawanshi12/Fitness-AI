import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  Target, 
  Droplets, 
  Moon, 
  Dumbbell, 
  TrendingUp, 
  CheckCircle2, 
  MessageSquare, 
  Award,
  Users,
  Heart,
  Flame,
  Brain,
  Clock // Added Clock icon
} from 'lucide-react'

// Mock API - unchanged
const api = {
  get: (endpoint) => {
    const mockData = {
      '/profile/me': { data: { name: 'Abhijeet', email: 'abhijeet@example.com', streak: 12 } },
      '/tasks/today': { data: Array.from({ length: 6 }, (_, i) => ({ id: i, title: `Task ${i + 1}`, completed: i < 3 })) },
      '/': { data: { message: 'Online' } }
    }
    return Promise.resolve(mockData[endpoint] || { data: {} })
  }
}

// Variants - unchanged
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

// Animated Counter Component - unchanged
function AnimatedCounter({ value, duration = 1000 }) {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    let start = 0
    const end = parseInt(value, 10)
    if (start === end) {
      setCount(value);
      return;
    }
    
    let totalMilSecDur = parseInt(duration, 10)
    let incrementTime = Math.max(1, totalMilSecDur / Math.abs(end - start))
    
    let timer = setInterval(() => {
      start += 1
      setCount(String(start))
      if (start >= end) {
          setCount(String(end));
          clearInterval(timer);
      }
    }, incrementTime)
    
    return () => clearInterval(timer)
  }, [value, duration])
  
  return <span>{count}</span>
}


// Progress Ring Component - Themed for dark background
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
          stroke="rgba(255, 255, 255, 0.1)" // Dark theme track
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
        <span className="text-2xl font-bold text-white">{progress}%</span>
      </div>
    </div>
  )
}

// Metric Card Component - ** COMPLETELY RESTYLED **
function MetricCard({ icon: Icon, title, value, unit, color, progress }) {
  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.02, y: -4 }}
      className="bg-slate-800/50 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden"
    >
      {/* Colored Header Section */}
      <div className={`p-4 bg-gradient-to-r ${color} flex items-center justify-between`}>
        <Icon className="w-7 h-7 text-white" />
        <TrendingUp className="w-5 h-5 text-white/70" />
      </div>
      
      {/* Card Body */}
      <div className="p-4 space-y-3">
        <div>
          <div className="flex items-baseline space-x-2">
            <motion.span 
              className="text-3xl font-bold text-white"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <AnimatedCounter value={value} />
            </motion.span>
            {unit && <span className="text-slate-300 font-medium">{unit}</span>}
          </div>
          <p className="text-slate-400 text-sm">{title}</p>
        </div>
        
        {progress !== undefined && (
          <div>
            <div className="w-full bg-white/10 rounded-full h-1.5">
              <motion.div
                className={`h-1.5 rounded-full bg-gradient-to-r ${color}`}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 1.5, delay: 0.5, ease: "easeInOut" }}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// General Card Component for consistent styling
function ThemedCard({ children, className = '' }) {
    return (
        <motion.div
            variants={itemVariants}
            className={`bg-slate-800/50 backdrop-blur-md border border-white/10 rounded-2xl p-6 ${className}`}
        >
            {children}
        </motion.div>
    );
}


// AI Chat Panel - Styled with ThemedCard
function AIChatPanel() {
  const [messages, setMessages] = useState([
    { type: 'ai', content: "Good morning! Ready for today's workout? I've prepared a custom plan based on your progress." },
    { type: 'suggestion', content: 'Suggested workout: Upper Body Strength (45 min)', action: 'View Plan' }
  ])

  return (
    <ThemedCard>
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-white">AI Fitness Coach</h3>
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
                ? 'bg-white/5 text-slate-200' 
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
          className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all"
        >
          <MessageSquare className="w-4 h-4" />
        </motion.button>
      </div>
    </ThemedCard>
  )
}

// Task Tracker - Styled with ThemedCard
function TaskTracker({ tasks }) {
  const completedTasks = tasks?.filter(task => task.completed).length || 0
  const totalTasks = tasks?.length || 0
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <ThemedCard className="h-full">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Today's Tasks</h3>
        <div className="text-sm text-slate-400">{completedTasks}/{totalTasks}</div>
      </div>
      
      <div className="flex items-center justify-center mb-6">
        <ProgressRing progress={Math.round(progress)} size={100} color="rgb(34, 197, 94)" />
      </div>
      
      <div className="space-y-3">
        {tasks?.slice(0, 4).map((task, idx) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`flex items-center space-x-3 p-3 rounded-xl transition-all ${
              task.completed ? 'bg-green-500/20' : 'bg-white/5 hover:bg-white/10'
            }`}
          >
            <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
              <CheckCircle2 className={`w-5 h-5 ${task.completed ? 'text-green-400' : 'text-slate-600'}`} />
            </motion.div>
            <span className={`flex-1 text-sm ${task.completed ? 'text-green-300 line-through' : 'text-slate-300'}`}>
              {task.title}
            </span>
          </motion.div>
        ))}
      </div>
    </ThemedCard>
  )
}

// Achievement Badge - Styled for dark theme
function AchievementBadge({ icon: Icon, title, description, unlocked = false }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, rotate: unlocked ? [0, -2, 2, 0] : 0 }}
      className={`p-4 rounded-xl border-2 transition-all ${
        unlocked 
          ? 'border-yellow-400/50 bg-yellow-500/10' 
          : 'border-white/20 bg-slate-800/50'
      }`}
    >
      <div className={`p-2 rounded-lg inline-block mb-2 ${
        unlocked ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-slate-700'
      }`}>
        <Icon className={`w-4 h-4 ${unlocked ? 'text-white' : 'text-slate-400'}`} />
      </div>
      <h4 className={`text-sm font-semibold mb-1 ${unlocked ? 'text-white' : 'text-slate-400'}`}>
        {title}
      </h4>
      <p className={`text-xs ${unlocked ? 'text-slate-300' : 'text-slate-500'}`}>
        {description}
      </p>
    </motion.div>
  )
}

// ServerStatus - Styled for dark theme
function ServerStatus() {
  const [status, setStatus] = useState('Connecting...')
  const [isOnline, setIsOnline] = useState(false)
  
  useEffect(() => {
    api.get('/').then(r => {
      setStatus(r.data?.message || 'Online')
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
        className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-500'}`}
      />
      <span className="text-sm text-slate-300">{status}</span>
    </div>
  )
}

export default function Dashboard() {
  const [userData, setUserData] = useState({ name: '', streak: 0, tasks: [] })
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
      } catch (error) { console.error('Failed to load dashboard data:', error) } 
      finally { setLoading(false) }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full"
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
      <ThemedCard>
        <div className="relative z-10">
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-4xl font-bold mb-2 text-white"
          >
            Welcome back{userData.name ? `, ${userData.name}` : ''}! 🎯
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-slate-300 text-lg mb-6"
          >
            You're crushing your fitness goals! Keep up the momentum.
          </motion.p>
          
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Flame className="w-6 h-6 text-orange-400" />
              <span className="text-2xl font-bold text-white">{userData.streak}</span>
              <span className="text-slate-300">day streak</span>
            </div>
            <ServerStatus />
          </div>
        </div>
      </ThemedCard>

      {/* Key Metrics */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <Activity className="w-6 h-6 mr-3 text-blue-400" />
          Today's Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            icon={Target}
            title="Calories Burned"
            value={12500}
            unit="kcal"
            color="from-red-500 to-orange-600"
            progress={68}
          />
          <MetricCard
            icon={Dumbbell}
            title="Total Workouts"
            value={48}
            unit="workouts"
            color="from-blue-500 to-sky-600"
            progress={85}
          />
          <MetricCard
            icon={Clock}
            title="Hours Trained"
            value={72}
            unit="hours"
            color="from-purple-500 to-indigo-600"
            progress={75}
          />
          <MetricCard
            icon={Flame}
            title="Current Streak"
            value={12}
            unit="days"
            color="from-green-500 to-emerald-600"
            progress={100}
          />
        </div>
      </motion.div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <AIChatPanel />
        </div>
        <div>
          <TaskTracker tasks={userData.tasks} />
        </div>
      </div>

      {/* Progress Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ThemedCard>
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
            Weight Progress
          </h3>
          <div className="h-48 bg-green-900/20 rounded-xl flex items-center justify-center">
            <div className="text-center text-slate-400">
              <TrendingUp className="w-12 h-12 mx-auto mb-2 text-green-400" />
              <p>Chart visualization here</p>
            </div>
          </div>
        </ThemedCard>

        <ThemedCard>
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Heart className="w-5 h-5 mr-2 text-red-400" />
            Heart Rate Zones
          </h3>
          <div className="h-48 bg-red-900/20 rounded-xl flex items-center justify-center">
            <div className="text-center text-slate-400">
              <Heart className="w-12 h-12 mx-auto mb-2 text-red-400" />
              <p>Heart rate data visualization</p>
            </div>
          </div>
        </ThemedCard>
      </div>

      {/* Achievements */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <Award className="w-6 h-6 mr-3 text-yellow-400" />
          Recent Achievements
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AchievementBadge icon={Flame} title="7-Day Streak" description="Completed 7 days in a row" unlocked={true} />
          <AchievementBadge icon={Dumbbell} title="Strength Hero" description="100 workouts completed" unlocked={true} />
          <AchievementBadge icon={Droplets} title="Hydration Master" description="Perfect hydration week" unlocked={false} />
          <AchievementBadge icon={Users} title="Community Star" description="Top 10% this month" unlocked={false} />
        </div>
      </motion.div>
    </motion.div>
  )
}