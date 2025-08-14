import { useEffect, useState } from 'react'
import { Plus, ChevronLeft, ChevronRight, Search, Filter, Calendar, Clock, Target, Droplets, Utensils, Dumbbell, Moon, Check, X, Edit2, Trash2, Star } from 'lucide-react'

type Task = {
  _id: string
  name: string
  description?: string
  type: 'workout' | 'diet' | 'hydration' | 'sleep' | 'habit' | string
  priority: 'high' | 'medium' | 'low'
  completed: boolean
  task_date: string
  time?: string
}

type TaskFormData = {
  name: string
  description: string
  type: string
  priority: 'high' | 'medium' | 'low'
  task_date: string
  time: string
}

// Mock API functions (logic unchanged)
const mockApi = {
  async getWeekTasks(startDate: string) {
    await new Promise(resolve => setTimeout(resolve, 500))
    const tasks: Task[] = []
    const days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(startDate)
      date.setDate(date.getDate() + i)
      return date.toISOString().split('T')[0]
    })
    
    days.forEach((date, index) => {
      if (index < 4) { // Add tasks to first 4 days for demo
        tasks.push(
          {
            _id: `task-${date}-1`,
            name: 'Morning Workout',
            description: '30 min strength training',
            type: 'workout',
            priority: 'high',
            completed: index < 2,
            task_date: date,
            time: '07:00'
          },
          {
            _id: `task-${date}-2`,
            name: 'Drink 2L Water',
            description: 'Stay hydrated throughout the day',
            type: 'hydration',
            priority: 'medium',
            completed: index === 0,
            task_date: date,
            time: '09:00'
          },
          {
            _id: `task-${date}-3`,
            name: 'Log meals',
            description: 'Track macros in the app',
            type: 'diet',
            priority: 'low',
            completed: false,
            task_date: date,
          }
        )
      }
    })
    
    return { data: tasks }
  },
  
  async createTask(task: TaskFormData) {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { 
      data: { 
        _id: `task-${Date.now()}`, 
        ...task,
        completed: false 
      } 
    }
  },
  
  async updateTask(id: string, updates: Partial<Task>) {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { data: { _id: id, ...updates } }
  },
  
  async deleteTask(id: string) {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { success: true }
  },
  
  async toggleCompletion(id: string) {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { success: true }
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'workout': return <Dumbbell className="w-4 h-4" />
    case 'diet': return <Utensils className="w-4 h-4" />
    case 'hydration': return <Droplets className="w-4 h-4" />
    case 'sleep': return <Moon className="w-4 h-4" />
    default: return <Target className="w-4 h-4" />
  }
}

// Updated priority colors for the dark theme
const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'bg-red-500/20 text-red-300 border-red-500/30'
    case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
    case 'low': return 'bg-green-500/20 text-green-300 border-green-500/30'
    default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return {
    dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
    dayNumber: date.getDate(),
    month: date.toLocaleDateString('en-US', { month: 'short' })
  }
}

export default function WeeklyTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [currentWeek, setCurrentWeek] = useState(() => {
    const today = new Date()
    const dayOfWeek = today.getDay()
    const monday = new Date(today.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1)))
    return monday.toISOString().split('T')[0]
  })
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
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

  // Generate week days array
  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(currentWeek)
    date.setDate(date.getDate() + i)
    return date.toISOString().split('T')[0]
  })

  const loadTasks = async () => {
    setLoading(true)
    try {
      const { data } = await mockApi.getWeekTasks(currentWeek)
      setTasks(data)
    } catch (error) {
      console.error('Error loading tasks:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadTasks()
  }, [currentWeek])

  const getTasksForDay = (date: string) => {
    return tasks.filter(task => {
      const matchesDate = task.task_date === date
      const matchesSearch = task.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesType = filterType === 'all' || task.type === filterType
      const matchesStatus = filterStatus === 'all' || 
        (filterStatus === 'completed' && task.completed) ||
        (filterStatus === 'pending' && !task.completed)
      
      return matchesDate && matchesSearch && matchesType && matchesStatus
    })
  }

  const getDayCompletionPercent = (date: string) => {
    const dayTasks = tasks.filter(task => task.task_date === date)
    if (dayTasks.length === 0) return 0
    const completed = dayTasks.filter(task => task.completed).length
    return Math.round((completed / dayTasks.length) * 100)
  }

  const handleCreateTask = async () => {
    if (!taskForm.name.trim() || !taskForm.task_date) return
    
    try {
      const { data } = await mockApi.createTask(taskForm)
      setTasks(prev => [...prev, data])
      resetTaskForm()
      setShowTaskModal(false)
    } catch (error) {
      console.error('Error creating task:', error)
    }
  }

  const handleUpdateTask = async () => {
    if (!editingTask || !taskForm.name.trim()) return
    
    try {
      await mockApi.updateTask(editingTask._id, taskForm)
      setTasks(prev => prev.map(task => 
        task._id === editingTask._id ? { ...task, ...taskForm } : task
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
      await mockApi.deleteTask(taskId)
      setTasks(prev => prev.filter(task => task._id !== taskId))
    } catch (error) {
      console.error('Error deleting task:', error)
    }
  }

  const handleToggleCompletion = async (task: Task) => {
    try {
      await mockApi.toggleCompletion(task._id)
      setTasks(prev => prev.map(t => 
        t._id === task._id ? { ...t, completed: !t.completed } : t
      ))
    } catch (error) {
      console.error('Error toggling task:', error)
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
        description: task.description || '',
        type: task.type,
        priority: task.priority,
        task_date: task.task_date,
        time: task.time || ''
      })
    } else {
      setEditingTask(null)
      resetTaskForm()
      setTaskForm(prev => ({ ...prev, task_date: date || new Date().toISOString().split('T')[0] }))
    }
    setShowTaskModal(true)
  }

  const navigateWeek = (direction: 'prev' | 'next') => {
    const date = new Date(currentWeek)
    date.setDate(date.getDate() + (direction === 'next' ? 7 : -7))
    setCurrentWeek(date.toISOString().split('T')[0])
  }

  const getWeekNumber = () => {
    const date = new Date(currentWeek)
    const start = new Date(date.getFullYear(), 0, 1)
    const days = Math.floor((date.getTime() - start.getTime()) / (24 * 60 * 60 * 1000))
    return Math.ceil((date.getDay() + 1 + days) / 7)
  }

  const totalTasks = tasks.length
  const completedTasks = tasks.filter(task => task.completed).length
  const overallProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading your tasks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 text-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">Weekly Tasks</h1>
              <div className="flex items-center space-x-4 text-sm text-slate-300">
                <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" /> Week {getWeekNumber()}</span>
                <span>{completedTasks} of {totalTasks} completed ({overallProgress}%)</span>
              </div>
            </div>
            
            <button
              onClick={() => openTaskModal()}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-3 rounded-xl flex items-center space-x-2 transition-all transform hover:scale-105 shadow-lg"
            >
              <Plus className="w-5 h-5" />
              <span>Add Task</span>
            </button>
          </div>

          {/* Controls */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0 bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
            {/* Week Navigation */}
            <div className="flex items-center space-x-2">
              <button onClick={() => navigateWeek('prev')} className="p-2 hover:bg-white/10 rounded-lg transition-colors"><ChevronLeft className="w-5 h-5" /></button>
              <span className="font-semibold min-w-[150px] text-center">{formatDate(currentWeek).month} {formatDate(currentWeek).dayNumber} - {formatDate(weekDays[6]).month} {formatDate(weekDays[6]).dayNumber}</span>
              <button onClick={() => navigateWeek('next')} className="p-2 hover:bg-white/10 rounded-lg transition-colors"><ChevronRight className="w-5 h-5" /></button>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input type="text" placeholder="Search tasks..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full sm:w-auto pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="all" className="text-black">All Types</option>
                <option value="workout" className="text-black">Workout</option>
                <option value="diet" className="text-black">Diet</option>
                <option value="hydration" className="text-black">Hydration</option>
                <option value="sleep" className="text-black">Sleep</option>
              </select>
              <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="all" className="text-black">All Status</option>
                <option value="completed" className="text-black">Completed</option>
                <option value="pending" className="text-black">Pending</option>
              </select>
            </div>
          </div>
        </div>

        {/* Weekly Task Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
          {weekDays.map((date) => {
            const dayTasks = getTasksForDay(date)
            const dayInfo = formatDate(date)
            const completionPercent = getDayCompletionPercent(date)
            const isToday = date === new Date().toISOString().split('T')[0]

            return (
              <div key={date} className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 flex flex-col">
                {/* Day Header */}
                <div className={`p-4 border-b border-white/10 ${isToday ? 'bg-gradient-to-r from-blue-500 to-purple-600 rounded-t-2xl' : ''}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="font-semibold">{dayInfo.dayName}</div>
                      <div className={`text-sm ${isToday ? 'text-purple-200' : 'text-slate-400'}`}>{dayInfo.month} {dayInfo.dayNumber}</div>
                    </div>
                    <button onClick={() => openTaskModal(undefined, date)} className={`p-1 rounded-lg transition-colors ${isToday ? 'hover:bg-white/20' : 'hover:bg-white/10 text-slate-300'}`}><Plus className="w-4 h-4" /></button>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2 mt-1">
                    <div className={`h-2 rounded-full transition-all duration-300 ${isToday ? 'bg-white' : 'bg-gradient-to-r from-blue-500 to-purple-600'}`} style={{ width: `${completionPercent}%` }}></div>
                  </div>
                </div>

                {/* Tasks List */}
                <div className="p-2 space-y-2 min-h-[300px] flex-grow">
                  {dayTasks.map((task) => (
                    <div key={task._id} className={`p-3 rounded-lg border transition-all hover:border-white/30 ${task.completed ? 'bg-black/20 border-white/10 opacity-60' : 'bg-white/5 border-white/10'}`}>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2 flex-1">
                          <button onClick={() => handleToggleCompletion(task)} className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${task.completed ? 'bg-blue-500 border-blue-500 text-white' : 'border-slate-500 hover:border-blue-400'}`}>
                            {task.completed && <Check className="w-3 h-3" />}
                          </button>
                          <div className={`flex items-center space-x-1 ${task.completed ? 'text-slate-500' : 'text-slate-300'}`}>{getTypeIcon(task.type)}</div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <button onClick={() => openTaskModal(task)} className="p-1 text-slate-400 hover:text-white transition-colors"><Edit2 className="w-3 h-3" /></button>
                          <button onClick={() => handleDeleteTask(task._id)} className="p-1 text-slate-400 hover:text-red-400 transition-colors"><Trash2 className="w-3 h-3" /></button>
                        </div>
                      </div>
                      <div className={`${task.completed ? 'line-through text-slate-500' : 'text-white'}`}>
                        <div className="font-medium text-sm mb-1">{task.name}</div>
                        {task.description && <div className="text-xs text-slate-400 mb-2">{task.description}</div>}
                        <div className="flex items-center justify-between">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-xs border ${getPriorityColor(task.priority)}`}>{task.priority}</span>
                          {task.time && <span className="text-xs text-slate-400 flex items-center"><Clock className="w-3 h-3 mr-1" />{task.time}</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                  {dayTasks.length === 0 && (
                    <div className="text-center py-8 text-slate-500 flex flex-col items-center justify-center h-full">
                      <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No tasks for this day</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Task Modal */}
        {showTaskModal && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800/80 backdrop-blur-lg border border-white/20 rounded-2xl shadow-xl w-full max-w-md">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">{editingTask ? 'Edit Task' : 'Create New Task'}</h2>
                  <button onClick={() => setShowTaskModal(false)} className="p-2 text-slate-400 hover:bg-white/10 hover:text-white rounded-lg transition-colors"><X className="w-5 h-5" /></button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Task Name</label>
                    <input type="text" required value={taskForm.name} onChange={(e) => setTaskForm(prev => ({ ...prev, name: e.target.value }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g., Evening Cardio" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                    <textarea value={taskForm.description} onChange={(e) => setTaskForm(prev => ({ ...prev, description: e.target.value }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" rows={2} placeholder="Optional details..." />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Category</label>
                      <select value={taskForm.type} onChange={(e) => setTaskForm(prev => ({ ...prev, type: e.target.value }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option className="text-black" value="workout">Workout</option>
                        <option className="text-black" value="diet">Diet</option>
                        <option className="text-black" value="hydration">Hydration</option>
                        <option className="text-black" value="sleep">Sleep</option>
                        <option className="text-black" value="habit">Habit</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Priority</label>
                      <select value={taskForm.priority} onChange={(e) => setTaskForm(prev => ({ ...prev, priority: e.target.value as 'high' | 'medium' | 'low' }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option className="text-black" value="low">Low</option>
                        <option className="text-black" value="medium">Medium</option>
                        <option className="text-black" value="high">High</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Date</label>
                      <input type="date" required value={taskForm.task_date} onChange={(e) => setTaskForm(prev => ({ ...prev, task_date: e.target.value }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Time (Optional)</label>
                      <input type="time" value={taskForm.time} onChange={(e) => setTaskForm(prev => ({ ...prev, time: e.target.value }))} className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                  </div>
                  <div className="flex items-center justify-end space-x-3 pt-4">
                    <button type="button" onClick={() => setShowTaskModal(false)} className="px-4 py-2 text-slate-200 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg transition-colors">Cancel</button>
                    <button type="button" onClick={editingTask ? handleUpdateTask : handleCreateTask} className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg transition-all">{editingTask ? 'Update Task' : 'Create Task'}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}