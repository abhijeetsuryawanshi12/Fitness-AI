import { useEffect, useState } from 'react'
import { Plus, ChevronLeft, ChevronRight, Search, Filter, Calendar, Clock, Target, Droplets, Utensils, Dumbbell, Moon, Check, X, Edit2, Trash2, Star, Save, Eye, Info, Zap, TrendingUp, Award } from 'lucide-react'
import api from '@/lib/api' // Import the actual API client

// Updated Task type to match the backend model
type Task = {
  _id: string
  name: string
  details?: {
    instructions?: string
    sets?: number
    reps?: number
    weights?: number[]
    [key: string]: any
  }
  type: 'workout' | 'diet' | 'hydration' | 'sleep' | 'habit' | string
  priority: 'high' | 'medium' | 'low'
  completed: boolean
  task_date: string
  time?: string
  performance?: {
    sets: number
    reps: (number | string)[]
    weights: (number | string)[]
  }
}

type TaskFormData = {
  name: string
  description: string
  type: string
  priority: 'high' | 'medium' | 'low'
  task_date: string
  time: string
}

type PerformanceLog = {
  sets: number
  reps: (number | string)[]
  weights: (number | string)[]
}

// --- Task Details Modal Component ---
const TaskDetailsModal = ({ task, onClose, onEdit, onDelete, onToggleCompletion }) => {
  const typeIcons = {
    workout: <Dumbbell className="w-5 h-5" />,
    diet: <Utensils className="w-5 h-5" />,
    hydration: <Droplets className="w-5 h-5" />,
    sleep: <Moon className="w-5 h-5" />,
    habit: <Target className="w-5 h-5" />
  }

  const extractTimeFromTaskDate = (taskDate: string) => {
    try {
      const date = new Date(taskDate)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      })
    } catch (error) {
      return 'No time set'
    }
  }

  const formatTaskDate = (taskDate: string) => {
    try {
      const date = new Date(taskDate)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch (error) {
      return taskDate
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
      <div className="bg-slate-800/95 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-300">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className={`p-4 rounded-2xl transition-all duration-300 ${task.type === 'workout' ? 'bg-gradient-to-br from-blue-500/20 to-blue-600/30 text-blue-400' :
                task.type === 'diet' ? 'bg-gradient-to-br from-green-500/20 to-green-600/30 text-green-400' :
                task.type === 'hydration' ? 'bg-gradient-to-br from-cyan-500/20 to-cyan-600/30 text-cyan-400' :
                task.type === 'sleep' ? 'bg-gradient-to-br from-purple-500/20 to-purple-600/30 text-purple-400' :
                'bg-gradient-to-br from-orange-500/20 to-orange-600/30 text-orange-400'}`}>
                {typeIcons[task.type] || <Target className="w-6 h-6" />}
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{task.name}</h2>
                <div className="flex items-center space-x-6 text-sm text-slate-400">
                  <span className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {formatTaskDate(task.task_date)}
                  </span>
                  <span className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {extractTimeFromTaskDate(task.task_date)}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-3 text-slate-400 hover:bg-white/10 hover:text-white rounded-xl transition-all duration-200 hover:rotate-90"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Status and Priority */}
          <div className="flex items-center space-x-4 mb-8">
            <div className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
              task.completed
                ? 'bg-gradient-to-r from-green-500/20 to-green-600/30 text-green-300 border border-green-500/30'
                : 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/30 text-yellow-300 border border-yellow-500/30'
            }`}>
              <div className={`w-3 h-3 rounded-full animate-pulse ${task.completed ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
              <span className="font-medium">{task.completed ? 'Completed' : 'Pending'}</span>
            </div>
            <div className={`px-4 py-3 rounded-xl font-medium border transition-all duration-300 ${
              task.priority === 'high' ? 'bg-gradient-to-r from-red-500/20 to-red-600/30 text-red-300 border-red-500/30' :
              task.priority === 'medium' ? 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/30 text-yellow-300 border-yellow-500/30' :
              'bg-gradient-to-r from-green-500/20 to-green-600/30 text-green-300 border-green-500/30'
            }`}>
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
            </div>
            <div className="px-4 py-3 rounded-xl font-medium bg-gradient-to-r from-slate-700/50 to-slate-600/50 text-slate-300 border border-slate-600/30">
              {task.type.charAt(0).toUpperCase() + task.type.slice(1)}
            </div>
          </div>

          {/* Content with enhanced styling */}
          <div className="space-y-6 max-h-[50vh] overflow-y-auto pr-2">
            {task.details?.instructions && (
              <div className="bg-gradient-to-br from-white/5 to-white/10 p-6 rounded-2xl border border-white/10 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-3">
                  <Info className="w-5 h-5" />
                  Instructions
                </h3>
                <p className="text-slate-300 leading-relaxed text-lg">{task.details.instructions}</p>
              </div>
            )}

            {task.type === 'workout' && task.details && (
              <div className="bg-gradient-to-br from-white/5 to-white/10 p-6 rounded-2xl border border-white/10 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-3">
                  <Dumbbell className="w-5 h-5" />
                  Workout Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {task.details.sets && (
                    <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/20 p-4 rounded-xl border border-blue-500/20 hover:border-blue-400/40 transition-all duration-300">
                      <div className="text-blue-400 text-sm font-medium mb-1">Sets</div>
                      <div className="text-white text-2xl font-bold">{task.details.sets}</div>
                    </div>
                  )}
                  {task.details.reps && (
                    <div className="bg-gradient-to-br from-green-500/10 to-green-600/20 p-4 rounded-xl border border-green-500/20 hover:border-green-400/40 transition-all duration-300">
                      <div className="text-green-400 text-sm font-medium mb-1">Reps</div>
                      <div className="text-white text-2xl font-bold">{task.details.reps}</div>
                    </div>
                  )}
                  {task.details.weights && task.details.weights.length > 0 && (
                    <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/20 p-4 rounded-xl border border-purple-500/20 hover:border-purple-400/40 transition-all duration-300">
                      <div className="text-purple-400 text-sm font-medium mb-1">Weight (kg)</div>
                      <div className="text-white text-2xl font-bold">
                        {Array.isArray(task.details.weights) ? task.details.weights.join(', ') : task.details.weights}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {task.performance && (
              <div className="bg-gradient-to-br from-white/5 to-white/10 p-6 rounded-2xl border border-white/10 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-3">
                  <Star className="w-5 h-5 text-yellow-400" />
                  Performance Log
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/20">
                        <th className="text-left py-3 text-slate-400 font-semibold">Set</th>
                        <th className="text-left py-3 text-slate-400 font-semibold">Reps</th>
                        <th className="text-left py-3 text-slate-400 font-semibold">Weight (kg)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Array.from({ length: task.performance.sets }).map((_, i) => (
                        <tr key={i} className="border-b border-white/10 hover:bg-white/5 transition-colors duration-200">
                          <td className="py-3 text-white font-semibold">{i + 1}</td>
                          <td className="py-3 text-slate-300">{task.performance.reps[i] || '-'}</td>
                          <td className="py-3 text-slate-300">{task.performance.weights[i] || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between space-x-4 pt-8 border-t border-white/10 mt-8">
            <button
              onClick={() => onToggleCompletion(task)}
              className={`px-8 py-3 rounded-xl transition-all duration-300 flex items-center space-x-3 font-medium transform hover:scale-105 ${
                task.completed
                  ? 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/30 text-yellow-300 border border-yellow-500/30 hover:from-yellow-500/30 hover:to-yellow-600/40'
                  : 'bg-gradient-to-r from-green-500/20 to-green-600/30 text-green-300 border border-green-500/30 hover:from-green-500/30 hover:to-green-600/40'
              }`}
            >
              <Check className="w-5 h-5" />
              <span>{task.completed ? 'Mark Incomplete' : 'Mark Complete'}</span>
            </button>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => onEdit(task)}
                className="px-6 py-3 bg-gradient-to-r from-blue-500/20 to-blue-600/30 text-blue-300 border border-blue-500/30 hover:from-blue-500/30 hover:to-blue-600/40 rounded-xl transition-all duration-300 flex items-center space-x-2 font-medium transform hover:scale-105"
              >
                <Edit2 className="w-4 h-4" />
                <span>Edit</span>
              </button>
              <button
                onClick={() => onDelete(task._id)}
                className="px-6 py-3 bg-gradient-to-r from-red-500/20 to-red-600/30 text-red-300 border border-red-500/30 hover:from-red-500/30 hover:to-red-600/40 rounded-xl transition-all duration-300 flex items-center space-x-2 font-medium transform hover:scale-105"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// --- Performance Log Modal Component ---
const PerformanceLogModal = ({ task, onClose, onSave }) => {
  const plannedSets = task.details?.sets || 1;
  const initialPerformance = task.performance || {
    sets: plannedSets,
    reps: task.details?.reps ? Array(plannedSets).fill(task.details.reps) : Array(plannedSets).fill(''),
    weights: task.details?.weights || Array(plannedSets).fill(''),
  };

  const [performance, setPerformance] = useState<PerformanceLog>(initialPerformance);
  const [saving, setSaving] = useState(false);

  const handleInputChange = (index, field, value) => {
    const newValues = [...performance[field]];
    newValues[index] = value;
    setPerformance(prev => ({ ...prev, [field]: newValues }));
  };

  const handleSave = async () => {
    setSaving(true);
    const processedPerformance = {
      ...performance,
      reps: performance.reps.map(r => r === '' ? '' : Number(r)),
      weights: performance.weights.map(w => w === '' ? '' : Number(w)),
    };
    await onSave(task._id, processedPerformance);
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
      <div className="bg-slate-800/95 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl w-full max-w-lg animate-in zoom-in-95 duration-300">
        <div className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">Log Performance</h2>
              <p className="text-slate-300 mt-1">{task.name}</p>
            </div>
            <button
              onClick={onClose}
              className="p-3 text-slate-400 hover:bg-white/10 hover:text-white rounded-xl transition-all duration-200 hover:rotate-90"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
            <div className="grid grid-cols-4 gap-4 text-sm font-semibold text-slate-400 px-4 py-2 bg-white/5 rounded-xl">
              <span>Set</span>
              <span>Planned</span>
              <span>Reps</span>
              <span>Weight (kg)</span>
            </div>
            {Array.from({ length: performance.sets }).map((_, i) => (
              <div key={i} className="grid grid-cols-4 gap-4 items-center bg-gradient-to-r from-white/5 to-white/10 p-4 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300">
                <div className="font-semibold text-white text-center">{i + 1}</div>
                <div className="text-sm text-slate-400 text-center">
                  {task.details?.reps}r @ {task.details?.weights?.[i] || task.details?.weights?.[0] || 'N/A'}kg
                </div>
                <div>
                  <input
                    type="number"
                    value={performance.reps[i]}
                    onChange={(e) => handleInputChange(i, 'reps', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-center text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    placeholder="0"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    value={performance.weights[i]}
                    onChange={(e) => handleInputChange(i, 'weights', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-center text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    placeholder="0"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-end space-x-4 pt-8 border-t border-white/10 mt-8">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-slate-200 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-all duration-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-xl transition-all duration-300 flex items-center gap-3 font-medium transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save & Complete
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'workout': return <Dumbbell className="w-4 h-4" />
    case 'diet': return <Utensils className="w-4 h-4" />
    case 'hydration': return <Droplets className="w-4 h-4" />
    case 'sleep': return <Moon className="w-4 h-4" />
    default: return <Target className="w-4 h-4" />
  }
}

const getTypeGradient = (type: string) => {
  switch (type) {
    case 'workout': return 'from-blue-500/20 to-blue-600/30 border-blue-500/30 text-blue-300'
    case 'diet': return 'from-green-500/20 to-green-600/30 border-green-500/30 text-green-300'
    case 'hydration': return 'from-cyan-500/20 to-cyan-600/30 border-cyan-500/30 text-cyan-300'
    case 'sleep': return 'from-purple-500/20 to-purple-600/30 border-purple-500/30 text-purple-300'
    case 'habit': return 'from-orange-500/20 to-orange-600/30 border-orange-500/30 text-orange-300'
    default: return 'from-slate-500/20 to-slate-600/30 border-slate-500/30 text-slate-300'
  }
}

const getPriorityGradient = (priority: string) => {
  switch (priority) {
    case 'high': return 'from-red-500/20 to-red-600/30 border-red-500/30 text-red-300'
    case 'medium': return 'from-yellow-500/20 to-yellow-600/30 border-yellow-500/30 text-yellow-300'
    case 'low': return 'from-green-500/20 to-green-600/30 border-green-500/30 text-green-300'
    default: return 'from-slate-500/20 to-slate-600/30 border-slate-500/30 text-slate-300'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  const isToday = date.toDateString() === today.toDateString()
  const isYesterday = date.toDateString() === yesterday.toDateString()
  const isTomorrow = date.toDateString() === tomorrow.toDateString()

  let displayName = ''
  if (isToday) displayName = 'Today'
  else if (isYesterday) displayName = 'Yesterday'
  else if (isTomorrow) displayName = 'Tomorrow'
  else displayName = date.toLocaleDateString('en-US', { weekday: 'long' })

  return {
    dayName: date.toLocaleDateString('en-US', { weekday: 'short', timeZone: 'UTC' }),
    dayNumber: date.getUTCDate(),
    month: date.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' }),
    displayName,
    isToday,
    isYesterday,
    isTomorrow
  }
}

const extractTimeFromTaskDate = (taskDate: string) => {
  try {
    const date = new Date(taskDate)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  } catch (error) {
    return null
  }
}

export default function DailyTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [currentDay, setCurrentDay] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [loggingPerformanceTask, setLoggingPerformanceTask] = useState<Task | null>(null)
  const [viewingTaskDetails, setViewingTaskDetails] = useState<Task | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  const [taskForm, setTaskForm] = useState<TaskFormData>({
    name: '',
    description: '',
    type: 'workout',
    priority: 'medium',
    task_date: '',
    time: ''
  })

  // Generate 3 consecutive days: yesterday, today, tomorrow
  const threeDays = Array.from({ length: 3 }, (_, i) => {
    const date = new Date(currentDay)
    date.setDate(date.getDate() + i - 1) // -1, 0, +1 (yesterday, today, tomorrow)
    return date.toISOString().split('T')[0]
  })

  const loadTasks = async () => {
    setLoading(true)
    try {
      // Load tasks for the 3-day period
      const startDate = threeDays[0]
      const { data } = await api.get('/tasks/week', {
        params: { start_date: startDate }
      })
      // Filter to only include our 3 days
      const filteredTasks = data.filter(task => {
        const taskDate = task.task_date.split('T')[0]
        return threeDays.includes(taskDate)
      })
      setTasks(filteredTasks)
    } catch (error) {
      console.error('Error loading tasks:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadTasks()
  }, [currentDay])

  const getTasksForDay = (date: string) => {
    return tasks.filter(task => {
      const taskDateOnly = task.task_date.split('T')[0]
      const matchesDate = taskDateOnly === date
      const matchesSearch = task.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesType = filterType === 'all' || task.type === filterType
      const matchesStatus = filterStatus === 'all' ||
        (filterStatus === 'completed' && task.completed) ||
        (filterStatus === 'pending' && !task.completed)

      return matchesDate && matchesSearch && matchesType && matchesStatus
    })
  }

  const getDayCompletionPercent = (date: string) => {
    const dayTasks = tasks.filter(task => task.task_date.split('T')[0] === date)
    if (dayTasks.length === 0) return 0
    const completed = dayTasks.filter(task => task.completed).length
    return Math.round((completed / dayTasks.length) * 100)
  }

  const handleCreateTask = async () => {
    if (!taskForm.name.trim() || !taskForm.task_date) return
    const newTaskPayload = {
      name: taskForm.name,
      type: taskForm.type,
      priority: taskForm.priority,
      task_date: taskForm.task_date,
      details: { instructions: taskForm.description },
    }
    try {
      const { data } = await api.post('/tasks/', newTaskPayload)
      setTasks(prev => [...prev, data])
      resetTaskForm()
      setShowTaskModal(false)
    } catch (error) {
      console.error('Error creating task:', error)
    }
  }

  const handleUpdateTask = async () => {
    if (!editingTask || !taskForm.name.trim()) return
    const updatedTaskPayload = {
      name: taskForm.name,
      type: taskForm.type,
      priority: taskForm.priority,
      task_date: taskForm.task_date,
      details: { instructions: taskForm.description },
    }
    try {
      const { data: updatedTask } = await api.put(`/tasks/${editingTask._id}`, updatedTaskPayload)
      setTasks(prev => prev.map(task =>
        task._id === editingTask._id ? updatedTask : task
      ))
      resetTaskForm()
      setEditingTask(null)
      setShowTaskModal(false)
    } catch (error) {
      console.error('Error updating task:', error)
    }
  }

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return
    try {
      await api.delete(`/tasks/${taskId}`)
      setTasks(prev => prev.filter(task => task._id !== taskId))
      if (viewingTaskDetails && viewingTaskDetails._id === taskId) {
        setViewingTaskDetails(null)
      }
    } catch (error) {
      console.error('Error deleting task:', error)
    }
  }

  const handleToggleCompletion = async (task: Task) => {
    if (task.type === 'workout' && !task.completed) {
      setLoggingPerformanceTask(task)
      if (viewingTaskDetails) {
        setViewingTaskDetails(null)
      }
      return
    }

    try {
      const { data: updatedTask } = await api.put(`/tasks/${task._id}/toggle_completion`)
      setTasks(prev => prev.map(t => t._id === task._id ? updatedTask : t))
      if (viewingTaskDetails && viewingTaskDetails._id === task._id) {
        setViewingTaskDetails(updatedTask)
      }
    } catch (error) {
      console.error('Error toggling task:', error)
    }
  }

  const handleSavePerformanceAndComplete = async (taskId: string, performanceData: PerformanceLog) => {
    try {
      const payload = { performance: performanceData }
      const { data: updatedTask } = await api.put(`/tasks/${taskId}/toggle_completion`, payload)

      setTasks(prev => prev.map(t => t._id === taskId ? updatedTask : t))
      setLoggingPerformanceTask(null)
    } catch (error) {
      console.error('Error saving performance data:', error)
    }
  }

  const resetTaskForm = () => {
    setTaskForm({
      name: '',
      description: '',
      type: 'workout',
      priority: 'medium',
      task_date: '',
      time: ''
    })
  }

  const openTaskModal = (task?: Task, date?: string) => {
    if (task) {
      setEditingTask(task)
      setTaskForm({
        name: task.name,
        description: task.details?.instructions || '',
        type: task.type,
        priority: task.priority,
        task_date: task.task_date.split('T')[0],
        time: task.time || ''
      })
    } else {
      setEditingTask(null)
      resetTaskForm()
      setTaskForm(prev => ({ ...prev, task_date: date || new Date().toISOString().split('T')[0] }))
    }
    setShowTaskModal(true)
  }

  const handleTaskClick = (task: Task) => {
    setViewingTaskDetails(task)
  }

  const handleEditFromDetails = (task: Task) => {
    setViewingTaskDetails(null)
    openTaskModal(task)
  }

  const navigateDay = (direction: 'prev' | 'next') => {
    const date = new Date(currentDay)
    date.setDate(date.getDate() + (direction === 'next' ? 1 : -1))
    setCurrentDay(date.toISOString().split('T')[0])
  }

  const totalTasks = tasks.length
  const completedTasks = tasks.filter(task => task.completed).length
  const overallProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  // Get stats for the current view
  const todayTasks = getTasksForDay(threeDays[1])
  const highPriorityTasks = tasks.filter(t => t.priority === 'high' && !t.completed).length
  const streakDays = 7 // This would come from your backend

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center animate-in fade-in duration-500">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500/30 border-t-blue-500 mx-auto mb-6"></div>
            <div className="absolute inset-0 rounded-full h-16 w-16 border-4 border-purple-500/20 border-b-purple-500 mx-auto animate-ping"></div>
          </div>
          <p className="text-slate-300 text-lg font-medium">Loading your tasks...</p>
          <p className="text-slate-500 text-sm mt-2">Preparing your daily overview</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyan-500/3 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Header Section with Enhanced Stats */}
        <div className="mb-10 animate-in slide-in-from-top duration-700">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-8 gap-6">
            <div className="space-y-2">
              <h1 className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Daily Focus
              </h1>
              <div className="flex items-center space-x-6 text-slate-300">
                <span className="flex items-center gap-2 text-lg">
                  <Calendar className="w-5 h-5" />
                  {formatDate(threeDays[1]).displayName}
                </span>
                <span className="text-lg">{completedTasks} of {totalTasks} completed</span>
              </div>
            </div>

            <button
              onClick={() => openTaskModal()}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-4 rounded-2xl flex items-center space-x-3 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl font-medium text-lg group"
            >
              <Plus className="w-6 h-6 group-hover:rotate-90 transition-transform duration-300" />
              <span>Add Task</span>
            </button>
          </div>

          {/* Stats Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/20 backdrop-blur-sm border border-blue-500/20 rounded-2xl p-6 hover:border-blue-400/40 transition-all duration-300 group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-400 font-medium mb-1">Today's Progress</p>
                  <p className="text-3xl font-bold text-white">{getDayCompletionPercent(threeDays[1])}%</p>
                </div>
                <div className="p-3 bg-blue-500/20 rounded-xl group-hover:bg-blue-500/30 transition-colors duration-300">
                  <TrendingUp className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/20 backdrop-blur-sm border border-purple-500/20 rounded-2xl p-6 hover:border-purple-400/40 transition-all duration-300 group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-400 font-medium mb-1">High Priority</p>
                  <p className="text-3xl font-bold text-white">{highPriorityTasks}</p>
                </div>
                <div className="p-3 bg-purple-500/20 rounded-xl group-hover:bg-purple-500/30 transition-colors duration-300">
                  <Zap className="w-6 h-6 text-purple-400" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500/10 to-green-600/20 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 hover:border-green-400/40 transition-all duration-300 group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-400 font-medium mb-1">Current Streak</p>
                  <p className="text-3xl font-bold text-white">{streakDays} days</p>
                </div>
                <div className="p-3 bg-green-500/20 rounded-xl group-hover:bg-green-500/30 transition-colors duration-300">
                  <Award className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/20 backdrop-blur-sm border border-orange-500/20 rounded-2xl p-6 hover:border-orange-400/40 transition-all duration-300 group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-400 font-medium mb-1">Total Tasks</p>
                  <p className="text-3xl font-bold text-white">{totalTasks}</p>
                </div>
                <div className="p-3 bg-orange-500/20 rounded-xl group-hover:bg-orange-500/30 transition-colors duration-300">
                  <Target className="w-6 h-6 text-orange-400" />
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Navigation and Filters */}
          <div className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-6">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between space-y-4 lg:space-y-0 gap-6">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => navigateDay('prev')}
                  className="p-3 hover:bg-white/10 rounded-xl transition-all duration-300 hover:scale-110 group"
                >
                  <ChevronLeft className="w-6 h-6 group-hover:-translate-x-1 transition-transform duration-300" />
                </button>
                <div className="text-center min-w-[200px]">
                  <span className="font-semibold text-xl">{formatDate(currentDay).displayName}</span>
                  <p className="text-slate-400 text-sm">{formatDate(currentDay).month} {formatDate(currentDay).dayNumber}</p>
                </div>
                <button
                  onClick={() => navigateDay('next')}
                  className="p-3 hover:bg-white/10 rounded-xl transition-all duration-300 hover:scale-110 group"
                >
                  <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
                </button>
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <div className="relative">
                  <Search className="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full lg:w-64 pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                >
                  <option value="all" className="text-black">All Types</option>
                  <option value="workout" className="text-black">Workout</option>
                  <option value="diet" className="text-black">Diet</option>
                  <option value="hydration" className="text-black">Hydration</option>
                  <option value="sleep" className="text-black">Sleep</option>
                </select>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                >
                  <option value="all" className="text-black">All Status</option>
                  <option value="completed" className="text-black">Completed</option>
                  <option value="pending" className="text-black">Pending</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* 3-Day Layout with Enhanced Design */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 animate-in slide-in-from-bottom duration-700 delay-200">
          {threeDays.map((date, index) => {
            const dayTasks = getTasksForDay(date)
            const dayInfo = formatDate(date)
            const completionPercent = getDayCompletionPercent(date)

            return (
              <div
                key={date}
                className={`relative backdrop-blur-xl rounded-3xl border overflow-hidden transition-all duration-500 hover:scale-[1.02] group ${
                  dayInfo.isToday
                    ? 'bg-gradient-to-br from-blue-500/15 to-purple-600/15 border-blue-400/30 shadow-lg shadow-blue-500/10'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {/* Day Header */}
                <div className={`p-6 border-b ${dayInfo.isToday ? 'border-white/20' : 'border-white/10'}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className={`text-2xl font-bold mb-1 ${
                        dayInfo.isToday ? 'text-white' :
                        dayInfo.isYesterday ? 'text-slate-300' :
                        'text-slate-200'
                      }`}>
                        {dayInfo.displayName}
                      </div>
                      <div className={`text-sm font-medium ${
                        dayInfo.isToday ? 'text-blue-200' : 'text-slate-400'
                      }`}>
                        {dayInfo.month} {dayInfo.dayNumber}, {dayInfo.dayName}
                      </div>
                    </div>
                    <button
                      onClick={() => openTaskModal(undefined, date)}
                      className={`p-3 rounded-xl transition-all duration-300 hover:scale-110 ${
                        dayInfo.isToday
                          ? 'hover:bg-white/20 text-white'
                          : 'hover:bg-white/10 text-slate-300'
                      }`}
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Progress Bar with Animation */}
                  <div className="relative">
                    <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-3 rounded-full transition-all duration-1000 ease-out ${
                          dayInfo.isToday
                            ? 'bg-gradient-to-r from-blue-400 to-purple-500'
                            : completionPercent === 100
                              ? 'bg-gradient-to-r from-green-400 to-green-500'
                              : 'bg-gradient-to-r from-slate-400 to-slate-500'
                        }`}
                        style={{ width: `${completionPercent}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs font-medium text-slate-400">
                        {dayTasks.filter(t => t.completed).length} / {dayTasks.length} completed
                      </span>
                      <span className={`text-sm font-bold ${
                        completionPercent === 100 ? 'text-green-400' :
                        dayInfo.isToday ? 'text-blue-400' : 'text-slate-400'
                      }`}>
                        {completionPercent}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Tasks List */}
                <div className="p-4 space-y-3 min-h-[400px] max-h-[600px] overflow-y-auto custom-scrollbar">
                  {dayTasks.map((task, taskIndex) => {
                    const taskTime = extractTimeFromTaskDate(task.task_date)

                    return (
                      <div
                        key={task._id}
                        className={`p-4 rounded-2xl border transition-all duration-300 cursor-pointer group hover:scale-[1.02] animate-in slide-in-from-left ${
                          task.completed
                            ? 'bg-black/20 border-white/5 opacity-70'
                            : 'bg-gradient-to-br from-white/5 to-white/10 border-white/10 hover:border-white/20 hover:from-white/10 hover:to-white/15'
                        }`}
                        style={{ animationDelay: `${taskIndex * 100}ms` }}
                        onClick={() => handleTaskClick(task)}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-3 flex-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleToggleCompletion(task)
                              }}
                              className={`flex-shrink-0 w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all duration-300 ${
                                task.completed
                                  ? 'bg-gradient-to-r from-green-500 to-green-600 border-green-500 text-white shadow-lg shadow-green-500/25'
                                  : 'border-slate-400 hover:border-blue-400 hover:bg-blue-500/10'
                              }`}
                            >
                              {task.completed && <Check className="w-4 h-4" />}
                            </button>
                            <div className={`flex items-center space-x-2 ${getTypeGradient(task.type)}`}>
                              <div className="p-2 bg-gradient-to-r rounded-lg border">
                                {getTypeIcon(task.type)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                openTaskModal(task)
                              }}
                              className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-300"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDeleteTask(task._id)
                              }}
                              className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-300"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                            <Eye className="w-4 h-4 text-slate-500" />
                          </div>
                        </div>

                        <div className={`transition-all duration-300 ${task.completed ? 'line-through text-slate-500' : 'text-white'}`}>
                          <div className="font-semibold text-lg mb-2">{task.name}</div>
                          <div className="flex items-center justify-between">
                            <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium border bg-gradient-to-r ${getPriorityGradient(task.priority)}`}>
                              {task.priority.toUpperCase()}
                            </span>
                            {taskTime && (
                              <span className="text-sm text-slate-400 flex items-center bg-white/5 px-3 py-1 rounded-full">
                                <Clock className="w-3 h-3 mr-1" />
                                {taskTime}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}

                  {dayTasks.length === 0 && (
                    <div className="text-center py-12 text-slate-500 flex flex-col items-center justify-center h-full animate-in fade-in duration-500">
                      <div className="p-6 bg-white/5 rounded-2xl border border-white/10 mb-4">
                        <Target className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p className="text-lg font-medium mb-1">No tasks yet</p>
                        <p className="text-sm text-slate-400">Add a task to get started</p>
                      </div>
                      <button
                        onClick={() => openTaskModal(undefined, date)}
                        className="text-blue-400 hover:text-blue-300 font-medium transition-colors duration-300"
                      >
                        + Add your first task
                      </button>
                    </div>
                  )}
                </div>

                {/* Day Summary Footer */}
                {dayTasks.length > 0 && (
                  <div className="p-4 border-t border-white/10 bg-white/5">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        <span className="text-slate-400">
                          {dayTasks.filter(t => t.type === 'workout').length} workouts
                        </span>
                        <span className="text-slate-400">
                          {dayTasks.filter(t => t.priority === 'high').length} high priority
                        </span>
                      </div>
                      <div className={`font-medium ${
                        completionPercent === 100 ? 'text-green-400' :
                        completionPercent >= 50 ? 'text-blue-400' : 'text-slate-400'
                      }`}>
                        {completionPercent === 100 ? '✨ Complete!' :
                         completionPercent >= 50 ? '💪 On track' : '⏳ Getting started'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Enhanced Task Modal */}
        {showTaskModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
            <div className="bg-slate-800/95 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl w-full max-w-md animate-in zoom-in-95 duration-300">
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    {editingTask ? 'Edit Task' : 'Create New Task'}
                  </h2>
                  <button
                    onClick={() => setShowTaskModal(false)}
                    className="p-3 text-slate-400 hover:bg-white/10 hover:text-white rounded-xl transition-all duration-200 hover:rotate-90"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">Task Name</label>
                    <input
                      type="text"
                      required
                      value={taskForm.name}
                      onChange={(e) => setTaskForm(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      placeholder="e.g., Morning Workout"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">Description</label>
                    <textarea
                      value={taskForm.description}
                      onChange={(e) => setTaskForm(prev => ({ ...prev, description: e.target.value }))}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      rows={3}
                      placeholder="Optional details or instructions..."
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-2">Category</label>
                      <select
                        value={taskForm.type}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                      >
                        <option className="text-black" value="workout">💪 Workout</option>
                        <option className="text-black" value="diet">🥗 Diet</option>
                        <option className="text-black" value="hydration">💧 Hydration</option>
                        <option className="text-black" value="sleep">🌙 Sleep</option>
                        <option className="text-black" value="habit">🎯 Habit</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-2">Priority</label>
                      <select
                        value={taskForm.priority}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, priority: e.target.value as 'high' | 'medium' | 'low' }))}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                      >
                        <option className="text-black" value="low">🟢 Low</option>
                        <option className="text-black" value="medium">🟡 Medium</option>
                        <option className="text-black" value="high">🔴 High</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-2">Date</label>
                      <input
                        type="date"
                        required
                        value={taskForm.task_date}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, task_date: e.target.value }))}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-2">Time (Optional)</label>
                      <input
                        type="time"
                        value={taskForm.time}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, time: e.target.value }))}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-end space-x-4 pt-6 border-t border-white/10">
                    <button
                      type="button"
                      onClick={() => setShowTaskModal(false)}
                      className="px-6 py-3 text-slate-200 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-all duration-300 font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={editingTask ? handleUpdateTask : handleCreateTask}
                      className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-xl transition-all duration-300 flex items-center gap-3 font-medium transform hover:scale-105"
                    >
                      {editingTask ? 'Update Task' : 'Create Task'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {loggingPerformanceTask && (
          <PerformanceLogModal
            task={loggingPerformanceTask}
            onClose={() => setLoggingPerformanceTask(null)}
            onSave={handleSavePerformanceAndComplete}
          />
        )}

        {viewingTaskDetails && (
          <TaskDetailsModal
            task={viewingTaskDetails}
            onClose={() => setViewingTaskDetails(null)}
            onEdit={handleEditFromDetails}
            onDelete={handleDeleteTask}
            onToggleCompletion={handleToggleCompletion}
          />
        )}
      </div>
    </div>
  )
}