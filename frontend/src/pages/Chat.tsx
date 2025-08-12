import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Settings, 
  User, 
  Send, 
  Camera, 
  Mic, 
  FileText, 
  Image,
  File,
  Volume2,
  VolumeX,
  Paperclip,
  X,
  Download,
  Eye,
  Trash2,
  Upload,
  MessageSquare,
  Zap,
  Apple,
  Activity,
  Bot,
  Play,
  Pause,
  MoreVertical,
  Flame
} from 'lucide-react'

// Mock API - replace with your actual API
const api = {
  post: (endpoint, data) => {
    const responses = {
      '/chat/': { data: { response: "That's a great question! I'd recommend starting with a 20-minute cardio workout followed by some strength training. Would you like me to create a specific plan for you?" }},
      '/food/analyze': { data: { analysis: "This appears to be a healthy salad with mixed greens, tomatoes, and grilled chicken. Estimated calories: 350-400. Great source of protein (25g) and fiber. Perfect for weight management!" }},
      '/voice/chat': { data: { user_text: "What's my workout plan for today?", ai_text: "Today I recommend a full-body workout focusing on compound movements. Start with 5 minutes warm-up, then squats, push-ups, and planks.", audio_b64: "base64audiodata..." }},
      '/documents/upload': { data: { message: 'File uploaded successfully' }},
      '/documents': { data: [
        { _id: '1', filename: 'Workout_Plan_Week1.pdf', created_at: '2024-01-15T10:30:00Z' },
        { _id: '2', filename: 'Nutrition_Guide.pdf', created_at: '2024-01-10T14:20:00Z' }
      ]}
    }
    return Promise.resolve(responses[endpoint] || { data: {} })
  },
  get: (endpoint) => {
    const responses = {
      '/documents': { data: [
        { _id: '1', filename: 'Workout_Plan_Week1.pdf', created_at: '2024-01-15T10:30:00Z' },
        { _id: '2', filename: 'Nutrition_Guide.pdf', created_at: '2024-01-10T14:20:00Z' }
      ]},
      '/profile/me': { data: { name: 'Alex Johnson', streak: 12, avatar: null }}
    }
    return Promise.resolve(responses[endpoint] || { data: {} })
  }
}

type Message = {
  id: string
  role: 'user' | 'ai'
  text: string
  timestamp: Date
  type?: 'text' | 'image' | 'audio' | 'document' | 'food-analysis'
  fileData?: any
  audioUrl?: string
}

type Document = { 
  _id: string
  filename: string 
  created_at?: string 
}

const messageVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { duration: 0.3, ease: "easeOut" }
  },
  exit: { 
    opacity: 0, 
    y: -10, 
    scale: 0.95,
    transition: { duration: 0.2 }
  }
}

const typingVariants = {
  animate: {
    scale: [1, 1.2, 1],
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut"
    }
  }
}

// User Profile Component
function UserProfile() {
  const [user, setUser] = useState({ name: '', streak: 0 })
  
  useEffect(() => {
    api.get('/profile/me').then(res => setUser(res.data))
  }, [])

  return (
    <div className="flex items-center space-x-3">
      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
        <User className="w-5 h-5 text-white" />
      </div>
      <div>
        <div className="text-sm font-semibold text-gray-800">{user.name || 'User'}</div>
        <div className="text-xs text-gray-500 flex items-center">
          <Flame className="w-3 h-3 mr-1 text-orange-500" />
          {user.streak} day streak
        </div>
      </div>
    </div>
  )
}

// Typing Indicator Component
function TypingIndicator() {
  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      className="flex items-center space-x-2 p-4"
    >
      <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="bg-gray-100 rounded-2xl px-4 py-3">
        <div className="flex space-x-1">
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              variants={typingVariants}
              animate="animate"
              className="w-2 h-2 bg-gray-400 rounded-full"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

// Message Component
function MessageBubble({ message, onPlayAudio }) {
  const isUser = message.role === 'user'
  
  const renderMessageContent = () => {
    switch (message.type) {
      case 'image':
        return (
          <div className="space-y-2">
            <img 
              src={message.fileData?.preview} 
              alt="Uploaded" 
              className="max-w-xs rounded-lg"
            />
            <p className="text-sm">{message.text}</p>
          </div>
        )
      case 'audio':
        return (
          <div className="flex items-center space-x-3 bg-white bg-opacity-20 rounded-lg p-3">
            <button
              onClick={() => onPlayAudio(message.audioUrl)}
              className="p-2 bg-white bg-opacity-30 rounded-full hover:bg-opacity-50 transition-all"
            >
              <Play className="w-4 h-4" />
            </button>
            <div className="flex-1">
              <div className="text-xs opacity-70">Voice Message</div>
              <div className="text-sm">{message.text}</div>
            </div>
          </div>
        )
      case 'document':
        return (
          <div className="flex items-center space-x-3 bg-white bg-opacity-20 rounded-lg p-3">
            <FileText className="w-6 h-6 opacity-70" />
            <div className="flex-1">
              <div className="text-sm font-medium">{message.fileData?.name}</div>
              <div className="text-xs opacity-70">{message.fileData?.size} KB</div>
            </div>
            <button className="p-1 hover:bg-white hover:bg-opacity-30 rounded">
              <Download className="w-4 h-4" />
            </button>
          </div>
        )
      case 'food-analysis':
        return (
          <div className="space-y-3">
            {message.fileData?.image && (
              <img 
                src={message.fileData.image} 
                alt="Food" 
                className="max-w-xs rounded-lg"
              />
            )}
            <div className="bg-white bg-opacity-20 rounded-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <Apple className="w-4 h-4" />
                <span className="text-sm font-medium">Nutrition Analysis</span>
              </div>
              <p className="text-sm">{message.text}</p>
            </div>
          </div>
        )
      default:
        return <p>{message.text}</p>
    }
  }

  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-start space-x-3 max-w-xs lg:max-w-md ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {!isUser && (
          <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
        )}
        
        <div className="flex flex-col">
          <div className={`rounded-2xl px-4 py-3 ${
            isUser 
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' 
              : 'bg-white shadow-md border border-gray-100 text-gray-800'
          }`}>
            {renderMessageContent()}
          </div>
          
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// File Upload Component
function FileUploadModal({ isOpen, onClose, onUpload }) {
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0])
      onClose()
    }
  }

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0])
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl p-6 w-96 mx-4"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Upload File</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600 mb-2">Drag and drop files here, or click to browse</p>
          <p className="text-sm text-gray-400">Supports images, audio, documents, and PDFs</p>
          
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*,audio/*,.pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Choose File
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Documents Sidebar
function DocumentsSidebar({ isOpen, onClose }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadDocuments()
    }
  }, [isOpen])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/documents')
      setDocuments(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-30 z-40"
            onClick={onClose}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className="fixed right-0 top-0 h-full w-80 bg-white shadow-xl z-50 flex flex-col"
          >
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Documents</h3>
                <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto" />
                  <p className="text-gray-500 mt-2">Loading documents...</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map(doc => (
                    <motion.div
                      key={doc._id}
                      whileHover={{ scale: 1.02 }}
                      className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start space-x-3">
                        <FileText className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {doc.filename}
                          </p>
                          <p className="text-xs text-gray-500">
                            {doc.created_at && new Date(doc.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <button className="p-1 hover:bg-gray-200 rounded">
                          <MoreVertical className="w-4 h-4 text-gray-400" />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Quick Actions Component
function QuickActions({ onAction }) {
  const actions = [
    { id: 'workout', label: 'Suggest Workout', icon: Activity, color: 'from-green-500 to-emerald-600' },
    { id: 'meal', label: 'Recommend Meal', icon: Apple, color: 'from-orange-500 to-red-600' },
    { id: 'progress', label: 'Check Progress', icon: Zap, color: 'from-blue-500 to-purple-600' }
  ]

  return (
    <div className="flex space-x-2 px-4 py-2">
      {actions.map(action => (
        <motion.button
          key={action.id}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onAction(action.label)}
          className={`flex items-center space-x-2 px-3 py-2 rounded-full text-white text-xs font-medium bg-gradient-to-r ${action.color} shadow-lg hover:shadow-xl transition-shadow`}
        >
          <action.icon className="w-3 h-3" />
          <span>{action.label}</span>
        </motion.button>
      ))}
    </div>
  )
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showDocumentsSidebar, setShowDocumentsSidebar] = useState(false)
  const [recording, setRecording] = useState(false)
  const [soundEnabled, setSoundEnabled] = useState(true)
  
  const messagesEndRef = useRef(null)
  const audioRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const recordingChunksRef = useRef([])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const generateMessageId = () => Math.random().toString(36).substr(2, 9)

  const sendMessage = async (text, type = 'text', fileData = null) => {
    if (!text.trim() && !fileData) return

    const userMessage = {
      id: generateMessageId(),
      role: 'user',
      text,
      timestamp: new Date(),
      type,
      fileData
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      let response
      if (type === 'food-analysis') {
        response = await api.post('/food/analyze', fileData)
        const aiMessage = {
          id: generateMessageId(),
          role: 'ai',
          text: response.data.analysis,
          timestamp: new Date(),
          type: 'food-analysis',
          fileData: { image: fileData.get('image_url') || URL.createObjectURL(fileData.get('image_file')) }
        }
        setMessages(prev => [...prev, aiMessage])
      } else if (type === 'audio') {
        response = await api.post('/voice/chat', fileData)
        const aiMessage = {
          id: generateMessageId(),
          role: 'ai',
          text: response.data.ai_text,
          timestamp: new Date(),
          type: 'audio',
          audioUrl: `data:audio/mpeg;base64,${response.data.audio_b64}`
        }
        setMessages(prev => [...prev, aiMessage])
        
        if (soundEnabled && audioRef.current) {
          audioRef.current.src = aiMessage.audioUrl
          audioRef.current.play()
        }
      } else {
        response = await api.post('/chat/', { message: text })
        const aiMessage = {
          id: generateMessageId(),
          role: 'ai',
          text: response.data.response,
          timestamp: new Date(),
          type: 'text'
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = {
        id: generateMessageId(),
        role: 'ai',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleFormSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleFileUpload = (file) => {
    const formData = new FormData()
    
    if (file.type.startsWith('image/')) {
      // Handle as food analysis
      formData.append('image_file', file)
      sendMessage(`Analyze this food image: ${file.name}`, 'food-analysis', formData)
    } else if (file.type.startsWith('audio/')) {
      // Handle as voice message
      formData.append('file', file)
      sendMessage(`Voice message: ${file.name}`, 'audio', formData)
    } else {
      // Handle as document
      const userMessage = {
        id: generateMessageId(),
        role: 'user',
        text: `Uploaded document: ${file.name}`,
        timestamp: new Date(),
        type: 'document',
        fileData: { name: file.name, size: Math.round(file.size / 1024) }
      }
      setMessages(prev => [...prev, userMessage])
      
      // Upload to server
      formData.append('file', file)
      api.post('/documents/upload', formData)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      recordingChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordingChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(recordingChunksRef.current, { type: 'audio/wav' })
        const file = new File([blob], 'recording.wav', { type: 'audio/wav' })
        handleFileUpload(file)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop()
      setRecording(false)
    }
  }

  const handleQuickAction = (action) => {
    sendMessage(action)
  }

  const playAudio = (audioUrl) => {
    if (audioRef.current) {
      audioRef.current.src = audioUrl
      audioRef.current.play()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white shadow-sm border-b border-gray-200 p-4 flex items-center justify-between"
      >
        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-800">AI Fitness Coach</h1>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Online</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>
          <button
            onClick={() => setShowDocumentsSidebar(true)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <FileText className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
          </button>
          <UserProfile />
        </div>
      </motion.div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map(message => (
            <MessageBubble 
              key={message.id} 
              message={message} 
              onPlayAudio={playAudio}
            />
          ))}
        </AnimatePresence>
        
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-4 py-2"
        >
          <p className="text-center text-gray-500 text-sm mb-3">
            Get started with these quick actions:
          </p>
          <QuickActions onAction={handleQuickAction} />
        </motion.div>
      )}

      {/* Input Area */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white border-t border-gray-200 p-4"
      >
        <form onSubmit={handleFormSubmit} className="flex items-end space-x-3">
          {/* Attachment Buttons */}
          <div className="flex space-x-2">
            <motion.button
              type="button"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowUploadModal(true)}
              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Paperclip className="w-5 h-5" />
            </motion.button>
            
            <motion.button
              type="button"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={recording ? stopRecording : startRecording}
              className={`p-2 rounded-lg transition-colors ${
                recording 
                  ? 'text-red-600 bg-red-50 animate-pulse' 
                  : 'text-gray-500 hover:text-red-600 hover:bg-red-50'
              }`}
            >
              <Mic className="w-5 h-5" />
            </motion.button>
          </div>

          {/* Message Input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about fitness, nutrition, or health..."
              className="w-full px-4 py-3 pr-12 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              disabled={loading}
            />
          </div>

          {/* Send Button */}
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!input.trim() || loading}
            className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </form>
      </motion.div>

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleFileUpload}
      />

      {/* Documents Sidebar */}
      <DocumentsSidebar
        isOpen={showDocumentsSidebar}
        onClose={() => setShowDocumentsSidebar(false)}
      />

      {/* Hidden Audio Element */}
      <audio ref={audioRef} className="hidden" />
    </div>
  )
}