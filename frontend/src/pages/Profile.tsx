import { useState } from 'react'
import { 
  User, Edit3, Save, X, Camera, Mail, Calendar, Users, Ruler, Weight, 
  Briefcase, Target, Clock, Dumbbell, Heart, Shield, Battery, Moon, 
  Utensils, Wine, Cigarette, Star, Lock, Eye, EyeOff, CheckCircle,
  MapPin, Phone, Globe
} from 'lucide-react'

export default function ProfilePage() {
  const [isEditMode, setIsEditMode] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [activeSection, setActiveSection] = useState('personal')
  
  // Sample user data
  const [profileData, setProfileData] = useState({
    // Personal Info
    name: "Abhijeet Suryawanshi",
    email: "abhijeet@example.com", 
    age: 28,
    gender: "Male",
    height: 175,
    weight: 70,
    profession: "Software Engineer",
    phone: "+91 98765 43210",
    location: "Pune, Maharashtra",
    
    // Fitness Goals
    primaryGoal: "Build Muscle",
    goalDeadline: "3 Months",
    workoutDuration: 60,
    workoutTime: "Morning",
    experience: "Intermediate",
    
    // Health Info
    medicalConditions: ["None"],
    injuries: ["None"],
    energyLevel: 7,
    sleepQuality: 8,
    
    // Diet Preferences
    dietType: "Vegetarian",
    dietTypeOther: "",
    mealsPerDay: 4,
    smokingHabit: "Never",
    alcoholConsumption: "Occasionally",
    favoriteFoods: ["Paneer", "Dal", "Rice", "Vegetables", "Fruits"],
    
    // Account Meta
    createdAt: "2024-01-15",
    lastUpdated: "2024-08-14",
    profilePicture: null
  })
  
  const [editData, setEditData] = useState({...profileData})

  const sections = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'fitness', label: 'Fitness Goals', icon: Target },
    { id: 'health', label: 'Health & Medical', icon: Heart },
    { id: 'diet', label: 'Diet & Nutrition', icon: Utensils },
    { id: 'account', label: 'Account Settings', icon: Shield }
  ]

  const goalOptions = ["Build Muscle", "Lose Fat", "Maintain Weight", "Improve Endurance", "General Fitness"]
  const experienceOptions = ["Beginner", "Intermediate", "Advanced"]
  const workoutTimeOptions = ["Morning", "Afternoon", "Evening", "Night"]
  const dietOptions = ["Anything", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean", "Other"]
  const foodOptions = ["Chicken", "Fish", "Eggs", "Paneer", "Tofu", "Dal", "Rice", "Quinoa", "Oats", "Vegetables", "Fruits", "Nuts", "Yogurt"]
  
  const handleSave = () => {
    setProfileData({...editData})
    setIsEditMode(false)
    // Show success toast (simplified)
    console.log("Profile updated successfully!")
  }

  const handleCancel = () => {
    setEditData({...profileData})
    setIsEditMode(false)
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  const toggleFavoriteFood = (food) => {
    const foods = editData.favoriteFoods || []
    if (foods.includes(food)) {
      setEditData({...editData, favoriteFoods: foods.filter(f => f !== food)})
    } else {
      setEditData({...editData, favoriteFoods: [...foods, food]})
    }
  }

  const Section = ({ id, title, icon: Icon, children }) => (
    <div className={`transition-all duration-300 ${activeSection === id ? 'block' : 'hidden'}`}>
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
            <Icon className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-white">{title}</h3>
        </div>
        {children}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        
        {/* Header Section */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-white/20">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            {/* Profile Picture */}
            <div className="relative">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-2xl font-bold text-white">
                {profileData.profilePicture ? (
                  <img src={profileData.profilePicture} alt="Profile" className="w-full h-full rounded-full object-cover" />
                ) : (
                  getInitials(profileData.name)
                )}
              </div>
              {isEditMode && (
                <button className="absolute -bottom-1 -right-1 bg-blue-500 rounded-full p-2 hover:bg-blue-600 transition-colors">
                  <Camera className="w-4 h-4 text-white" />
                </button>
              )}
            </div>

            {/* User Info */}
            <div className="flex-1">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">{profileData.name}</h1>
                  <div className="flex items-center gap-4 text-slate-300">
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      <span>{profileData.profession}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>{profileData.location}</span>
                    </div>
                  </div>
                </div>

                {/* Edit Button */}
                <div className="flex gap-3">
                  {isEditMode ? (
                    <>
                      <button
                        onClick={handleSave}
                        className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 flex items-center gap-2 font-medium"
                      >
                        <Save className="w-4 h-4" />
                        Save Changes
                      </button>
                      <button
                        onClick={handleCancel}
                        className="bg-white/10 border border-white/20 text-white px-6 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 flex items-center gap-2 font-medium"
                      >
                        <X className="w-4 h-4" />
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setIsEditMode(true)}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center gap-2 font-medium"
                    >
                      <Edit3 className="w-4 h-4" />
                      Edit Profile
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Navigation Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 sticky top-6">
              <h3 className="text-white font-semibold mb-4">Profile Sections</h3>
              <nav className="space-y-2">
                {sections.map((section) => {
                  const Icon = section.icon
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full text-left p-3 rounded-xl transition-all duration-200 flex items-center gap-3 ${
                        activeSection === section.id
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                          : 'text-slate-300 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {section.label}
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Personal Information */}
            <Section id="personal" title="Personal Information" icon={User}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-medium mb-2">Full Name</label>
                  {isEditMode ? (
                    <input
                      type="text"
                      value={editData.name}
                      onChange={(e) => setEditData({...editData, name: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10">
                      {profileData.name}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Email</label>
                  <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {profileData.email}
                  </div>
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Age</label>
                  {isEditMode ? (
                    <input
                      type="number"
                      value={editData.age}
                      onChange={(e) => setEditData({...editData, age: parseInt(e.target.value)})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {profileData.age} years
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Gender</label>
                  {isEditMode ? (
                    <select
                      value={editData.gender}
                      onChange={(e) => setEditData({...editData, gender: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Male" className="text-black">Male</option>
                      <option value="Female" className="text-black">Female</option>
                      <option value="Other" className="text-black">Other</option>
                    </select>
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      {profileData.gender}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Height (cm)</label>
                  {isEditMode ? (
                    <input
                      type="number"
                      value={editData.height}
                      onChange={(e) => setEditData({...editData, height: parseInt(e.target.value)})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Ruler className="w-4 h-4" />
                      {profileData.height} cm
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Weight (kg)</label>
                  {isEditMode ? (
                    <input
                      type="number"
                      value={editData.weight}
                      onChange={(e) => setEditData({...editData, weight: parseInt(e.target.value)})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Weight className="w-4 h-4" />
                      {profileData.weight} kg
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Profession</label>
                  {isEditMode ? (
                    <input
                      type="text"
                      value={editData.profession}
                      onChange={(e) => setEditData({...editData, profession: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      {profileData.profession}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Phone</label>
                  {isEditMode ? (
                    <input
                      type="tel"
                      value={editData.phone}
                      onChange={(e) => setEditData({...editData, phone: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      {profileData.phone}
                    </div>
                  )}
                </div>
              </div>
            </Section>

            {/* Fitness Goals */}
            <Section id="fitness" title="Fitness Goals & Preferences" icon={Target}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-medium mb-2">Primary Goal</label>
                  {isEditMode ? (
                    <select
                      value={editData.primaryGoal}
                      onChange={(e) => setEditData({...editData, primaryGoal: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {goalOptions.map(goal => (
                        <option key={goal} value={goal} className="text-black">{goal}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      {profileData.primaryGoal}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Goal Deadline</label>
                  {isEditMode ? (
                    <input
                      type="text"
                      value={editData.goalDeadline}
                      onChange={(e) => setEditData({...editData, goalDeadline: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., 3 Months"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {profileData.goalDeadline}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Workout Duration (minutes)</label>
                  {isEditMode ? (
                    <input
                      type="number"
                      value={editData.workoutDuration}
                      onChange={(e) => setEditData({...editData, workoutDuration: parseInt(e.target.value)})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {profileData.workoutDuration} minutes
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Preferred Workout Time</label>
                  {isEditMode ? (
                    <select
                      value={editData.workoutTime}
                      onChange={(e) => setEditData({...editData, workoutTime: e.target.value})}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {workoutTimeOptions.map(time => (
                        <option key={time} value={time} className="text-black">{time}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {profileData.workoutTime}
                    </div>
                  )}
                </div>

                <div className="md:col-span-2">
                  <label className="block text-white font-medium mb-2">Workout Experience</label>
                  {isEditMode ? (
                    <div className="flex gap-3">
                      {experienceOptions.map(level => (
                        <button
                          key={level}
                          onClick={() => setEditData({...editData, experience: level})}
                          className={`px-4 py-2 rounded-xl transition-all duration-200 ${
                            editData.experience === level
                              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                              : 'bg-white/10 text-slate-300 hover:bg-white/20'
                          }`}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Dumbbell className="w-4 h-4" />
                      {profileData.experience}
                    </div>
                  )}
                </div>
              </div>
            </Section>

            {/* Health & Medical */}
            <Section id="health" title="Health & Medical Information" icon={Heart}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-medium mb-2">Medical Conditions</label>
                  <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    {profileData.medicalConditions.join(', ')}
                  </div>
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Injuries</label>
                  <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                    <Heart className="w-4 h-4" />
                    {profileData.injuries.join(', ')}
                  </div>
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Energy Level (1-10)</label>
                  {isEditMode ? (
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={editData.energyLevel}
                      onChange={(e) => setEditData({...editData, energyLevel: parseInt(e.target.value)})}
                      className="w-full"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Battery className="w-4 h-4" />
                      {profileData.energyLevel}/10
                    </div>
                  )}
                  {isEditMode && <div className="text-center text-white mt-2">{editData.energyLevel}/10</div>}
                </div>

                <div>
                  <label className="block text-white font-medium mb-2">Sleep Quality (1-10)</label>
                  {isEditMode ? (
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={editData.sleepQuality}
                      onChange={(e) => setEditData({...editData, sleepQuality: parseInt(e.target.value)})}
                      className="w-full"
                    />
                  ) : (
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Moon className="w-4 h-4" />
                      {profileData.sleepQuality}/10
                    </div>
                  )}
                  {isEditMode && <div className="text-center text-white mt-2">{editData.sleepQuality}/10</div>}
                </div>
              </div>
            </Section>

            {/* Diet & Nutrition */}
            <Section id="diet" title="Diet & Nutrition Preferences" icon={Utensils}>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white font-medium mb-2">Diet Type</label>
                    {isEditMode ? (
                      <select
                        value={editData.dietType}
                        onChange={(e) => setEditData({...editData, dietType: e.target.value})}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {dietOptions.map(diet => (
                          <option key={diet} value={diet} className="text-black">{diet}</option>
                        ))}
                      </select>
                    ) : (
                      <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                        <Utensils className="w-4 h-4" />
                        {profileData.dietType}
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-white font-medium mb-2">Meals per Day</label>
                    {isEditMode ? (
                      <input
                        type="number"
                        value={editData.mealsPerDay}
                        onChange={(e) => setEditData({...editData, mealsPerDay: parseInt(e.target.value)})}
                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    ) : (
                      <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                        <Utensils className="w-4 h-4" />
                        {profileData.mealsPerDay} meals
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-white font-medium mb-2">Smoking Habit</label>
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Cigarette className="w-4 h-4" />
                      {profileData.smokingHabit}
                    </div>
                  </div>

                  <div>
                    <label className="block text-white font-medium mb-2">Alcohol Consumption</label>
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Wine className="w-4 h-4" />
                      {profileData.alcoholConsumption}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-white font-medium mb-3">Favorite Foods</label>
                  <div className="flex flex-wrap gap-2">
                    {foodOptions.map(food => {
                      const isSelected = profileData.favoriteFoods.includes(food)
                      return (
                        <div
                          key={food}
                          className={`px-3 py-2 rounded-xl text-sm transition-all duration-200 ${
                            isSelected
                              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                              : 'bg-white/10 text-slate-300 border border-white/20'
                          }`}
                        >
                          {food}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </Section>

            {/* Account Settings */}
            <Section id="account" title="Account Settings" icon={Shield}>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white font-medium mb-2">Account Created</label>
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {new Date(profileData.createdAt).toLocaleDateString()}
                    </div>
                  </div>

                  <div>
                    <label className="block text-white font-medium mb-2">Last Updated</label>
                    <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-300 border border-white/10 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      {new Date(profileData.lastUpdated).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-yellow-400 font-medium mb-1">Password Security</h4>
                      <p className="text-slate-300 text-sm">Keep your account secure with a strong password</p>
                    </div>
                    <button className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white px-4 py-2 rounded-xl hover:from-yellow-600 hover:to-orange-700 transition-all duration-200 flex items-center gap-2 font-medium">
                      <Lock className="w-4 h-4" />
                      Change Password
                    </button>
                  </div>
                </div>

                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-red-400 font-medium mb-1">Danger Zone</h4>
                      <p className="text-slate-300 text-sm">Permanently delete your account and all data</p>
                    </div>
                    <button className="bg-red-500 text-white px-4 py-2 rounded-xl hover:bg-red-600 transition-all duration-200 font-medium">
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            </Section>
          </div>
        </div>

        {/* Success Toast - would normally be a separate component */}
        {!isEditMode && (
          <div className="fixed bottom-6 right-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-xl shadow-lg opacity-0 pointer-events-none transition-opacity duration-300">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              <span>Profile updated successfully!</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}