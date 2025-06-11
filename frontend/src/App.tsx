import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MessageSquare, Plus, Settings, Send, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { v4 as uuidv4 } from 'uuid';
import SettingsModal from './components/Settings';
import './App.css';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  thread_id: string;
}

interface Thread {
  id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  message_count: number;
}

interface WSMessage {
  type: string;
  data?: any;
  message?: string;
  typing?: boolean;
}

const API_BASE = '';
const WS_BASE = 'ws://localhost:8000';

function App() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [connected, setConnected] = useState(false);

  const [showSettings, setShowSettings] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const clientId = useRef(uuidv4());

  // Scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Auto-resize textarea
  const autoResize = useCallback((element: HTMLTextAreaElement) => {
    element.style.height = 'auto';
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`;
  }, []);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(`${WS_BASE}/ws/${clientId.current}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const wsMessage: WSMessage = JSON.parse(event.data);
      
      if (wsMessage.type === 'message' && wsMessage.data) {
        const message: ChatMessage = {
          ...wsMessage.data,
          timestamp: new Date(wsMessage.data.timestamp)
        };
        
        // Only add AI messages from WebSocket (user messages are added immediately when sent)
        if (message.role === 'assistant') {
          setMessages(prev => [...prev, message]);
          setIsTyping(false); // Hide loading when AI response arrives
        }
      } else if (wsMessage.type === 'typing') {
        setIsTyping(wsMessage.typing || false);
      } else if (wsMessage.type === 'error') {
        console.error('WebSocket error:', wsMessage.message);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    wsRef.current = ws;
  }, []);

  // Load threads from API
  const loadThreads = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/threads`);
      if (response.ok) {
        const threadsData = await response.json();
        setThreads(threadsData.map((t: any) => ({
          ...t,
          created_at: new Date(t.created_at),
          updated_at: new Date(t.updated_at)
        })));
      }
    } catch (error) {
      console.error('Failed to load threads:', error);
    }
  }, []);

  // Load messages for a thread
  const loadMessages = useCallback(async (threadId: string) => {
    try {
      const response = await fetch(`${API_BASE}/threads/${threadId}/messages`);
      if (response.ok) {
        const messagesData = await response.json();
        setMessages(messagesData.map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp)
        })));
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  }, []);

  // Create new thread
  const createNewThread = useCallback(async (initialMessage?: string) => {
    try {
      const response = await fetch(`${API_BASE}/threads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: initialMessage || 'New conversation' })
      });
      
      if (response.ok) {
        const newThread = await response.json();
        const thread = {
          ...newThread,
          created_at: new Date(newThread.created_at),
          updated_at: new Date(newThread.updated_at)
        };
        setThreads(prev => [thread, ...prev]);
        setSelectedThread(thread);
        setMessages([]);
        return thread;
      }
    } catch (error) {
      console.error('Failed to create thread:', error);
    }
    return null;
  }, []);

  // Send message
  const sendMessage = useCallback(async () => {
    if (!currentMessage.trim()) return;

    const messageContent = currentMessage.trim();
    let threadToUse = selectedThread;
    
    // Create new thread if none selected
    if (!threadToUse) {
      threadToUse = await createNewThread(messageContent.slice(0, 50));
      if (!threadToUse) return;
    }

    // Create and immediately show user message
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
      thread_id: threadToUse.id
    };
    
    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);

    // Show loading indicator immediately
    setIsTyping(true);

    // Clear input immediately
    setCurrentMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    // Send via WebSocket if connected
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'send_message',
        thread_id: threadToUse.id,
        content: messageContent,
        force_web_search: false
      }));
    }
  }, [currentMessage, selectedThread, createNewThread]);

  // Select thread
  const selectThread = useCallback((thread: Thread) => {
    setSelectedThread(thread);
    loadMessages(thread.id);
  }, [loadMessages]);

  // Delete thread
  const deleteThread = useCallback(async (threadId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    try {
      const response = await fetch(`${API_BASE}/threads/${threadId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setThreads(prev => prev.filter(t => t.id !== threadId));
        if (selectedThread?.id === threadId) {
          setSelectedThread(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete thread:', error);
    }
  }, [selectedThread]);

  // Handle key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  // Handle textarea input
  const handleTextareaChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCurrentMessage(e.target.value);
    autoResize(e.target);
  }, [autoResize]);

  // Initialize
  useEffect(() => {
    loadThreads();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [loadThreads, connectWebSocket]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <button 
            className="zackgpt-title"
            onClick={() => {
              setSelectedThread(null);
              setMessages([]);
            }}
          >
            ZackGPT
          </button>
          <button className="new-chat-btn" onClick={() => createNewThread()}>
            <Plus size={16} />
            New chat
          </button>
        </div>

        <div className="thread-list">
          {threads.map(thread => (
            <button
              key={thread.id}
              className={`thread-item ${selectedThread?.id === thread.id ? 'selected' : ''}`}
              onClick={() => selectThread(thread)}
            >
              <MessageSquare size={16} />
              <span className="thread-title">{thread.title}</span>
              <button
                className="delete-btn"
                onClick={(e) => deleteThread(thread.id, e)}
              >
                <X size={14} />
              </button>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <button 
            className="settings-btn"
            onClick={() => setShowSettings(true)}
          >
            <Settings size={16} />
            Settings
          </button>
          <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
            <div className="status-dot"></div>
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {!selectedThread ? (
          /* Welcome Screen */
          <div className="welcome-screen">
            <div className="welcome-content">
              <h1>Good to see you, Zack.</h1>
              <div className="input-container">
                <textarea
                  ref={textareaRef}
                  value={currentMessage}
                  onChange={handleTextareaChange}
                  onKeyDown={handleKeyPress}
                  placeholder="Message ZackGPT..."
                  className="message-input"
                  rows={1}
                />
                <button
                  className="send-btn"
                  onClick={sendMessage}
                  disabled={!currentMessage.trim()}
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Chat Interface */
          <div className="chat-interface">
            <div className="messages-container">
              {messages.map(message => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-content">
                    {message.role === 'assistant' ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      <p>{message.content}</p>
                    )}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="message assistant">
                  <div className="message-content loading">
                    <div className="loading-dots">
                      <div className="dot"></div>
                      <div className="dot"></div>
                      <div className="dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input">
              <div className="input-container">
                <textarea
                  ref={textareaRef}
                  value={currentMessage}
                  onChange={handleTextareaChange}
                  onKeyDown={handleKeyPress}
                  placeholder="Message ZackGPT..."
                  className="message-input"
                  rows={1}
                  disabled={isTyping}
                />
                <button
                  className="send-btn"
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || isTyping}
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </div>
  );
}

export default App;
