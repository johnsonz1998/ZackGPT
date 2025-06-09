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
    web_search_enabled: true,
    web_search_max_results: 5,
    openai_api_key_masked: '***masked***',
    elevenlabs_api_key_masked: '***masked***',
    serpapi_key_masked: '',
    google_api_key_masked: '',
    google_cse_id_masked: '',
    debug_mode: false,
    log_level: 'INFO'
  };

  originalConfig: ZackGPTConfig = { ...this.config };
  loading = false;
  saving = false;
  isDirty = false;

  // API Key management
  apiKeys = {
    openai_api_key: '',
    elevenlabs_api_key: '',
    serpapi_key: '',
    google_api_key: '',
    google_cse_id: ''
  };
  apiKeysChanged = false;

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
    
    // Save config first
    this.apiService.updateConfig(this.config).subscribe({
      next: (updatedConfig) => {
        this.config = updatedConfig;
        this.originalConfig = { ...updatedConfig };
        
        // If API keys have changed, save them too
        if (this.apiKeysChanged) {
          this.saveApiKeysInternal();
        } else {
          this.saving = false;
          this.isDirty = false;
          console.log('Config saved successfully');
        }
      },
      error: (error) => {
        console.error('Failed to save config:', error);
        this.saving = false;
      }
    });
  }

  private saveApiKeysInternal(): void {
    // Only send non-empty keys
    const keysToUpdate: {[key: string]: string} = {};
    Object.entries(this.apiKeys).forEach(([key, value]) => {
      if (value && value.trim()) {
        keysToUpdate[key] = value.trim();
      }
    });

    if (Object.keys(keysToUpdate).length === 0) {
      this.saving = false;
      this.isDirty = false;
      this.apiKeysChanged = false;
      return;
    }

    this.apiService.updateApiKeys(keysToUpdate).subscribe({
      next: (response) => {
        this.saving = false;
        this.isDirty = false;
        this.apiKeysChanged = false;
        if (response.success) {
          console.log('Config and API keys saved successfully');
          // Clear the API key fields after successful save
          this.apiKeys = {
            openai_api_key: '',
            elevenlabs_api_key: '',
            serpapi_key: '',
            google_api_key: '',
            google_cse_id: ''
          };
          // Reload config to show updated masked keys
          this.loadConfig();
        } else {
          console.error('Failed to update API keys:', response.message);
        }
      },
      error: (error) => {
        console.error('Error updating API keys:', error);
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
    this.apiKeys = {
      openai_api_key: '',
      elevenlabs_api_key: '',
      serpapi_key: '',
      google_api_key: '',
      google_cse_id: ''
    };
    this.apiKeysChanged = false;
    this.isDirty = false;
  }

  onConfigChange(): void {
    this.checkIfDirty();
  }

  private checkIfDirty(): void {
    const configChanged = JSON.stringify(this.config) !== JSON.stringify(this.originalConfig);
    const apiKeysHaveValues = Object.values(this.apiKeys).some(value => value && value.trim());
    this.isDirty = configChanged || apiKeysHaveValues;
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
           this.isValidEvolutionFreq() &&
           this.isValidWebSearchResults();
  }

  isValidWebSearchResults(): boolean {
    return this.config.web_search_max_results > 0 && this.config.web_search_max_results <= 20;
  }

  // API Key management methods
  onApiKeyChange(): void {
    this.apiKeysChanged = true;
    this.checkIfDirty();
  }


} 