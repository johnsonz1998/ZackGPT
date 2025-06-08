import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ZackgptApiService, ZackGPTConfig } from '../../services/zackgpt-api.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  config: ZackGPTConfig = {
    model_name: 'gpt-4',
    max_tokens: 2000,
    temperature: 0.7,
    voice_enabled: false,
    voice_model: 'whisper-1',
    tts_voice: 'alloy',
    memory_enabled: true,
    max_memory_entries: 1000,
    evolution_enabled: true,
    evolution_frequency: 10,
    openai_api_key_masked: '***masked***',
    elevenlabs_api_key_masked: '***masked***',
    debug_mode: false,
    log_level: 'INFO'
  };

  originalConfig: ZackGPTConfig = { ...this.config };
  loading = false;
  saving = false;
  isDirty = false;

  // Dropdown options
  logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];
  ttsVoices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
  modelOptions = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'];

  constructor(private apiService: ZackgptApiService) {}

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig(): void {
    this.loading = true;
    this.apiService.getConfig().subscribe({
      next: (config) => {
        this.config = config;
        this.originalConfig = { ...config };
        this.loading = false;
        this.checkIfDirty();
      },
      error: (error) => {
        console.error('Failed to load config:', error);
        this.loading = false;
      }
    });
  }

  saveConfig(): void {
    this.saving = true;
    this.apiService.updateConfig(this.config).subscribe({
      next: (updatedConfig) => {
        this.config = updatedConfig;
        this.originalConfig = { ...updatedConfig };
        this.saving = false;
        this.isDirty = false;
        console.log('Config saved successfully');
      },
      error: (error) => {
        console.error('Failed to save config:', error);
        this.saving = false;
      }
    });
  }

  resetConfig(): void {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
      this.loading = true;
      this.apiService.resetConfig().subscribe({
        next: (defaultConfig) => {
          this.config = defaultConfig;
          this.originalConfig = { ...defaultConfig };
          this.loading = false;
          this.isDirty = false;
          console.log('Config reset to defaults');
        },
        error: (error) => {
          console.error('Failed to reset config:', error);
          this.loading = false;
        }
      });
    }
  }

  discardChanges(): void {
    this.config = { ...this.originalConfig };
    this.isDirty = false;
  }

  onConfigChange(): void {
    this.checkIfDirty();
  }

  private checkIfDirty(): void {
    this.isDirty = JSON.stringify(this.config) !== JSON.stringify(this.originalConfig);
  }

  // Validation helpers
  isValidTemperature(): boolean {
    return this.config.temperature >= 0 && this.config.temperature <= 2;
  }

  isValidMaxTokens(): boolean {
    return this.config.max_tokens > 0 && this.config.max_tokens <= 8000;
  }

  isValidMemoryEntries(): boolean {
    return this.config.max_memory_entries > 0 && this.config.max_memory_entries <= 10000;
  }

  isValidEvolutionFreq(): boolean {
    return this.config.evolution_frequency > 0 && this.config.evolution_frequency <= 100;
  }

  isFormValid(): boolean {
    return this.isValidTemperature() && 
           this.isValidMaxTokens() && 
           this.isValidMemoryEntries() && 
           this.isValidEvolutionFreq();
  }
} 