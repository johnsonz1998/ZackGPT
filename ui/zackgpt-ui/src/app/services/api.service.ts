import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, Subject, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thread_id: string;
}

export interface Thread {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface HealthStatus {
  status: string;
  version: string;
  backend_connected: boolean;
  features: {
    websocket_chat: boolean;
    thread_management: boolean;
    memory_persistence: boolean;
    prompt_evolution: boolean;
  };
}

export interface SystemStats {
  total_threads: number;
  total_messages: number;
  evolution_stats: any;
  memory_stats: any;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000';
  private readonly wsUrl = 'ws://localhost:8000';
  
  private websocket: WebSocket | null = null;
  private clientId = this.generateClientId();
  
  // Observable subjects for real-time updates
  public connected$ = new BehaviorSubject<boolean>(false);
  public messages$ = new Subject<ChatMessage>();
  public typing$ = new BehaviorSubject<boolean>(false);
  public errors$ = new Subject<string>();
  
  constructor(private http: HttpClient) {
    this.checkHealth();
  }

  private generateClientId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Server Error ${error.status}: ${error.message}`;
    }
    
    console.error('API Error:', errorMessage);
    this.errors$.next(errorMessage);
    return throwError(() => errorMessage);
  }

  // =============================
  //         HEALTH CHECK
  // =============================

  checkHealth(): Observable<HealthStatus> {
    return this.http.get<HealthStatus>(`${this.baseUrl}/health`)
      .pipe(
        retry(2),
        catchError(this.handleError.bind(this))
      );
  }

  // =============================
  //      THREAD MANAGEMENT
  // =============================

  getThreads(): Observable<Thread[]> {
    return this.http.get<Thread[]>(`${this.baseUrl}/threads`)
      .pipe(
        retry(2),
        catchError(this.handleError.bind(this))
      );
  }

  createThread(title: string): Observable<Thread> {
    return this.http.post<Thread>(`${this.baseUrl}/threads`, { title })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  getThread(threadId: string): Observable<Thread> {
    return this.http.get<Thread>(`${this.baseUrl}/threads/${threadId}`)
      .pipe(
        retry(2),
        catchError(this.handleError.bind(this))
      );
  }

  deleteThread(threadId: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/threads/${threadId}`)
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  // =============================
  //      MESSAGE MANAGEMENT
  // =============================

  getMessages(threadId: string): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.baseUrl}/threads/${threadId}/messages`)
      .pipe(
        retry(2),
        catchError(this.handleError.bind(this))
      );
  }

  sendMessage(threadId: string, content: string): Observable<ChatMessage> {
    return this.http.post<ChatMessage>(`${this.baseUrl}/threads/${threadId}/messages`, {
      content,
      thread_id: threadId
    }).pipe(
      catchError(this.handleError.bind(this))
    );
  }

  // =============================
  //         WEBSOCKET
  // =============================

  connectWebSocket(): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      this.websocket = new WebSocket(`${this.wsUrl}/ws/${this.clientId}`);
      
      this.websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        this.connected$.next(true);
      };
      
      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          this.errors$.next('Failed to parse server message');
        }
      };
      
      this.websocket.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.connected$.next(false);
        this.typing$.next(false);
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000);
      };
      
      this.websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.connected$.next(false);
        this.errors$.next('WebSocket connection failed');
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.errors$.next('Failed to establish WebSocket connection');
    }
  }

  private handleWebSocketMessage(data: any): void {
    switch (data.type) {
      case 'message':
        this.messages$.next(data.data as ChatMessage);
        break;
        
      case 'typing':
        this.typing$.next(data.typing);
        break;
        
      case 'error':
        this.errors$.next(data.message);
        break;
        
      case 'messages':
        // Handle bulk messages (for thread loading)
        data.data.forEach((message: ChatMessage) => {
          this.messages$.next(message);
        });
        break;
        
      default:
        console.warn('Unknown WebSocket message type:', data.type);
    }
  }

  sendMessageViaWebSocket(threadId: string, content: string): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      const message = {
        action: 'send_message',
        thread_id: threadId,
        content: content
      };
      
      this.websocket.send(JSON.stringify(message));
    } else {
      this.errors$.next('WebSocket not connected');
      // Fallback to REST API
      this.sendMessage(threadId, content).subscribe({
        next: (response) => this.messages$.next(response),
        error: (error) => this.errors$.next(error)
      });
    }
  }

  loadMessagesViaWebSocket(threadId: string): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      const message = {
        action: 'get_messages',
        thread_id: threadId
      };
      
      this.websocket.send(JSON.stringify(message));
    } else {
      // Fallback to REST API
      this.getMessages(threadId).subscribe({
        next: (messages) => {
          messages.forEach(msg => this.messages$.next(msg));
        },
        error: (error) => this.errors$.next(error)
      });
    }
  }

  disconnectWebSocket(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
      this.connected$.next(false);
    }
  }

  // =============================
  //         SYSTEM STATS
  // =============================

  getSystemStats(): Observable<SystemStats> {
    return this.http.get<SystemStats>(`${this.baseUrl}/stats`)
      .pipe(
        retry(2),
        catchError(this.handleError.bind(this))
      );
  }

  // =============================
  //          UTILITIES
  // =============================

  isConnected(): boolean {
    return this.connected$.value;
  }

  getConnectionStatus(): Observable<boolean> {
    return this.connected$.asObservable();
  }

  // Clean up resources
  ngOnDestroy(): void {
    this.disconnectWebSocket();
    this.connected$.complete();
    this.messages$.complete();
    this.typing$.complete();
    this.errors$.complete();
  }
} 