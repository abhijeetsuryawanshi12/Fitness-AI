import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Settings, 
  User, 
  Send, 
  Paperclip,
  Mic, 
  FileText,
  X,
  Download,
  Upload,
  MessageSquare, // <-- Added for the history button
  Zap,
  Apple,
  Activity,
  Bot,
  Play,
  MoreVertical,
  Flame,
  Volume2,
  VolumeX
} from 'lucide-react'

import ReactMarkdown from 'react-markdown';

import api from '@/lib/api'
import Orb from '@/components/react_bits/Orb';

// Type Definitions
type Message = {
  id: string
  role: 'user' | 'ai'
  text: string
  timestamp: Date
  type?: 'text' | 'image' | 'audio' | 'document' | 'food-analysis'
  fileData?: any
  audioUrl?: string
}

type ChatSession = {
  _id: string;
  title: string;
  created_at: string;
};

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
        <div className="text-sm font-semibold text-white">{user.name || 'User'}</div>
        <div className="text-xs text-slate-300 flex items-center">
          <Flame className="w-3 h-3 mr-1 text-orange-400" />
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
      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl px-4 py-3 border border-white/20">
        <div className="flex space-x-1">
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              variants={typingVariants}
              animate="animate"
              className="w-2 h-2 bg-slate-400 rounded-full"
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
            <img src={message.fileData?.preview} alt="Uploaded" className="max-w-xs rounded-lg" />
            <p className="text-sm">{message.text}</p>
          </div>
        )
      case 'audio':
        return (
          <div className="flex items-center space-x-3 bg-black/20 rounded-lg p-3">
            <button onClick={() => onPlayAudio(message.audioUrl)} className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-all">
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
          <div className="flex items-center space-x-3 bg-black/20 rounded-lg p-3">
            <FileText className="w-6 h-6 opacity-70" />
            <div className="flex-1">
              <div className="text-sm font-medium">{message.fileData?.name}</div>
              <div className="text-xs opacity-70">{message.fileData?.size} KB</div>
            </div>
            <button className="p-1 hover:bg-white/10 rounded">
              <Download className="w-4 h-4" />
            </button>
          </div>
        )
      case 'food-analysis':
        return (
          <div className="space-y-3">
            {message.fileData?.image && <img src={message.fileData.image} alt="Food" className="max-w-xs rounded-lg" />}
            <div className="bg-black/20 rounded-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <Apple className="w-4 h-4 text-green-400" />
                <span className="text-sm font-medium text-slate-100">Nutrition Analysis</span>
              </div>
              <div className="prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{message.text}</ReactMarkdown>
              </div>
            </div>
          </div>
        )
      default:
        // Use dangerouslySetInnerHTML to render markdown
        // return <div dangerouslySetInnerHTML={{ __html: message.text.replace(/\n/g, '<br />') }} />;
        if (isUser) {
          return message.text; // User's text doesn't need markdown styling
        }
        return (
          <div className="prose prose-sm prose-invert max-w-none">
            <ReactMarkdown>{message.text}</ReactMarkdown>
          </div>
        )
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
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
        )}
        <div className="flex flex-col">
          <div className={`rounded-2xl px-4 py-3 text-white ${isUser ? 'bg-gradient-to-br from-blue-500 to-purple-600' : 'bg-white/10 backdrop-blur-lg border border-white/20'}`}>
              <div className={!isUser ? 'prose prose-sm prose-invert max-w-none' : ''}>
                {renderMessageContent()}
              </div>
          </div>
          <div className={`text-xs text-slate-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// File Upload Modal Component
function FileUploadModal({ isOpen, onClose, onUpload }) {
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => { e.preventDefault(); e.stopPropagation(); if (e.type === "dragenter" || e.type === "dragover") setDragActive(true); else if (e.type === "dragleave") setDragActive(false) }
  const handleDrop = (e) => { e.preventDefault(); e.stopPropagation(); setDragActive(false); if (e.dataTransfer.files && e.dataTransfer.files[0]) { onUpload(e.dataTransfer.files[0]); onClose() } }
  const handleFileSelect = (e) => { if (e.target.files && e.target.files[0]) { onUpload(e.target.files[0]); onClose() } }

  if (!isOpen) return null

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="bg-slate-800/80 backdrop-blur-lg border border-white/20 rounded-2xl p-6 w-96 mx-4 text-white" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Upload File</h3>
          <button onClick={onClose} className="p-1 text-slate-400 hover:bg-white/10 rounded"><X className="w-5 h-5" /></button>
        </div>
        <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-white/20'}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
          <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
          <p className="text-slate-300 mb-2">Drag and drop files here</p>
          <p className="text-sm text-slate-400">Supports images, audio, and documents</p>
          <input ref={fileInputRef} type="file" className="hidden" accept="image/*,audio/*,.pdf,.doc,.docx,.txt" onChange={handleFileSelect} />
          <button onClick={() => fileInputRef.current?.click()} className="mt-4 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all">Choose File</button>
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
      setLoading(true)
      api.get('/documents').then(res => setDocuments(res.data)).finally(() => setLoading(false))
    }
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
          <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} className="fixed right-0 top-0 h-full w-80 bg-slate-900/80 backdrop-blur-lg border-l border-white/20 z-50 flex flex-col">
            <div className="p-4 border-b border-white/20"><div className="flex items-center justify-between"><h3 className="text-lg font-semibold text-white">Documents</h3><button onClick={onClose} className="p-1 text-slate-300 hover:bg-white/10 rounded"><X className="w-5 h-5" /></button></div></div>
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? <div className="text-center py-8"><div className="animate-spin w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full mx-auto" /><p className="text-slate-400 mt-2">Loading documents...</p></div> : <div className="space-y-3">{documents.map(doc => <motion.div key={doc._id} whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.1)' }} className="p-3 bg-white/5 rounded-lg transition-colors cursor-pointer"><div className="flex items-start space-x-3"><FileText className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" /><div className="flex-1 min-w-0"><p className="text-sm font-medium text-white truncate">{doc.filename}</p><p className="text-xs text-slate-400">{doc.created_at && new Date(doc.created_at).toLocaleDateString()}</p></div><button className="p-1 text-slate-500 hover:text-white rounded"><MoreVertical className="w-4 h-4" /></button></div></motion.div>)}</div>}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// NEW: Chat History Sidebar
function ChatHistorySidebar({ isOpen, onClose, onSelectSession, onNewChat }) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api.get('/chat/sessions')
        .then(res => setSessions(res.data))
        .catch(err => console.error("Failed to fetch sessions:", err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
          <motion.div
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            className="fixed right-0 top-0 h-full w-80 bg-slate-900/80 backdrop-blur-lg border-l border-white/20 z-50 flex flex-col"
          >
            <div className="p-4 border-b border-white/20 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Chat History</h3>
              <button onClick={onClose} className="p-1 text-slate-300 hover:bg-white/10 rounded"><X className="w-5 h-5" /></button>
            </div>
            
            <div className="p-4 border-b border-white/10">
              <button 
                onClick={onNewChat}
                className="w-full flex items-center justify-center px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all text-sm font-semibold"
              >
                + New Chat
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full mx-auto" />
                  <p className="text-slate-400 mt-2">Loading history...</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {sessions.map(session => (
                    <motion.div 
                      key={session._id} 
                      onClick={() => onSelectSession(session._id)}
                      whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.1)' }} 
                      className="p-3 bg-white/5 rounded-lg transition-colors cursor-pointer"
                    >
                      <p className="text-sm text-white truncate">{session.title}</p>
                      <p className="text-xs text-slate-400 mt-1">{new Date(session.created_at).toLocaleDateString()}</p>
                    </motion.div>
                  ))}
                  {sessions.length === 0 && !loading && (
                    <p className="text-center text-slate-400 text-sm py-4">No past conversations found.</p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// Quick Actions Component
function QuickActions({ onAction }) {
  const actions = [
    { id: 'workout', label: 'Suggest Workout', icon: Activity, color: 'from-green-500 to-emerald-600' },
    { id: 'meal', label: 'Recommend Meal', icon: Apple, color: 'from-orange-500 to-red-600' },
    { id: 'progress', label: 'Check Progress', icon: Zap, color: 'from-blue-500 to-purple-600' }
  ]

  return (
    <div className="flex flex-wrap justify-center gap-2 px-4 py-2">
      {actions.map(action => (
        <motion.button key={action.id} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => onAction(action.label)} className={`flex items-center space-x-2 px-3 py-2 rounded-full text-white text-xs font-medium bg-gradient-to-r ${action.color} shadow-lg hover:shadow-xl transition-shadow`}>
          <action.icon className="w-3 h-3" />
          <span>{action.label}</span>
        </motion.button>
      ))}
    </div>
  )
}


export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showDocumentsSidebar, setShowDocumentsSidebar] = useState(false)
  const [recording, setRecording] = useState(false)
  const [soundEnabled, setSoundEnabled] = useState(true)

  // New state for chat history
  const [isHistorySidebarOpen, setIsHistorySidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  const messagesEndRef = useRef(null)
  const audioRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const recordingChunksRef = useRef([])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  // New handler to select a session
  const handleSelectSession = async (sessionId: string) => {
    if (sessionId === currentSessionId) {
      setIsHistorySidebarOpen(false);
      return;
    }

    setLoading(true);
    setMessages([]);
    setCurrentSessionId(sessionId);
    setIsHistorySidebarOpen(false);

    try {
      const response = await api.get(`/chat/sessions/${sessionId}/history`);
      const history = response.data;
      
      const formattedMessages = history.map((msg: any) => ({
        id: Math.random().toString(36).substr(2, 9),
        role: msg.type === 'human' ? 'user' : 'ai',
        text: msg.content,
        timestamp: new Date(),
        type: 'text',
      }));
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to fetch chat history:", error);
      setMessages([{ id: 'error-msg', role: 'ai', text: 'Sorry, I was unable to load the conversation history.', timestamp: new Date(), type: 'text' }]);
    } finally {
      setLoading(false);
    }
  };

  // New handler to start a new chat
  const handleNewChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    setInput('');
    setIsHistorySidebarOpen(false);
  };

  const sendMessage = async (text, type = 'text', fileData = null, originalFile = null) => {
      if (!text.trim() && !fileData) return

      const userMessage: Message = { id: Math.random().toString(36).substr(2, 9), role: 'user', text, timestamp: new Date(), type, fileData: originalFile ? { preview: URL.createObjectURL(originalFile) } : null };
      setMessages(prev => [...prev, userMessage])
      setInput('')
      setLoading(true)

      try {
        if (type === 'food-analysis') {
          const response = await api.post('/food/analyze', fileData);
          const aiMessage = { id: Math.random().toString(36).substr(2, 9), role: 'ai', text: response.data.analysis, timestamp: new Date(), type: 'food-analysis', fileData: { image: URL.createObjectURL(originalFile) } };
          setMessages(prev => [...prev, aiMessage]);
        } else if (type === 'audio') {
          const response = await api.post('/voice/chat', fileData);
          const aiMessage = { id: Math.random().toString(36).substr(2, 9), role: 'ai', text: response.data.ai_text, timestamp: new Date(), type: 'audio', audioUrl: `data:audio/mpeg;base64,${response.data.audio_b64}` };
          setMessages(prev => [...prev, aiMessage]);
          if (soundEnabled && audioRef.current && aiMessage.audioUrl) { audioRef.current.src = aiMessage.audioUrl; audioRef.current.play(); }
        } else {
          // MODIFIED: Text chat logic with session handling
          const response = await api.post('/chat/', { message: text, session_id: currentSessionId });
          
          if (!currentSessionId) {
            setCurrentSessionId(response.data.session_id);
          }
          
          const aiMessage = { id: Math.random().toString(36).substr(2, 9), role: 'ai', text: response.data.response, timestamp: new Date(), type: 'text' };
          setMessages(prev => [...prev, aiMessage]);
        }
      } catch (error) {
        console.error('Failed to send message:', error);
        const errorText = error.response ? `Error: ${error.response.status} - ${error.response.data?.detail || 'Please try again.'}` : 'A network error occurred. Please check your connection.';
        const errorMessage = { id: Math.random().toString(36).substr(2, 9), role: 'ai', text: errorText, timestamp: new Date(), type: 'text' };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setLoading(false);
      }
    }
  
    const handleFileUpload = (file) => {
      const formData = new FormData();
      if (file.type.startsWith('image/')) {
        formData.append('image_file', file);
        sendMessage(`Analyze this food image: ${file.name}`, 'food-analysis', formData, file);
      } else if (file.type.startsWith('audio/')) {
        formData.append('file', file);
        sendMessage(`Voice message: ${file.name}`, 'audio', formData, file);
      } else {
        const userMessage = { id: Math.random().toString(36).substr(2, 9), role: 'user', text: `Uploaded document: ${file.name}`, timestamp: new Date(), type: 'document', fileData: { name: file.name, size: Math.round(file.size / 1024) } };
        setMessages(prev => [...prev, userMessage]);
        formData.append('file', file);
        api.post('/documents/upload', formData).then(response => console.log('Document uploaded:', response.data.message)).catch(err => console.error("Document upload failed", err));
      }
    }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      recordingChunksRef.current = []
      mediaRecorderRef.current.ondataavailable = (event) => event.data.size > 0 && recordingChunksRef.current.push(event.data)
      mediaRecorderRef.current.onstop = () => { const blob = new Blob(recordingChunksRef.current, { type: 'audio/wav' }); const file = new File([blob], 'recording.wav', { type: 'audio/wav' }); handleFileUpload(file); stream.getTracks().forEach(track => track.stop()) }
      mediaRecorderRef.current.start()
      setRecording(true)
    } catch (error) { console.error('Failed to start recording:', error) }
  }

  const stopRecording = () => { if (mediaRecorderRef.current && recording) { mediaRecorderRef.current.stop(); setRecording(false) } }

  return (
    <div className="relative h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Background Orb */}
      <div className="absolute inset-0 z-0">
        <Orb
          hoverIntensity={0.5}
          rotateOnHover={true}
          hue={240} // Matching blue/purple theme
          forceHoverState={false}
        />
      </div>

      {/* UI Content Layer */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-white/5 backdrop-blur-lg border-b border-white/20 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
            <div><h1 className="text-xl font-bold">AI Fitness Coach</h1><div className="flex items-center space-x-2 text-sm text-slate-300"><div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /><span>Online</span></div></div>
          </div>
          <div className="flex items-center space-x-3">
            <button onClick={() => setSoundEnabled(!soundEnabled)} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">{soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}</button>
            <button onClick={() => setShowDocumentsSidebar(true)} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"><FileText className="w-5 h-5" /></button>
            <button onClick={() => setIsHistorySidebarOpen(true)} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"><MessageSquare className="w-5 h-5" /></button>
            <button className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"><Settings className="w-5 h-5" /></button>
            <UserProfile />
          </div>
        </motion.div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map(message => <MessageBubble key={message.id} message={message} onPlayAudio={(url) => { if(audioRef.current) { audioRef.current.src = url; audioRef.current.play() }}}/>)}
          </AnimatePresence>
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        {messages.length === 0 && !currentSessionId && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="px-4 py-2">
            <p className="text-center text-slate-400 text-sm mb-3">Get started with these quick actions:</p>
            <QuickActions onAction={sendMessage} />
          </motion.div>
        )}

        {/* Input Area */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-white/5 backdrop-blur-lg border-t border-white/20 p-4">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(input) }} className="flex items-end space-x-3">
            <div className="flex space-x-2">
              <motion.button type="button" whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => setShowUploadModal(true)} className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"><Paperclip className="w-5 h-5" /></motion.button>
              <motion.button type="button" whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={recording ? stopRecording : startRecording} className={`p-2 rounded-lg transition-colors ${recording ? 'text-red-400 bg-red-500/10 animate-pulse' : 'text-slate-300 hover:text-red-400 hover:bg-red-500/10'}`}><Mic className="w-5 h-5" /></motion.button>
            </div>
            <div className="flex-1 relative">
              <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask me anything about fitness, nutrition, or health..." className="w-full px-4 py-3 pr-12 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" disabled={loading} />
            </div>
            <motion.button type="submit" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} disabled={!input.trim() || loading} className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"><Send className="w-5 h-5" /></motion.button>
          </form>
        </motion.div>
      </div>

      {/* Modals and Sidebars remain here as they use `fixed` positioning */}
      <FileUploadModal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)} onUpload={handleFileUpload} />
      <DocumentsSidebar isOpen={showDocumentsSidebar} onClose={() => setShowDocumentsSidebar(false)} />
      <ChatHistorySidebar isOpen={isHistorySidebarOpen} onClose={() => setIsHistorySidebarOpen(false)} onSelectSession={handleSelectSession} onNewChat={handleNewChat} />
      <audio ref={audioRef} className="hidden" />
    </div>
  )
}