import { Component, OnInit, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ApiService, Thread } from '../../services/api.service';

@Component({
  selector: 'app-threads',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './threads.component.html',
  styleUrls: ['./threads.component.scss']
})
export class ThreadsComponent implements OnInit, OnDestroy {
  @Output() threadSelected = new EventEmitter<Thread>();
  
  threads: Thread[] = [];
  selectedThreadId: string | null = null;
  isCreatingThread = false;
  newThreadName = '';
  loading = false;
  connected = false;
  backendConnected = false;
  error = '';

  private subscriptions: Subscription[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.initializeConnections();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private initializeConnections(): void {
    // Subscribe to connection status
    this.subscriptions.push(
      this.apiService.getConnectionStatus().subscribe(connected => {
        this.connected = connected;
        this.backendConnected = connected;
        if (connected) {
          this.loadThreads();
        }
      })
    );

    // Subscribe to errors
    this.subscriptions.push(
      this.apiService.errors$.subscribe(error => {
        this.error = error;
        console.error('API Error:', error);
      })
    );

    // Initial load
    this.loadThreads();
  }

  loadThreads(): void {
    this.loading = true;
    this.error = '';

    this.apiService.getThreads().subscribe({
      next: (threads) => {
        this.threads = threads.sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
        this.loading = false;
        
        // Auto-select first thread if none selected
        if (threads.length > 0 && !this.selectedThreadId) {
          this.selectThread(threads[0]);
        }
      },
      error: (error) => {
        console.error('Failed to load threads:', error);
        this.loading = false;
        this.error = 'Failed to load threads';
        this.threads = [];
      }
    });
  }

  selectThread(thread: Thread): void {
    this.selectedThreadId = thread.id;
    this.threadSelected.emit(thread);
  }

  createNewChat(): void {
    // Create a draft/temporary thread that will be created on first message
    const draftThread: Thread = {
      id: `draft-${Date.now()}`,
      title: '',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      isDraft: true
    };
    
    this.selectThread(draftThread);
  }

  startCreatingThread(): void {
    this.isCreatingThread = true;
    this.newThreadName = '';
    setTimeout(() => {
      const input = document.getElementById('newThreadInput') as HTMLInputElement;
      if (input) input.focus();
    }, 100);
  }

  cancelCreatingThread(): void {
    this.isCreatingThread = false;
    this.newThreadName = '';
  }

  createThread(): void {
    if (!this.newThreadName.trim()) return;

    const threadTitle = this.newThreadName.trim();
    this.newThreadName = '';

    this.apiService.createThread(threadTitle).subscribe({
      next: (newThread) => {
        this.threads.unshift(newThread);
        this.selectThread(newThread);
        this.isCreatingThread = false;
      },
      error: (error) => {
        console.error('Failed to create thread:', error);
        this.error = 'Failed to create thread';
        this.isCreatingThread = false;
      }
    });
  }

  deleteThread(thread: Thread, event: Event): void {
    event.stopPropagation();
    
    if (confirm(`Are you sure you want to delete "${thread.title}"?`)) {
      this.apiService.deleteThread(thread.id).subscribe({
        next: () => {
          this.threads = this.threads.filter(t => t.id !== thread.id);
          
          // If we deleted the selected thread, select another one
          if (this.selectedThreadId === thread.id) {
            if (this.threads.length > 0) {
              this.selectThread(this.threads[0]);
            } else {
              this.selectedThreadId = null;
              // Emit null to indicate no thread selected
              this.threadSelected.emit(null as any);
            }
          }
        },
        error: (error) => {
          console.error('Failed to delete thread:', error);
          this.error = 'Failed to delete thread';
        }
      });
    }
  }

  formatDate(dateString: string): string {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
      
      if (diffInHours < 1) {
        return 'Just now';
      } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)}h ago`;
      } else if (diffInHours < 48) {
        return 'Yesterday';
      } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays}d ago`;
      }
    } catch (error) {
      return 'Unknown';
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.createThread();
    } else if (event.key === 'Escape') {
      this.cancelCreatingThread();
    }
  }

  clearError(): void {
    this.error = '';
  }

  retry(): void {
    this.loadThreads();
  }

  trackThread(index: number, thread: Thread): string {
    return thread.id;
  }

  addNewThread(thread: Thread): void {
    // Add thread to the beginning of the list and update the UI
    this.threads.unshift(thread);
  }
} 