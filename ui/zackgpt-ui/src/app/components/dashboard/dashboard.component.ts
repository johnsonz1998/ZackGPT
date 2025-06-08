import { Component, OnInit, OnDestroy, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { 
  ApiService, 
  ChatMessage, 
  Thread, 
  HealthStatus, 
  SystemStats 
} from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy, OnChanges {
  @Input() selectedThread: Thread | null = null;
  
  // UI State
  connected = false;
  isTyping = false;
  currentMessage = '';
  selectedTab = 0;
  loading = false;
  error = '';

  // Data
  messages: ChatMessage[] = [];
  healthStatus: HealthStatus | null = null;
  systemStats: SystemStats | null = null;

  private subscriptions: Subscription[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.initializeConnections();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedThread'] && this.selectedThread) {
      this.loadThreadMessages();
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.apiService.disconnectWebSocket();
  }

  private initializeConnections(): void {
    // Subscribe to connection status
    this.subscriptions.push(
      this.apiService.getConnectionStatus().subscribe(connected => {
        this.connected = connected;
        if (connected && this.selectedThread) {
          this.loadThreadMessages();
        }
      })
    );

    // Subscribe to real-time messages
    this.subscriptions.push(
      this.apiService.messages$.subscribe(message => {
        if (this.selectedThread && message.thread_id === this.selectedThread.id) {
          // Check if message already exists to avoid duplicates
          const existingMessage = this.messages.find(m => m.id === message.id);
          if (!existingMessage) {
            this.messages.push(message);
            this.scrollToBottom();
          }
        }
      })
    );

    // Subscribe to typing indicator
    this.subscriptions.push(
      this.apiService.typing$.subscribe(typing => {
        this.isTyping = typing;
      })
    );

    // Subscribe to errors
    this.subscriptions.push(
      this.apiService.errors$.subscribe(error => {
        this.error = error;
        console.error('API Error:', error);
      })
    );

    // Initialize WebSocket connection
    this.apiService.connectWebSocket();
    
    // Load health status
    this.loadHealthStatus();
    
    // Load system stats
    this.loadSystemStats();
  }

  private loadHealthStatus(): void {
    this.apiService.checkHealth().subscribe({
      next: (health) => {
        this.healthStatus = health;
        console.log('Health check:', health);
      },
      error: (error) => {
        console.error('Health check failed:', error);
        this.healthStatus = {
          status: 'unhealthy',
          version: 'unknown',
          backend_connected: false,
          features: {
            websocket_chat: false,
            thread_management: false,
            memory_persistence: false,
            prompt_evolution: false
          }
        };
      }
    });
  }

  private loadSystemStats(): void {
    this.apiService.getSystemStats().subscribe({
      next: (stats) => {
        this.systemStats = stats;
      },
      error: (error) => {
        console.error('Failed to load system stats:', error);
      }
    });
  }

  private loadThreadMessages(): void {
    if (!this.selectedThread) return;
    
    this.loading = true;
    this.messages = [];
    this.error = '';

    if (this.connected) {
      // Use WebSocket for real-time loading
      this.apiService.loadMessagesViaWebSocket(this.selectedThread.id);
    } else {
      // Fallback to REST API
      this.apiService.getMessages(this.selectedThread.id).subscribe({
        next: (messages) => {
          this.messages = messages.sort((a, b) => 
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          );
          this.scrollToBottom();
          this.loading = false;
        },
        error: (error) => {
          console.error('Failed to load thread messages:', error);
          this.error = 'Failed to load messages';
          this.loading = false;
        }
      });
    }
  }

  sendMessage(): void {
    if (!this.currentMessage.trim() || !this.selectedThread || this.isTyping) {
      return;
    }

    const userMessage = this.currentMessage.trim();
    this.currentMessage = '';

    if (this.connected) {
      // Use WebSocket for real-time messaging
      this.apiService.sendMessageViaWebSocket(this.selectedThread.id, userMessage);
    } else {
      // Fallback to REST API
      this.apiService.sendMessage(this.selectedThread.id, userMessage).subscribe({
        next: (response) => {
          // Message will be added via the messages$ subscription
        },
        error: (error) => {
          console.error('Failed to send message:', error);
          this.error = 'Failed to send message';
        }
      });
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  refreshStats(): void {
    this.loadSystemStats();
  }

  clearError(): void {
    this.error = '';
  }

  reconnect(): void {
    this.apiService.connectWebSocket();
  }

  connect(): void {
    this.apiService.connectWebSocket();
  }

  formatTime(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString();
  }

  formatDate(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  getMessageClass(role: string): string {
    return role === 'user' ? 'user-message' : 'assistant-message';
  }

  trackMessage(index: number, message: ChatMessage): string {
    return message.id;
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.messages-container');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }
} 