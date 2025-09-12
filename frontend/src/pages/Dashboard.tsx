import { useEffect, useState } from 'react';
import {
  Activity,
  Target,
  Droplets,
  Dumbbell,
  TrendingUp,
  CheckCircle2, // --- CHANGE START ---: Import new icon for the updated card
  MessageSquare,
  Award,
  Users,
  Heart,
  Flame,
  Brain,
  Clock,
  ChevronDown
} from 'lucide-react';
import api from '@/lib/api';

import Squares from '@/components/react_bits/Squares';
import BlurText from '@/components/react_bits/BlurText';

// --- IMPORT THE NEW MAGICBENTO COMPONENTS ---
import MagicBento, { BentoCard } from '@/components/react_bits/MagicBento';

// --- HELPER COMPONENTS (No changes needed here) ---

// NOTE: We will keep the mock API for other metrics that are not yet available.
const mockMetricsApi = {
  get: (endpoint) => {
    const mockData = {
      '/metrics/calories': {
        data: {
          daily: { value: 2850, progress: 68 },
          weekly: { value: 12500, progress: 75 },
          monthly: { value: 52000, progress: 82 }
        }
      },
      // We are replacing the workouts endpoint, so this is no longer used for that card.
      '/metrics/workouts': {
        data: {
          daily: { value: 1, progress: 100 },
          weekly: { value: 5, progress: 85 },
          monthly: { value: 22, progress: 88 }
        }
      },
      '/metrics/hours': {
        data: {
          daily: { value: 1.5, progress: 75 },
          weekly: { value: 8, progress: 80 },
          monthly: { value: 32, progress: 85 }
        }
      },
      '/metrics/streak': {
        data: {
          daily: { value: 12, progress: 100 },
          weekly: { value: 12, progress: 100 },
          monthly: { value: 12, progress: 100 }
        }
      }
    }
    return Promise.resolve(mockData[endpoint] || { data: {} })
  }
}

// Time period options
const timePeriods = [
  { value: 'daily', label: 'Today', shortLabel: 'Day' },
  { value: 'weekly', label: 'This Week', shortLabel: 'Week' },
  { value: 'monthly', label: 'This Month', shortLabel: 'Month' }
]


// Animated Counter Component
function AnimatedCounter({ value, duration = 1000 }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let start = 0
    const end = parseFloat(value)
    if (start === end) {
      setCount(value);
      return;
    }

    let totalMilSecDur = parseInt(duration, 10)
    let incrementTime = Math.max(1, totalMilSecDur / Math.abs(end - start))

    let timer = setInterval(() => {
      start += end > 10 ? Math.ceil(end / 100) : 0.1
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(parseFloat(start.toFixed(1)));
      }
    }, incrementTime)

    return () => clearInterval(timer)
  }, [value, duration])

  // Display integer if value is a whole number, otherwise one decimal place
  return <span>{Number.isInteger(count) ? count : count.toFixed(0)}</span>
}

// Time Period Dropdown Component
function TimePeriodDropdown({ selectedPeriod, onPeriodChange, className = '' }) {
  const [isOpen, setIsOpen] = useState(false)
  const selectedOption = timePeriods.find(p => p.value === selectedPeriod)

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 px-4 py-2.5 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-white/20 rounded-xl text-white text-sm font-medium transition-all shadow-lg hover:shadow-xl transform hover:scale-102"
      >
        <span>{selectedOption?.label}</span>
        <div className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
          <ChevronDown className="w-4 h-4" />
        </div>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full mt-2 right-0 z-20 bg-slate-800 border border-white/20 rounded-xl shadow-2xl overflow-hidden min-w-40 backdrop-blur-md">
            {timePeriods.map((period) => (
              <button
                key={period.value}
                onClick={() => {
                  onPeriodChange(period.value)
                  setIsOpen(false)
                }}
                className={`w-full px-4 py-3 text-left text-sm transition-colors flex items-center space-x-3 hover:bg-blue-500/20 ${selectedPeriod === period.value
                    ? 'text-blue-300 bg-blue-500/20 border-l-2 border-blue-400'
                    : 'text-white hover:text-blue-300'
                  }`}
              >
                <span className="flex-1">{period.label}</span>
                {selectedPeriod === period.value && (
                  <div className="w-2 h-2 bg-blue-400 rounded-full" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// Progress Ring Component
function ProgressRing({ progress, size = 120, strokeWidth = 8, color = "rgb(59, 130, 246)" }) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: 'stroke-dashoffset 1.5s ease-out'
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-white">{progress}%</span>
      </div>
    </div>
  )
}

// ServerStatus
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
      <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`} />
      <span className="text-sm text-slate-300">{status}</span>
    </div>
  )
}

// --- UPDATED COMPONENTS TO USE BENTOCARD ---

// Metric Card Component (Now provides only the inner content)
function MetricCard({ icon: Icon, title, value, unit, color, progress, loading }) {
  return (
    <div className="flex flex-col h-full group"> {/* Added group for hover effects */}
      <div className={`p-4 bg-gradient-to-r ${color} relative overflow-hidden rounded-t-xl`}>
        <div className="flex items-center justify-between relative z-10">
          <Icon className="w-7 h-7 text-white" />
          <TrendingUp className="w-5 h-5 text-white/70 group-hover:text-white transition-colors" />
        </div>
        <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, transparent 30%, rgba(255,255,255,0.1) 100%)' }} />
      </div>

      <div className="p-4 space-y-3 flex-grow flex flex-col justify-between">
        <div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-white">
              {loading ? (
                <div className="w-16 h-8 bg-white/10 rounded animate-pulse" />
              ) : (
                <AnimatedCounter value={value} />
              )}
            </span>
            {!loading && unit && (
              <span className="text-slate-300 font-medium">{unit}</span>
            )}
          </div>
          <p className="text-slate-400 text-sm">{title}</p>
        </div>

        {!loading && progress !== undefined && (
          <div>
            <div className="w-full bg-white/10 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full bg-gradient-to-r ${color} transition-all duration-1500 ease-in-out`}
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// AI Chat Panel
function AIChatPanel() {
  const [messages] = useState([
    { type: 'ai', content: "Good morning! Ready for today's workout? I've prepared a custom plan based on your progress." },
    { type: 'suggestion', content: 'Suggested workout: Upper Body Strength (45 min)', action: 'View Plan' }
  ])

  return (
    <>
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-white">AI Fitness Coach</h3>
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
      </div>

      <div className="space-y-3 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-xl text-sm animate-fadeIn ${msg.type === 'ai'
                ? 'bg-white/5 text-slate-200'
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
              }`}
          >
            {msg.content}
            {msg.action && (
              <button className="mt-2 px-3 py-1 bg-white bg-opacity-20 rounded-lg text-xs hover:bg-opacity-30 transition-all transform hover:scale-105">
                {msg.action}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="flex space-x-2">
        <input
          type="text"
          placeholder="Ask your AI coach..."
          className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all transform hover:scale-105">
          <MessageSquare className="w-4 h-4" />
        </button>
      </div>
    </>
  )
}

// Task Tracker
function TaskTracker({ tasks }) {
  const completedTasks = tasks?.filter(task => task.completed).length || 0
  const totalTasks = tasks?.length || 0
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Today's Tasks</h3>
        <div className="text-sm text-slate-400">{completedTasks}/{totalTasks}</div>
      </div>

      <div className="flex items-center justify-center mb-6">
        <ProgressRing progress={Math.round(progress)} size={100} color="rgb(34, 197, 94)" />
      </div>

      <div className="space-y-3">
        {tasks?.slice(0, 4).map((task) => (
          <div
            key={task._id}
            className={`flex items-center space-x-3 p-3 rounded-xl transition-all animate-fadeIn ${task.completed ? 'bg-green-500/20' : 'bg-white/5 hover:bg-white/10'
              }`}
          >
            <div className="transform hover:scale-110 transition-transform">
              <CheckCircle2 className={`w-5 h-5 ${task.completed ? 'text-green-400' : 'text-slate-600'}`} />
            </div>
            <span className={`flex-1 text-sm ${task.completed ? 'text-green-300 line-through' : 'text-slate-300'}`}>
              {task.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Achievement Badge
function AchievementBadge({ icon: Icon, title, description, unlocked = false }) {
  return (
    <div
      className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${unlocked
          ? 'border-yellow-400/50 bg-yellow-500/10 hover:rotate-1'
          : 'border-white/20 bg-slate-800/50'
        }`}
    >
      <div className={`p-2 rounded-lg inline-block mb-2 ${unlocked ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-slate-700'
        }`}>
        <Icon className={`w-4 h-4 ${unlocked ? 'text-white' : 'text-slate-400'}`} />
      </div>
      <h4 className={`text-sm font-semibold mb-1 ${unlocked ? 'text-white' : 'text-slate-400'}`}>
        {title}
      </h4>
      <p className={`text-xs ${unlocked ? 'text-slate-300' : 'text-slate-500'}`}>
        {description}
      </p>
    </div>
  )
}

// Metrics Section Component
function MetricsSection() {
  const [selectedPeriod, setSelectedPeriod] = useState('weekly')
  const [metricsData, setMetricsData] = useState({ calories: {}, workouts: {}, hours: {} })
  const [loading, setLoading] = useState(true)

  // --- CHANGE START ---: This entire useEffect hook is updated to fetch real data
  useEffect(() => {
    async function fetchAllMetrics() {
      setLoading(true)
      try {
        // We will fetch the real progress data and the mock data for other cards concurrently
        const [progressRes, caloriesRes, hoursRes] = await Promise.all([
          // REAL API CALL: Fetch progress data from your backend
          api.get('/progress/me', { params: { period: selectedPeriod } }),
          // MOCK API CALLS: Keep these for now
          mockMetricsApi.get('/metrics/calories'),
          mockMetricsApi.get('/metrics/hours')
        ]);

        // Extract the completion percentage from the real API response
        const completionPercent = progressRes.data.tasks_completion_percent || 0;
        const caloriesBurnt = progressRes.data.summary.total_calories || 0;

        setMetricsData({
          calories: {
            value: caloriesBurnt,
            progress: caloriesRes.data[selectedPeriod]?.progress || 0
          },
          // Use the real data for the 'workouts' card
          workouts: {
            value: Math.round(completionPercent),
            progress: Math.round(completionPercent)
          },
          hours: hoursRes.data[selectedPeriod] || { value: 0, progress: 0 }
        })
      } catch (error) {
        console.error('Failed to load metrics data:', error)
        // Set a default error state so the UI doesn't crash
        setMetricsData({
            calories: { value: 0, progress: 0 },
            workouts: { value: 0, progress: 0 },
            hours: { value: 0, progress: 0 }
        })
      } finally {
        setLoading(false)
      }
    }
    fetchAllMetrics()
  }, [selectedPeriod])
  // --- CHANGE END ---

  return (
    <div className="relative z-20">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
        <h2 className="text-2xl font-bold text-white flex items-center shrink-0">
          <Activity className="w-6 h-6 mr-3 text-blue-400" />
          Performance Overview
        </h2>
        <div className="flex items-center space-x-4 w-full md:w-auto justify-end">
          <span className="text-slate-400 text-sm hidden sm:inline">View data for:</span>
          <TimePeriodDropdown
            selectedPeriod={selectedPeriod}
            onPeriodChange={setSelectedPeriod}
            className="scale-105"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 z-10">
        <BentoCard className="card p-0">
          <MetricCard
            icon={Target}
            title="Calories Burned"
            value={metricsData.calories.value}
            unit="kcal"
            color="from-red-500 to-orange-600"
            progress={metricsData.calories.progress}
            loading={loading}
          />
        </BentoCard>

        {/* --- CHANGE START ---: Update the MetricCard props for the new data */}
        <BentoCard className="card p-0">
          <MetricCard
            icon={CheckCircle2}         // Using a more general icon
            title="Task Completion"     // More accurate title
            value={metricsData.workouts.value}
            unit="%"                    // Unit is now percentage
            color="from-blue-500 to-sky-600"
            progress={metricsData.workouts.progress}
            loading={loading}
          />
        </BentoCard>
        {/* --- CHANGE END --- */}
        
        <BentoCard className="card p-0">
          <MetricCard
            icon={Clock}
            title="Training Time"
            value={metricsData.hours.value}
            unit="hours"
            color="from-purple-500 to-indigo-600"
            progress={metricsData.hours.progress}
            loading={loading}
          />
        </BentoCard>
      </div>
    </div>
  )
}

// --- MAIN DASHBOARD COMPONENT ---
export default function Dashboard() {
  const [userData, setUserData] = useState({ name: '', streak: 0, tasks: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [{ data: me }, { data: tasksData }] = await Promise.all([
          api.get('/profile/me'),
          api.get('/tasks/today')
        ])
        setUserData({
          name: me.name || me.email.split('@')[0],
          streak: me.streak ?? 0,
          tasks: tasksData || []
        })
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Default props for the BentoCard components to avoid repetition
  const bentoCardProps = {
    disableAnimations: loading,
    enableTilt: true,
    enableMagnetism: true,
    clickEffect: true,
    particleCount: 15,
    glowColor: "132, 0, 255",
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="relative min-h-screen bg-slate-900 p-4 md:p-6 lg:p-8 overflow-hidden">
      <div className="absolute inset-0 z-0 opacity-50">
        <Squares speed={0.5} squareSize={40} direction='diagonal' borderColor='#fff' hoverFillColor='#222' />
      </div>
      <div className="absolute inset-0 z-10 bg-gradient-to-br from-slate-900/80 via-purple-900/20 to-slate-900/80" />

      {/* Wrap the entire dashboard content grid in the MagicBento container */}
      <MagicBento
        className="relative z-20 max-w-7xl mx-auto space-y-8 opacity-0 animate-fadeIn"
        enableSpotlight={true}
        enableBorderGlow={true}
        glowColor="132, 0, 255"
      >
        <div className="space-y-8"> {/* Added this div to group children for MagicBento */}
          <BentoCard {...bentoCardProps} className="card relative overflow-hidden p-6 md:p-8">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-indigo-900/20" />
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-full blur-3xl transform translate-x-32 -translate-y-32" />
            <div className="relative z-10">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                <div className="flex-1">
                  <h1 className="text-4xl lg:text-5xl font-bold mb-3 text-white">
                    <BlurText text={`Welcome back, ${userData.name}!`} delay={100} animateBy="words" direction="top" />
                  </h1>
                  <p className="text-slate-300 text-lg mb-6">You're crushing your fitness goals! Keep up the momentum.</p>
                  <ServerStatus />
                </div>
                <div className="flex-shrink-0">
                  <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-3xl p-6 text-center relative overflow-hidden shadow-2xl">
                    <div className="absolute inset-0 bg-white/10 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 25% 25%, transparent 20%, rgba(255,255,255,0.1) 21%, rgba(255,255,255,0.1) 40%, transparent 41%), radial-gradient(circle at 75% 75%, transparent 20%, rgba(255,255,255,0.1) 21%, rgba(255,255,255,0.1) 40%, transparent 41%)' }} />
                    <div className="relative z-10">
                      <div className="w-16 h-16 mx-auto mb-3 animate-spin-slow">
                        <Flame className="w-full h-full text-white drop-shadow-lg" />
                      </div>
                      <div className="text-4xl font-bold text-white mb-1">{userData.streak}</div>
                      <div className="text-orange-100 font-medium text-sm uppercase tracking-wider">Day Streak</div>
                      <div className="mt-2 text-xs text-orange-200 animate-pulse">🔥 On Fire!</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </BentoCard>

          <MetricsSection />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <BentoCard {...bentoCardProps} className="card lg:col-span-2 p-6">
              <AIChatPanel />
            </BentoCard>
            <BentoCard {...bentoCardProps} className="card p-6">
              <TaskTracker tasks={userData.tasks} />
            </BentoCard>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <BentoCard {...bentoCardProps} className="card p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
                Weight Progress
              </h3>
              <div className="h-48 bg-slate-800/50 rounded-xl flex items-center justify-center">
                <div className="text-center text-slate-400">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2 text-green-400" />
                  <p>Chart visualization here</p>
                </div>
              </div>
            </BentoCard>
            
            <BentoCard {...bentoCardProps} className="card p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Heart className="w-5 h-5 mr-2 text-red-400" />
                Heart Rate Zones
              </h3>
              <div className="h-48 bg-slate-800/50 rounded-xl flex items-center justify-center">
                <div className="text-center text-slate-400">
                  <Heart className="w-12 h-12 mx-auto mb-2 text-red-400" />
                  <p>Heart rate data visualization</p>
                </div>
              </div>
            </BentoCard>
          </div>

          <BentoCard {...bentoCardProps} className="card p-6">
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
          </BentoCard>
        </div>
      </MagicBento>
    </div>
  )
}