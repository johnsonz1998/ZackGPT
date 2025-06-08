import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

export interface ChatMessage {
  id?: string;
  timestamp: string;
  user_message: string;
  assistant_response?: string;
  response_time?: number;
  context?: any;
}

export interface ChatThread {
  id: string;
  title: string; // Changed from 'name' to 'title' to match backend
  created_at: string;
  updated_at: string;
  message_count: number;
  preview?: string; // Last message preview
}

export interface SystemStats {
  messages_sent: number;
  responses_generated: number;
  uptime: string;
  last_response_time: string;
  memory_entries: number;
  evolution_components: number;
  evolution_experiments: number;
  conversation_length: number;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface EvolutionStats {
  total_components: number;
  experiments: number;
  success_rates?: any;
  component_performance?: any;
}

export interface ZackGPTConfig {
  // Core Settings
  model_name: string;
  max_tokens: number;
  temperature: number;
  
  // Voice Settings
  voice_enabled: boolean;
  voice_model: string;
  tts_voice: string;
  
  // Memory Settings
  memory_enabled: boolean;
  max_memory_entries: number;
  
  // Evolution Settings
  evolution_enabled: boolean;
  evolution_frequency: number;
  
  // API Keys (masked for security)
  openai_api_key_masked: string;
  elevenlabs_api_key_masked: string;
  
  // Other settings
  debug_mode: boolean;
  log_level: string;
}

@Injectable({
  providedIn: 'root'
})
export class ZackgptApiService {
  private apiUrl = 'http://localhost:8000';  // Adjust based on your backend port
  private wsUrl = 'ws://localhost:8000/ws';      // WebSocket URL
  
  private socket$?: WebSocketSubject<any>;
  private messagesSubject$ = new Subject<any>();
  public messages$ = this.messagesSubject$.asObservable();

  constructor(private http: HttpClient) {}

  // HTTP API Methods
  getStats(): Observable<SystemStats> {
    return this.http.get<SystemStats>(`${this.apiUrl}/stats`);
  }

  getLogs(count: number = 100): Observable<LogEntry[]> {
    return this.http.get<LogEntry[]>(`${this.apiUrl}/logs?count=${count}`);
  }

  getConversationHistory(): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.apiUrl}/conversation`);
  }

  getEvolutionStats(): Observable<EvolutionStats> {
    return this.http.get<EvolutionStats>(`${this.apiUrl}/evolution`);
  }

  // Chat Thread Methods
  getThreads(): Observable<ChatThread[]> {
    return this.http.get<ChatThread[]>(`${this.apiUrl}/threads`);
  }

  createThread(title: string): Observable<ChatThread> {
    return this.http.post<ChatThread>(`${this.apiUrl}/threads`, { title });
  }

  getThreadMessages(threadId: string): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.apiUrl}/threads/${threadId}/messages`);
  }

  updateThread(threadId: string, updates: Partial<ChatThread>): Observable<ChatThread> {
    return this.http.patch<ChatThread>(`${this.apiUrl}/threads/${threadId}`, updates);
  }

  deleteThread(threadId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/threads/${threadId}`);
  }

  // Settings Methods
  getConfig(): Observable<ZackGPTConfig> {
    return this.http.get<ZackGPTConfig>(`${this.apiUrl}/config`);
  }

  updateConfig(config: Partial<ZackGPTConfig>): Observable<ZackGPTConfig> {
    return this.http.patch<ZackGPTConfig>(`${this.apiUrl}/config`, config);
  }

  resetConfig(): Observable<ZackGPTConfig> {
    return this.http.post<ZackGPTConfig>(`${this.apiUrl}/config/reset`, {});
  }

  // WebSocket Methods
  connect(): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket({
        url: this.wsUrl,
        openObserver: {
          next: () => {
            console.log('Connected to ZackGPT WebSocket');
          }
        },
        closeObserver: {
          next: () => {
            console.log('Disconnected from ZackGPT WebSocket');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
          }
        }
      });

      this.socket$.subscribe(
        (message) => this.messagesSubject$.next(message),
        (error) => console.error('WebSocket error:', error)
      );
    }
  }

  sendMessage(message: string, threadId?: string): void {
    if (this.socket$) {
      this.socket$.next({
        type: 'user_message',
        data: { message, thread_id: threadId }
      });
    }
  }

  requestStats(): void {
    if (this.socket$) {
      this.socket$.next({ type: 'get_stats' });
    }
  }

  requestLogs(): void {
    if (this.socket$) {
      this.socket$.next({ type: 'get_logs' });
    }
  }

  disconnect(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
} 