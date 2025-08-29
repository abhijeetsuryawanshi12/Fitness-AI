import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, User, Target, Heart, Utensils, Sparkles, Dumbbell } from 'lucide-react';
import api from '@/lib/api';
import { cn } from '@/lib/utils';

// --- Reusable UI Components for Onboarding ---

const ProgressBar = ({ current, total }: { current: number; total: number }) => {
  const progress = (current / total) * 100;
  return (
    <div className="w-full bg-slate-700/50 rounded-full h-2.5 mb-8">
      <motion.div
        className="bg-gradient-to-r from-blue-500 to-purple-600 h-2.5 rounded-full"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      />
    </div>
  );
};

const OptionCard = ({ label, icon, isSelected, onClick }: { label: string; icon?: React.ReactNode; isSelected: boolean; onClick: () => void }) => (
  <motion.button
    type="button"
    onClick={onClick}
    className={cn(
      "w-full text-left p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-4",
      isSelected
        ? "bg-blue-500/20 border-blue-500 shadow-lg"
        : "bg-white/5 border-white/20 hover:bg-white/10"
    )}
    whileHover={{ scale: 1.03 }}
    whileTap={{ scale: 0.98 }}
  >
    {icon && <div className="flex-shrink-0">{icon}</div>}
    <span className="font-medium">{label}</span>
  </motion.button>
);

const StepContainer = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    transition={{ duration: 0.3, ease: 'easeInOut' }}
    className="space-y-6"
  >
    {children}
  </motion.div>
);

const StepHeader = ({ icon: Icon, title, subtitle }: { icon: React.ElementType, title: string, subtitle: string }) => (
  <div className="text-center">
    <div className="inline-flex items-center justify-center w-12 h-12 bg-white/10 rounded-2xl mb-4 border border-white/20">
      <Icon className="w-6 h-6 text-blue-400" />
    </div>
    <h2 className="text-3xl font-bold text-white">{title}</h2>
    <p className="text-slate-300 mt-2">{subtitle}</p>
  </div>
);


// --- Main Onboarding Component ---

export default function Onboarding() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    age: 25,
    gender: "",
    height: 170,
    weight: 70,
    profession: "",
    primary_goal: "",
    goal_deadline: "",
    workout_time_minutes: 60,
    preferred_workout_time: "",
    workout_experience: "",
    medical_conditions_text: "None",
    injuries_text: "None",
    energy_level: 7,
    sleep_quality: 8,
    diet_type: "",
    diet_type_other: "",
    meals_per_day: 3,
    smoking_habit: "",
    alcohol_consumption: "",
    favorite_foods_text: ""
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const totalSteps = 6;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const isNumeric = type === 'number' || type === 'range';
    setFormData(prev => ({ ...prev, [name]: isNumeric ? Number(value) : value }));
  };

  const handleSelect = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const nextStep = () => setStep(s => Math.min(s + 1, totalSteps));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const handleSubmit = async () => {
    setLoading(true);
    const payload = {
      ...formData,
      medical_conditions: formData.medical_conditions_text.split(',').map(s => s.trim()).filter(Boolean),
      injuries: formData.injuries_text.split(',').map(s => s.trim()).filter(Boolean),
      favorite_foods: formData.favorite_foods_text.split(',').map(s => s.trim()).filter(Boolean),
    };
    // Remove temporary text fields from the payload
    delete (payload as any).medical_conditions_text;
    delete (payload as any).injuries_text;
    delete (payload as any).favorite_foods_text;

    try {
      await api.put('/profile/me', payload);
      navigate('/dashboard');
    } catch (error) {
      console.error("Failed to update profile", error);
      alert("There was an error saving your profile. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <StepContainer>
            <StepHeader icon={User} title="About You" subtitle="Let's start with the basics to personalize your experience." />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Age</label>
                <input type="number" name="age" value={formData.age} onChange={handleChange} className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Gender</label>
                <div className="grid grid-cols-2 gap-2">
                  <OptionCard label="Male" isSelected={formData.gender === 'Male'} onClick={() => handleSelect('gender', 'Male')} />
                  <OptionCard label="Female" isSelected={formData.gender === 'Female'} onClick={() => handleSelect('gender', 'Female')} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Height (cm)</label>
                <input type="number" name="height" value={formData.height} onChange={handleChange} className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Weight (kg)</label>
                <input type="number" name="weight" value={formData.weight} onChange={handleChange} className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">Profession</label>
                <input type="text" name="profession" value={formData.profession} onChange={handleChange} placeholder="e.g., Software Developer, Student" className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
            </div>
          </StepContainer>
        );
      case 2:
        return (
          <StepContainer>
            <StepHeader icon={Target} title="Your Fitness Goals" subtitle="What are you aiming to achieve?" />
            <div>
              <label className="block text-sm font-medium mb-2">Primary Goal</label>
              <div className="space-y-3">
                <OptionCard label="Build Muscle" isSelected={formData.primary_goal === 'Build Muscle'} onClick={() => handleSelect('primary_goal', 'Build Muscle')} />
                <OptionCard label="Lose Fat" isSelected={formData.primary_goal === 'Lose Fat'} onClick={() => handleSelect('primary_goal', 'Lose Fat')} />
                <OptionCard label="Maintain Weight" isSelected={formData.primary_goal === 'Maintain Weight'} onClick={() => handleSelect('primary_goal', 'Maintain Weight')} />
                <OptionCard label="Improve Endurance" isSelected={formData.primary_goal === 'Improve Endurance'} onClick={() => handleSelect('primary_goal', 'Improve Endurance')} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Goal Deadline</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <OptionCard label="1 Month" isSelected={formData.goal_deadline === '1 Month'} onClick={() => handleSelect('goal_deadline', '1 Month')} />
                <OptionCard label="3 Months" isSelected={formData.goal_deadline === '3 Months'} onClick={() => handleSelect('goal_deadline', '3 Months')} />
                <OptionCard label="6 Months" isSelected={formData.goal_deadline === '6 Months'} onClick={() => handleSelect('goal_deadline', '6 Months')} />
                <OptionCard label="1 Year" isSelected={formData.goal_deadline === '1 Year'} onClick={() => handleSelect('goal_deadline', '1 Year')} />
              </div>
            </div>
          </StepContainer>
        );
      case 3:
        return (
          <StepContainer>
            <StepHeader icon={Dumbbell} title="Workout Preferences" subtitle="How do you like to train?" />
            <div>
              <label className="block text-sm font-medium mb-2">Workout Experience</label>
              <div className="grid grid-cols-3 gap-3">
                <OptionCard label="Beginner" isSelected={formData.workout_experience === 'Beginner'} onClick={() => handleSelect('workout_experience', 'Beginner')} />
                <OptionCard label="Intermediate" isSelected={formData.workout_experience === 'Intermediate'} onClick={() => handleSelect('workout_experience', 'Intermediate')} />
                <OptionCard label="Advanced" isSelected={formData.workout_experience === 'Advanced'} onClick={() => handleSelect('workout_experience', 'Advanced')} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Preferred Workout Time</label>
              <div className="grid grid-cols-3 gap-3">
                <OptionCard label="Morning" isSelected={formData.preferred_workout_time === 'Morning'} onClick={() => handleSelect('preferred_workout_time', 'Morning')} />
                <OptionCard label="Afternoon" isSelected={formData.preferred_workout_time === 'Afternoon'} onClick={() => handleSelect('preferred_workout_time', 'Afternoon')} />
                <OptionCard label="Evening" isSelected={formData.preferred_workout_time === 'Evening'} onClick={() => handleSelect('preferred_workout_time', 'Evening')} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Workout Duration (minutes)</label>
              <input type="range" name="workout_time_minutes" min="15" max="180" step="15" value={formData.workout_time_minutes} onChange={handleChange} className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
              <div className="text-center mt-1 text-slate-300">{formData.workout_time_minutes} mins</div>
            </div>
          </StepContainer>
        );
      case 4:
        return (
          <StepContainer>
            <StepHeader icon={Heart} title="Health & Lifestyle" subtitle="This helps us create a safe and effective plan for you." />
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Energy Level (1-10)</label>
                <input type="range" name="energy_level" min="1" max="10" value={formData.energy_level} onChange={handleChange} className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
                <div className="text-center mt-1 text-slate-300">{formData.energy_level}</div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Sleep Quality (1-10)</label>
                <input type="range" name="sleep_quality" min="1" max="10" value={formData.sleep_quality} onChange={handleChange} className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
                <div className="text-center mt-1 text-slate-300">{formData.sleep_quality}</div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Existing Medical Conditions (comma-separated)</label>
                <textarea name="medical_conditions_text" value={formData.medical_conditions_text} onChange={handleChange} placeholder="e.g., Asthma, High Blood Pressure" className="w-full h-20 bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Past or Current Injuries (comma-separated)</label>
                <textarea name="injuries_text" value={formData.injuries_text} onChange={handleChange} placeholder="e.g., Knee sprain, Lower back pain" className="w-full h-20 bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
            </div>
          </StepContainer>
        );
      case 5:
        return (
          <StepContainer>
            <StepHeader icon={Utensils} title="Nutrition & Habits" subtitle="Tell us about your dietary preferences." />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Diet Type</label>
                <select name="diet_type" value={formData.diet_type} onChange={handleChange} className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none text-white">
                  <option className="text-black" value="">Select Diet...</option>
                  <option className="text-black" value="Anything">Anything</option>
                  <option className="text-black" value="Vegetarian">Vegetarian</option>
                  <option className="text-black" value="Vegan">Vegan</option>
                  <option className="text-black" value="Pescatarian">Pescatarian</option>
                  <option className="text-black" value="Keto">Keto</option>
                  <option className="text-black" value="Gluten-Free">Gluten-Free</option>
                  <option className="text-black" value="Other">Other</option>
                </select>
                {formData.diet_type === 'Other' && (
                  <input type="text" name="diet_type_other" value={formData.diet_type_other} onChange={handleChange} placeholder="Please specify" className="w-full mt-2 bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
                )}
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Meals Per Day</label>
                <input type="number" name="meals_per_day" min="1" max="10" value={formData.meals_per_day} onChange={handleChange} className="w-full bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Smoking Habit</label>
                <div className="grid grid-cols-3 gap-2">
                  <OptionCard label="None" isSelected={formData.smoking_habit === 'Non-smoker'} onClick={() => handleSelect('smoking_habit', 'Non-smoker')} />
                  <OptionCard label="Light" isSelected={formData.smoking_habit === 'Light smoker'} onClick={() => handleSelect('smoking_habit', 'Light smoker')} />
                  <OptionCard label="Heavy" isSelected={formData.smoking_habit === 'Heavy smoker'} onClick={() => handleSelect('smoking_habit', 'Heavy smoker')} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Alcohol Consumption</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <OptionCard label="None" isSelected={formData.alcohol_consumption === 'None'} onClick={() => handleSelect('alcohol_consumption', 'None')} />
                  <OptionCard label="Light" isSelected={formData.alcohol_consumption === 'Light'} onClick={() => handleSelect('alcohol_consumption', 'Light')} />
                  <OptionCard label="Moderate" isSelected={formData.alcohol_consumption === 'Moderate'} onClick={() => handleSelect('alcohol_consumption', 'Moderate')} />
                  <OptionCard label="Heavy" isSelected={formData.alcohol_consumption === 'Heavy'} onClick={() => handleSelect('alcohol_consumption', 'Heavy')} />
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Favorite Foods (comma-separated)</label>
              <textarea name="favorite_foods_text" value={formData.favorite_foods_text} onChange={handleChange} placeholder="e.g., Chicken breast, Broccoli, Oats" className="w-full h-20 bg-white/5 border border-white/20 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" />
            </div>
          </StepContainer>
        );
      case 6:
        return (
          <StepContainer>
            <StepHeader icon={Sparkles} title="You're All Set!" subtitle="Ready to start your personalized fitness journey?" />
            <div className="text-center text-slate-300">
              <p>We've gathered all the necessary information. Click finish to head to your dashboard and see your personalized setup!</p>
            </div>
          </StepContainer>
        );
      default:
        return null;
    }
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex flex-col items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-2xl">
        <div className="flex items-center gap-3 mb-4">
          <Dumbbell className="w-8 h-8 text-blue-400" />
          <span className="text-xl font-bold">Welcome to Fitness AI</span>
        </div>
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
          <ProgressBar current={step} total={totalSteps} />
          <AnimatePresence mode="wait">
            {renderStepContent()}
          </AnimatePresence>

          <div className="mt-8 flex justify-between items-center">
            <button
              onClick={prevStep}
              disabled={step === 1 || loading}
              className="px-6 py-3 rounded-xl flex items-center gap-2 text-slate-300 hover:text-white bg-white/10 hover:bg-white/20 transition-all disabled:opacity-50"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            {step < totalSteps ? (
              <button
                onClick={nextStep}
                className="px-6 py-3 rounded-xl flex items-center gap-2 text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-3 rounded-xl flex items-center gap-2 text-white bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 transition-all transform hover:scale-105 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Finish & Go to Dashboard'}
                <Sparkles className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}