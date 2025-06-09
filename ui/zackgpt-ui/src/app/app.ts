import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { SettingsComponent } from './components/settings/settings.component';
import { ThreadsComponent } from './components/threads/threads.component';
import { Thread } from './services/api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, DashboardComponent, SettingsComponent, ThreadsComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  title = 'ZackGPT UI';
  activeTab: 'chat' | 'settings' = 'chat';
  selectedThread: Thread | null = null;
  connected = false;

  onThreadSelected(thread: Thread): void {
    this.selectedThread = thread;
    this.activeTab = 'chat';
  }

  onThreadCreated(thread: Thread): void {
    this.selectedThread = thread;
    this.activeTab = 'chat';
  }

  setActiveTab(tab: 'chat' | 'settings'): void {
    this.activeTab = tab;
  }
}
