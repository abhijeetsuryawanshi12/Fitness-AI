import { useState, useEffect } from 'react';
import {
  User, Edit3, Save, X, Camera, Mail, Calendar, Users, Ruler, Weight,
  Briefcase, Target, Clock, Dumbbell, Heart, Shield, Battery, Moon,
  Utensils, Wine, Cigarette, Star, Lock, MapPin, Phone, CheckCircle
} from 'lucide-react';
import api from '@/lib/api';

const InfoField = ({ label, value, isEditing, onChange, name, type = "text", as: Component = 'input', options = [], ...props }) => (
  <div>
    <label className="block text-sm font-medium text-slate-300 mb-1">{label}</label>
    {isEditing ? (
      Component === 'input' ? (
        <input
          type={type}
          name={name}
          value={value || ''}
          onChange={onChange}
          className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...props}
        />
      ) : Component === 'select' ? (
        <select
          name={name}
          value={value || ''}
          onChange={onChange}
          className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...props}
        >
          {options.map(opt => <option key={opt} value={opt} className="text-black">{opt}</option>)}
        </select>
      ) : (
        <textarea
          name={name}
          value={Array.isArray(value) ? value.join(', ') : value || ''}
          onChange={onChange}
          className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...props}
        />
      )
    ) : (
      <div className="bg-white/5 rounded-xl px-4 py-3 text-slate-200 border border-white/10 min-h-[50px]">
        {Array.isArray(value) ? value.join(', ') : value || <span className="text-slate-400">Not set</span>}
      </div>
    )}
  </div>
);


export default function ProfilePage() {
  const [isEditMode, setIsEditMode] = useState(false)
  const [activeSection, setActiveSection] = useState('personal')
  const [profileData, setProfileData] = useState(null)
  const [editData, setEditData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await api.get('/profile/me');
        setProfileData(data);
        setEditData(data);
      } catch (error) {
        console.error("Failed to fetch profile", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const sections = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'fitness', label: 'Fitness Goals', icon: Target },
    { id: 'health', label: 'Health & Medical', icon: Heart },
    { id: 'diet', label: 'Diet & Nutrition', icon: Utensils },
    { id: 'account', label: 'Account Settings', icon: Shield }
  ]

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let finalValue = value;
    if (type === 'number' || type === 'range') finalValue = Number(value);
    if (name === 'medical_conditions' || name === 'injuries' || name === 'favorite_foods') {
      finalValue = value.split(',').map(s => s.trim());
    }
    setEditData(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { data } = await api.put('/profile/me', editData);
      setProfileData(data);
      setEditData(data);
      setIsEditMode(false);
    } catch (error) {
      console.error("Failed to update profile", error);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditData({ ...profileData })
    setIsEditMode(false)
  }

  const getInitials = (name = "") => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!profileData) return <div>Failed to load profile.</div>;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-white/20">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
          <div className="relative">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-2xl font-bold text-white">
              {getInitials(profileData.name)}
            </div>
            {isEditMode && <button className="absolute -bottom-1 -right-1 bg-blue-500 rounded-full p-2 hover:bg-blue-600"><Camera className="w-4 h-4 text-white" /></button>}
          </div>

          <div className="flex-1">
            <h1 className="text-3xl font-bold text-white mb-2">{profileData.name}</h1>
            <div className="flex items-center gap-4 text-slate-300">
              <div className="flex items-center gap-2"><Briefcase className="w-4 h-4" /><span>{profileData.profession || "Profession not set"}</span></div>
              <div className="flex items-center gap-2"><MapPin className="w-4 h-4" /><span>Location not set</span></div>
            </div>
          </div>

          <div className="flex gap-3">
            {isEditMode ? (
              <>
                <button onClick={handleSave} className="bg-green-500 text-white px-6 py-3 rounded-xl flex items-center gap-2 font-medium"><Save className="w-4 h-4" />{saving ? 'Saving...' : 'Save'}</button>
                <button onClick={handleCancel} className="bg-white/10 text-white px-6 py-3 rounded-xl flex items-center gap-2 font-medium"><X className="w-4 h-4" />Cancel</button>
              </>
            ) : (
              <button onClick={() => setIsEditMode(true)} className="bg-blue-500 text-white px-6 py-3 rounded-xl flex items-center gap-2 font-medium"><Edit3 className="w-4 h-4" />Edit Profile</button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 sticky top-6">
            <h3 className="text-white font-semibold mb-4">Profile Sections</h3>
            <nav className="space-y-2">
              {sections.map(section => (
                <button key={section.id} onClick={() => setActiveSection(section.id)} className={`w-full text-left p-3 rounded-xl flex items-center gap-3 ${activeSection === section.id ? 'bg-blue-500/80 text-white' : 'text-slate-300 hover:bg-white/10'}`}>
                  <section.icon className="w-4 h-4" />{section.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="lg:col-span-3 space-y-6">
          {activeSection === 'personal' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 grid grid-cols-1 md:grid-cols-2 gap-6">
              <InfoField label="Full Name" name="name" value={editData.name} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Email" name="email" value={editData.email} isEditing={false} onChange={() => { }} />
              <InfoField label="Age" name="age" type="number" value={editData.age} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Gender" name="gender" as="select" options={["Male", "Female", "Other"]} value={editData.gender} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Height (cm)" name="height" type="number" value={editData.height} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Weight (kg)" name="weight" type="number" value={editData.weight} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Profession" name="profession" value={editData.profession} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Phone" name="phone" value={editData.phone} isEditing={isEditMode} onChange={handleChange} />
            </div>
          )}

          {activeSection === 'fitness' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 grid grid-cols-1 md:grid-cols-2 gap-6">
              <InfoField label="Primary Goal" name="primary_goal" as="select" options={["Build Muscle", "Lose Fat", "Maintain Weight", "Improve Endurance"]} value={editData.primary_goal} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Goal Deadline" name="goal_deadline" as="select" options={["1 Month", "3 Months", "6 Months", "1 Year"]} value={editData.goal_deadline} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Workout Duration (mins)" name="workout_time_minutes" type="number" value={editData.workout_time_minutes} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Preferred Workout Time" name="preferred_workout_time" as="select" options={["Morning", "Afternoon", "Evening"]} value={editData.preferred_workout_time} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Workout Experience" name="workout_experience" as="select" options={["Beginner", "Intermediate", "Advanced"]} value={editData.workout_experience} isEditing={isEditMode} onChange={handleChange} />
            </div>
          )}

          {activeSection === 'health' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 grid grid-cols-1 md:grid-cols-2 gap-6">
              <InfoField label="Medical Conditions (comma-separated)" as="textarea" name="medical_conditions" value={editData.medical_conditions} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Injuries (comma-separated)" as="textarea" name="injuries" value={editData.injuries} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Energy Level (1-10)" name="energy_level" type="range" min="1" max="10" value={editData.energy_level} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Sleep Quality (1-10)" name="sleep_quality" type="range" min="1" max="10" value={editData.sleep_quality} isEditing={isEditMode} onChange={handleChange} />
            </div>
          )}

          {activeSection === 'diet' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 grid grid-cols-1 md:grid-cols-2 gap-6">
              <InfoField label="Diet Type" name="diet_type" as="select" options={["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free", "Other"]} value={editData.diet_type} isEditing={isEditMode} onChange={handleChange} />
              {editData.diet_type === 'Other' && <InfoField label="Other Diet Details" name="diet_type_other" value={editData.diet_type_other} isEditing={isEditMode} onChange={handleChange} />}
              <InfoField label="Meals Per Day" name="meals_per_day" type="number" value={editData.meals_per_day} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Smoking Habit" name="smoking_habit" as="select" options={["Non-smoker", "Light smoker", "Heavy smoker"]} value={editData.smoking_habit} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Alcohol Consumption" name="alcohol_consumption" as="select" options={["None", "Light", "Moderate", "Heavy"]} value={editData.alcohol_consumption} isEditing={isEditMode} onChange={handleChange} />
              <InfoField label="Favorite Foods (comma-separated)" as="textarea" name="favorite_foods" value={editData.favorite_foods} isEditing={isEditMode} onChange={handleChange} />
            </div>
          )}

          {activeSection === 'account' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 space-y-4">
              <InfoField label="Account Created" name="createdAt" value={new Date(profileData.created_at).toLocaleDateString()} isEditing={false} onChange={() => { }} />
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <h4 className="text-red-400 font-medium">Delete Account</h4>
                  <p className="text-slate-300 text-sm">This action is permanent and cannot be undone.</p>
                </div>
                <button className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium">Delete</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}