import { Component, OnInit, OnDestroy, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { marked } from 'marked';

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
  @Output() threadCreated = new EventEmitter<Thread>();
  
  // UI State
  connected = false;
  isTyping = false;
  currentMessage = '';
  selectedTab = 0;
  loading = false;
  error = '';
  developerMode = false;
  showThinking = false;
  showCopyButton: string | null = null;
  
  // Web Search Tools
  showToolsMenu = false;
  forceWebSearch = false;

  // Data
  messages: ChatMessage[] = [];
  healthStatus: HealthStatus | null = null;
  systemStats: SystemStats | null = null;

  // Track processed messages to prevent duplicates
  private processedMessageIds = new Set<string>();
  private subscriptions: Subscription[] = [];
  private scrollTimeout: any;
  private messagesContainer!: HTMLElement;

  constructor(private apiService: ApiService) {
    // Configure marked for better formatting
    marked.setOptions({
      gfm: true,
      breaks: true,
      silent: true
    });
  }

  ngOnInit(): void {
    this.initializeConnections();
    this.setupScrollbarBehavior();
    
    // Initialize scrollbar functionality after view init
    setTimeout(() => {
      this.initializeScrollbar();
    }, 100);

    // Close tools menu when clicking outside
    document.addEventListener('click', (event) => {
      if (this.showToolsMenu) {
        this.showToolsMenu = false;
      }
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedThread'] && this.selectedThread) {
      // Only load if this is actually a different thread
      const previousThread = changes['selectedThread'].previousValue;
      if (!previousThread || previousThread.id !== this.selectedThread.id) {
        this.loadThreadMessages();
      }
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.apiService.disconnectWebSocket();
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
  }

  private initializeConnections(): void {
    // Subscribe to connection status
    this.subscriptions.push(
      this.apiService.getConnectionStatus().subscribe(connected => {
        this.connected = connected;
        // Don't auto-reload messages on connection change to prevent duplicates
        // Messages will be loaded via ngOnChanges when thread is selected
      })
    );

    // Subscribe to real-time messages
    this.subscriptions.push(
      this.apiService.messages$.subscribe(message => {
        if (this.selectedThread && message.thread_id === this.selectedThread.id) {
          // Clear loading state when first message arrives via WebSocket
          if (this.loading) {
            this.loading = false;
          }
          
          // Hide thinking indicator when we receive a message
          if (message.role === 'assistant') {
            this.showThinking = false;
            this.isTyping = false;
          }
          
          // Create a unique message key for tracking
          const messageKey = `${message.id || `${message.content}-${message.role}-${message.timestamp}`}`;
          
          // Check if we've already processed this exact message
          if (this.processedMessageIds.has(messageKey)) {
            return; // Skip if already processed
          }
          
          // Additional duplicate check by content and role for messages without IDs
          const isDuplicate = this.messages.some(existingMsg => {
            // Check by ID first (most reliable)
            if (message.id && existingMsg.id && message.id === existingMsg.id) {
              return true;
            }
            
            // Check by exact content and role match
            if (message.content === existingMsg.content && 
                message.role === existingMsg.role) {
              return true;
            }
            
            return false;
          });
          
          if (!isDuplicate) {
            this.messages.push(message);
            this.processedMessageIds.add(messageKey);
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
    
    // Load developer mode setting
    this.loadDeveloperMode();
    
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

  private loadDeveloperMode(): void {
    // Load developer mode from backend config
    this.apiService.getConfig().subscribe({
      next: (config) => {
        this.developerMode = config.debug_mode;
      },
      error: () => {
        this.developerMode = false;
      }
    });
  }

  private loadThreadMessages(): void {
    if (!this.selectedThread) return;
    
    // Clear everything for a fresh start
    this.processedMessageIds.clear();
    this.messages = [];
    this.loading = false;
    this.error = '';
    
    // If it's a draft thread, just clear messages and don't load anything
    if (this.selectedThread.isDraft) {
      return;
    }
    
    this.loading = true;

    if (this.connected) {
      // Use WebSocket for real-time loading
      this.apiService.loadMessagesViaWebSocket(this.selectedThread.id);
      
      // Set a timeout to clear loading state (for empty threads or no response)
      setTimeout(() => {
        if (this.loading) {
          this.loading = false;
          console.log('Message loading timeout - assuming thread is empty');
        }
      }, 2000); // Increased timeout to 2 seconds
    } else {
      // Fallback to REST API
      this.apiService.getMessages(this.selectedThread.id).subscribe({
        next: (messages: ChatMessage[]) => {
          // Clear and set messages atomically to prevent duplicates
          this.messages = [...messages];
          this.loading = false;
          this.scrollToBottom();
          
          // Track loaded messages to prevent duplicates
          this.processedMessageIds.clear();
          messages.forEach((msg: ChatMessage) => {
            const messageKey = `${msg.id || `${msg.content}-${msg.role}-${msg.timestamp}`}`;
            this.processedMessageIds.add(messageKey);
          });
        },
        error: (error: any) => {
          console.error('Failed to load messages:', error);
          this.error = 'Failed to load messages';
          this.loading = false;
        }
      });
    }
  }

  // Convert markdown content to HTML
  formatMessage(content: string): string {
    try {
      return marked(content) as string;
    } catch (error) {
      console.error('Markdown parsing error:', error);
      return content; // Fallback to plain text
    }
  }

  sendMessage(): void {
    if (!this.currentMessage.trim() || !this.selectedThread || this.isTyping) {
      return;
    }

    const userMessage = this.currentMessage.trim();
    const useWebSearch = this.forceWebSearch;
    
    // Reset input and web search state
    this.currentMessage = '';
    this.forceWebSearch = false;
    this.showToolsMenu = false;

    // If this is a draft thread, create it first
    if (this.selectedThread.isDraft) {
      this.createThreadFromFirstMessage(userMessage);
      return;
    }

    // Immediately add user message to display
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
      thread_id: this.selectedThread.id
    };
    
    this.messages.push(userMsg);
    this.scrollToBottom();
    
    // Show thinking indicator
    this.showThinking = true;
    this.isTyping = true;

    if (this.connected) {
      // Use WebSocket for real-time messaging
      this.apiService.sendMessageViaWebSocket(this.selectedThread.id, userMessage, useWebSearch);
    } else {
      // Fallback to REST API
      this.apiService.sendMessage(this.selectedThread.id, userMessage, useWebSearch).subscribe({
        next: (response) => {
          // Hide thinking indicator
          this.showThinking = false;
          this.isTyping = false;
          
          // Replace temp user message with real one and add assistant response
          const userMsgIndex = this.messages.findIndex(m => m.id === userMsg.id);
          if (userMsgIndex !== -1) {
            this.messages[userMsgIndex] = {
              ...response,
              role: 'user',
              content: userMessage
            };
          }
          
          // Add assistant response
          this.messages.push(response);
          this.scrollToBottom();
        },
        error: (error) => {
          console.error('Failed to send message:', error);
          this.error = 'Failed to send message';
          this.showThinking = false;
          this.isTyping = false;
          
          // Remove temp user message on error
          const userMsgIndex = this.messages.findIndex(m => m.id === userMsg.id);
          if (userMsgIndex !== -1) {
            this.messages.splice(userMsgIndex, 1);
          }
        }
      });
    }
  }

  private createThreadFromFirstMessage(firstMessage: string): void {
    // Capture web search state before resetting
    const useWebSearch = this.forceWebSearch;
    
    // Reset states
    this.forceWebSearch = false;
    this.showToolsMenu = false;
    
    // Generate a title from the first message
    const title = this.generateChatTitle(firstMessage);
    
    // Show thinking indicator immediately
    this.showThinking = true;
    this.isTyping = true;
    
    // Add user message to display
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: firstMessage,
      timestamp: new Date().toISOString(),
      thread_id: 'pending'
    };
    
    this.messages.push(userMsg);
    this.scrollToBottom();

    // Create the actual thread
    this.apiService.createThread(title).subscribe({
      next: (newThread) => {
        // Update the selected thread reference
        this.selectedThread = newThread;
        
        // Update the user message with real thread ID
        userMsg.thread_id = newThread.id;
        userMsg.id = `user-${Date.now()}`;
        
        // Emit the new thread to parent (threads component)
        this.threadCreated.emit(newThread);
        
        // Send the message via WebSocket or API
        if (this.connected) {
          this.apiService.sendMessageViaWebSocket(newThread.id, firstMessage, useWebSearch);
        } else {
          this.apiService.sendMessage(newThread.id, firstMessage, useWebSearch).subscribe({
            next: (response) => {
              this.showThinking = false;
              this.isTyping = false;
              this.messages.push(response);
              this.scrollToBottom();
            },
            error: (error) => {
              console.error('Failed to send message:', error);
              this.error = 'Failed to send message';
              this.showThinking = false;
              this.isTyping = false;
            }
          });
        }
      },
      error: (error) => {
        console.error('Failed to create thread:', error);
        this.error = 'Failed to create chat';
        this.showThinking = false;
        this.isTyping = false;
        
        // Remove the temp message on error
        const userMsgIndex = this.messages.findIndex(m => m.id === userMsg.id);
        if (userMsgIndex !== -1) {
          this.messages.splice(userMsgIndex, 1);
        }
      }
    });
  }

  private generateChatTitle(firstMessage: string): string {
    // Take first 50 characters and clean it up for a title
    let title = firstMessage.substring(0, 50).trim();
    
    // Remove common question words and clean up
    title = title.replace(/^(how|what|when|where|why|who|can|could|would|should|is|are|tell me|explain)/i, '');
    title = title.trim();
    
    // If title is too short or empty, use first few words
    if (title.length < 10) {
      const words = firstMessage.split(' ').slice(0, 5);
      title = words.join(' ');
    }
    
    // Add ellipsis if truncated
    if (firstMessage.length > 50) {
      title += '...';
    }
    
    // Fallback to default
    if (!title.trim()) {
      title = 'New Chat';
    }
    
    return title;
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
    
    // Auto-resize textarea
    this.autoResizeTextarea(event.target as HTMLTextAreaElement);
  }

  onInput(event: Event): void {
    // Auto-resize textarea on input
    this.autoResizeTextarea(event.target as HTMLTextAreaElement);
  }

  private autoResizeTextarea(textarea: HTMLTextAreaElement): void {
    if (!textarea) return;
    
    // Reset height to auto to get the scroll height
    textarea.style.height = 'auto';
    
    // Set height to scroll height but respect min/max bounds
    const minHeight = 24; // Minimum height
    const maxHeight = 200; // Maximum height (matches CSS)
    const scrollHeight = Math.max(minHeight, Math.min(maxHeight, textarea.scrollHeight));
    
    textarea.style.height = scrollHeight + 'px';
    
    // Update parent container height
    const container = textarea.closest('.input-container') as HTMLElement;
    if (container) {
      const newContainerHeight = Math.max(56, scrollHeight + 32); // 56px minimum, 32px for padding
      container.style.height = newContainerHeight + 'px';
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

  copyMessage(content: string): void {
    navigator.clipboard.writeText(content).then(() => {
      console.log('Message copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy message:', err);
    });
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

  private setupScrollbarBehavior(): void {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.messages-container');
      if (messagesContainer) {
        messagesContainer.addEventListener('scroll', () => {
          // Add scrolling class to show scrollbar
          messagesContainer.classList.add('scrolling');
          
          // Clear existing timeout
          if (this.scrollTimeout) {
            clearTimeout(this.scrollTimeout);
          }
          
          // Set timeout to hide scrollbar after 3 seconds
          this.scrollTimeout = setTimeout(() => {
            messagesContainer.classList.remove('scrolling');
          }, 3000);
        });
      }
    }, 500);
  }

  private initializeScrollbar() {
    this.messagesContainer = document.querySelector('.messages-container') as HTMLElement;
    
    if (this.messagesContainer) {
      // Add scroll event listener
      this.messagesContainer.addEventListener('scroll', () => {
        this.handleScroll();
      });
      
      // Add mouse enter/leave for hover effect
      this.messagesContainer.addEventListener('mouseenter', () => {
        this.showScrollbar();
      });
      
      this.messagesContainer.addEventListener('mouseleave', () => {
        this.hideScrollbarAfterDelay();
      });
    }
  }

  private handleScroll() {
    this.showScrollbar();
    this.hideScrollbarAfterDelay();
  }

  private showScrollbar() {
    if (this.messagesContainer) {
      this.messagesContainer.classList.add('scrolling');
    }
    
    // Clear existing timeout
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
  }

  private hideScrollbarAfterDelay() {
    // Clear existing timeout
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
    
    // Set new timeout to hide scrollbar after 3 seconds
    this.scrollTimeout = setTimeout(() => {
      if (this.messagesContainer) {
        this.messagesContainer.classList.remove('scrolling');
      }
    }, 3000);
  }

  // Web Search Tools Methods
  toggleToolsMenu(): void {
    this.showToolsMenu = !this.showToolsMenu;
  }

  toggleWebSearch(): void {
    this.forceWebSearch = !this.forceWebSearch;
    this.showToolsMenu = false; // Hide menu after selection
  }

  getInputPlaceholder(): string {
    if (this.forceWebSearch) {
      return 'Search the web...';
    }
    return 'Message ZackGPT...';
  }
} 