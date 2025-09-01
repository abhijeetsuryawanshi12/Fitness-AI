import { useState, useEffect } from 'react'
import { Calendar, Clock, Target, Dumbbell, Utensils, Play, CheckCircle, Circle, Download, Share2, Zap, TrendingUp, Award, RefreshCw } from 'lucide-react'
import api from '@/lib/api' // Import your actual API instance

export default function Plan() {
  const [type, setType] = useState('workout and diet')
  const [loading, setLoading] = useState(false) // For generation button
  const [initialLoading, setInitialLoading] = useState(true) // For initial page load
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedDay, setSelectedDay] = useState(1)
  const [completedExercises, setCompletedExercises] = useState(new Set())

  // Fetch the latest plan when the component mounts
  useEffect(() => {
    async function fetchLatestPlan() {
      try {
        setError(null);
        const { data } = await api.get('/plan/latest');
        setPlan(data);
        if (data?.content?.daily_plan?.[0]?.day) {
          setSelectedDay(data.content.daily_plan[0].day);
        }
      } catch (err) {
        // A 404 error is expected if the user has no plan, so we don't set an error state for it.
        if (err.response?.status !== 404) {
          setError('Could not fetch your existing plan.');
        }
      } finally {
        setInitialLoading(false);
      }
    }
    fetchLatestPlan();
  }, []);

  // Function to generate a new plan
  async function generate(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      // Use the real API endpoint
      const { data } = await api.post('/plan/generate', { type })
      setPlan(data)
      setSelectedDay(1)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to generate plan')
    } finally {
      setLoading(false)
    }
  }
  
  // Function to reset state and show the generation form again
  const handleGenerateNew = () => {
    setPlan(null);
    setError(null);
    setSelectedDay(1);
    setActiveTab('overview');
  };

  const toggleExerciseComplete = (exerciseId) => {
    const newCompleted = new Set(completedExercises)
    if (newCompleted.has(exerciseId)) {
      newCompleted.delete(exerciseId)
    } else {
      newCompleted.add(exerciseId)
    }
    setCompletedExercises(newCompleted)
  }

  const currentDay = plan?.content?.daily_plan?.find((day) => day.day === selectedDay)
  const totalDays = plan?.content?.daily_plan?.length || 0
  const progressPercentage = totalDays > 0 ? (selectedDay / totalDays) * 100 : 0

  const getTotalNutrition = (meals) => {
    return meals.reduce((total, meal) => ({
      calories: total.calories + (meal.nutrition_facts?.calories || 0),
      protein: total.protein + (meal.nutrition_facts?.protein || 0),
      carbs: total.carbs + (meal.nutrition_facts?.carbs || 0),
      fat: total.fat + (meal.nutrition_facts?.total_fat || 0),
    }), { calories: 0, protein: 0, carbs: 0, fat: 0 })
  }
  
  // Initial loading state while checking for an existing plan
  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <p className="text-lg">Checking for your fitness plan...</p>
        </div>
      </div>
    );
  }

  // If no plan exists, show the generation form
  if (!plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl mb-6">
              <Dumbbell className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">Create Your Fitness Plan</h1>
            <p className="text-slate-300 text-lg">Generate a personalized workout and nutrition plan tailored to your goals</p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/20">
            <div className="space-y-6">
              <div>
                <label className="block text-white font-medium mb-3">Plan Type</label>
                <select 
                  className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={type} 
                  onChange={e => setType(e.target.value)}
                >
                  <option value="workout" className="text-black">Workout Only</option>
                  <option value="diet" className="text-black">Diet Only</option>
                  <option value="workout and diet" className="text-black">Workout & Diet</option>
                </select>
              </div>

              <button 
                disabled={loading}
                onClick={generate}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-4 px-8 rounded-2xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Generating Your Plan...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Generate Plan
                  </>
                )}
              </button>

              {error && (
                <div className="mt-6 bg-red-500/20 border border-red-500/50 text-red-100 px-4 py-3 rounded-2xl">
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // If a plan exists, display it
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Your Fitness Plan</h1>
              <p className="text-slate-300">{plan.content.title}</p>
            </div>
            <div className="flex gap-3">
              <button onClick={handleGenerateNew} className="bg-white/10 backdrop-blur-sm border border-white/20 text-white px-4 py-2 rounded-xl hover:bg-white/20 transition-colors flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Generate New Plan
              </button>
              <button className="bg-white/10 backdrop-blur-sm border border-white/20 text-white px-4 py-2 rounded-xl hover:bg-white/20 transition-colors flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Award className="w-6 h-6 text-yellow-400" />
                <span className="text-white font-medium">Progress</span>
              </div>
              <span className="text-slate-300">Day {selectedDay} of {totalDays}</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-white/10 backdrop-blur-lg rounded-2xl p-2 mb-8 border border-white/20">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'workout', label: 'Workout', icon: Dumbbell },
            { id: 'meals', label: 'Nutrition', icon: Utensils }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Day Selector */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 sticky top-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Select Day
              </h3>
              <div className="space-y-2">
                {plan.content.daily_plan.map((day) => (
                  <button
                    key={day.day}
                    onClick={() => setSelectedDay(day.day)}
                    className={`w-full text-left p-3 rounded-xl transition-all duration-200 ${
                      selectedDay === day.day
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                        : 'text-slate-300 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <div className="font-medium">Day {day.day}</div>
                    <div className="text-sm opacity-75">{day.theme}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === 'overview' && currentDay && (
              <div className="space-y-6">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                  <h3 className="text-2xl font-bold text-white mb-2">Day {currentDay.day}: {currentDay.theme}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div className="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
                      <Dumbbell className="w-6 h-6 text-blue-400 mb-2" />
                      <div className="text-blue-100 font-medium">{currentDay.exercises?.length || 0} Exercises</div>
                    </div>
                    <div className="bg-green-500/20 rounded-xl p-4 border border-green-500/30">
                      <Utensils className="w-6 h-6 text-green-400 mb-2" />
                      <div className="text-green-100 font-medium">{currentDay.meals?.length || 0} Meals</div>
                    </div>
                    <div className="bg-purple-500/20 rounded-xl p-4 border border-purple-500/30">
                      <Target className="w-6 h-6 text-purple-400 mb-2" />
                      <div className="text-purple-100 font-medium">
                        {currentDay.meals ? getTotalNutrition(currentDay.meals).calories : 0} Calories
                      </div>
                    </div>
                  </div>
                </div>

                {currentDay.exercises && currentDay.exercises.length > 0 && (
                  <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h4 className="text-xl font-semibold text-white mb-4">Today's Workout</h4>
                    <div className="space-y-3">
                      {currentDay.exercises.slice(0, 3).map((exercise, index) => (
                        <div key={index} className="bg-white/5 rounded-xl p-4 border border-white/10">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                              <span className="text-white text-sm font-bold">{index + 1}</span>
                            </div>
                            <div>
                              <div className="text-white font-medium">{exercise.name}</div>
                              <div className="text-slate-400 text-sm">{exercise.sets} sets × {exercise.reps} reps</div>
                            </div>
                          </div>
                        </div>
                      ))}
                      {currentDay.exercises.length > 3 && (
                        <div className="text-center">
                          <button 
                            onClick={() => setActiveTab('workout')}
                            className="text-blue-400 hover:text-blue-300 font-medium"
                          >
                            View all {currentDay.exercises.length} exercises →
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'workout' && currentDay && (
              <div className="space-y-6">
                {currentDay.exercises && currentDay.exercises.length > 0 ? (
                  currentDay.exercises.map((exercise, index) => {
                    const exerciseId = `${currentDay.day}-${index}`
                    const isCompleted = completedExercises.has(exerciseId)
                    
                    return (
                      <div key={index} className={`bg-white/10 backdrop-blur-lg rounded-2xl p-6 border transition-all duration-200 ${
                        isCompleted ? 'border-green-500/50 bg-green-500/10' : 'border-white/20'
                      }`}>
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="text-xl font-semibold text-white mb-2">{exercise.name}</h4>
                            <div className="flex items-center gap-4 text-slate-300">
                              <span className="flex items-center gap-1">
                                <Target className="w-4 h-4" />
                                {exercise.sets} sets
                              </span>
                              <span>{exercise.reps} reps</span>
                              {exercise.weights && exercise.weights[0] > 0 && (
                                <span>{exercise.weights[0]}kg</span>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={() => toggleExerciseComplete(exerciseId)}
                            className={`p-2 rounded-xl transition-colors ${
                              isCompleted 
                                ? 'text-green-400 bg-green-500/20' 
                                : 'text-slate-400 hover:text-white'
                            }`}
                          >
                            {isCompleted ? <CheckCircle className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
                          </button>
                        </div>
                        
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                          <h5 className="text-white font-medium mb-2 flex items-center gap-2">
                            <Play className="w-4 h-4" />
                            Instructions
                          </h5>
                          <p className="text-slate-300 text-sm leading-relaxed">{exercise.instructions}</p>
                        </div>

                        {exercise.weights && exercise.weights.length > 0 && (
                          <div className="mt-4">
                            <h5 className="text-white font-medium mb-2">Weight per Set</h5>
                            <div className="flex gap-2">
                              {exercise.weights.map((weight, setIndex) => (
                                <div key={setIndex} className="bg-blue-500/20 rounded-lg px-3 py-2 border border-blue-500/30">
                                  <span className="text-blue-100 text-sm">Set {setIndex + 1}: {weight > 0 ? `${weight}kg` : 'Bodyweight'}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })
                ) : (
                  <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 border border-white/20 text-center">
                    <div className="w-16 h-16 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Clock className="w-8 h-8 text-purple-400" />
                    </div>
                    <h3 className="text-2xl font-semibold text-white mb-2">Rest Day</h3>
                    <p className="text-slate-300">Take a break and let your muscles recover!</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'meals' && currentDay && (
              <div className="space-y-6">
                {currentDay.meals && currentDay.meals.length > 0 && (
                  <>
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                      <h3 className="text-xl font-semibold text-white mb-4">Daily Nutrition Summary</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(getTotalNutrition(currentDay.meals)).map(([key, value]) => (
                          <div key={key} className="bg-white/5 rounded-xl p-4 text-center border border-white/10">
                            <div className="text-2xl font-bold text-white">{Math.round(value)}</div>
                            <div className="text-slate-400 capitalize text-sm">{key === 'fat' ? 'Total Fat' : key}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="grid gap-6">
                      {currentDay.meals.map((meal, index) => (
                        <div key={index} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                          <h4 className="text-xl font-semibold text-white mb-4 flex items-center gap-3">
                            <Utensils className="w-5 h-5 text-orange-400" />
                            {meal.meal_name}
                          </h4>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-orange-500/20 rounded-xl p-4 border border-orange-500/30">
                              <div className="text-orange-100 text-sm mb-1">Calories</div>
                              <div className="text-2xl font-bold text-orange-100">{meal.nutrition_facts.calories}</div>
                            </div>
                            <div className="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
                              <div className="text-blue-100 text-sm mb-1">Protein</div>
                              <div className="text-2xl font-bold text-blue-100">{meal.nutrition_facts.protein}g</div>
                            </div>
                            <div className="bg-green-500/20 rounded-xl p-4 border border-green-500/30">
                              <div className="text-green-100 text-sm mb-1">Carbs</div>
                              <div className="text-2xl font-bold text-green-100">{meal.nutrition_facts.carbs}g</div>
                            </div>
                            <div className="bg-purple-500/20 rounded-xl p-4 border border-purple-500/30">
                              <div className="text-purple-100 text-sm mb-1">Fat</div>
                              <div className="text-2xl font-bold text-purple-100">{meal.nutrition_facts.total_fat}g</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}