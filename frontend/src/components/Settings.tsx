import React, { useState, useEffect } from 'react';
import { X, Settings as SettingsIcon, Key, Zap, Globe } from 'lucide-react';
import './Settings.css';

interface ZackGPTConfig {
  model_name: string;
  max_tokens: number;
  temperature: number;
  voice_enabled: boolean;
  voice_model: string;
  tts_voice: string;
  memory_enabled: boolean;
  max_memory_entries: number;
  evolution_enabled: boolean;
  evolution_frequency: number;
  web_search_enabled: boolean;
  web_search_max_results: number;
  openai_api_key_masked: string;
  elevenlabs_api_key_masked: string;
  serpapi_key_masked: string;
  google_api_key_masked: string;
  google_cse_id_masked: string;
  debug_mode: boolean;
  log_level: string;
}

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [config, setConfig] = useState<ZackGPTConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('general');
  const [apiKeys, setApiKeys] = useState({
    openai_api_key: '',
    elevenlabs_api_key: '',
    serpapi_key: '',
    google_api_key: '',
    google_cse_id: ''
  });

  useEffect(() => {
    if (isOpen) {
      loadConfig();
    }
  }, [isOpen]);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/config');
      if (response.ok) {
        const configData = await response.json();
        setConfig(configData);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateApiKeys = async () => {
    setLoading(true);
    try {
      const response = await fetch('/config/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiKeys)
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('API keys updated:', result);
        loadConfig(); // Reload config to see updated masked keys
        // Clear the form
        setApiKeys({
          openai_api_key: '',
          elevenlabs_api_key: '',
          serpapi_key: '',
          google_api_key: '',
          google_cse_id: ''
        });
      }
    } catch (error) {
      console.error('Failed to update API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApiKeyChange = (key: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [key]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={e => e.stopPropagation()}>
        <div className="settings-header">
          <h2>
            <SettingsIcon size={20} />
            Settings
          </h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="settings-content">
          <div className="settings-tabs">
            <button 
              className={`tab ${activeTab === 'general' ? 'active' : ''}`}
              onClick={() => setActiveTab('general')}
            >
              <Zap size={16} />
              General
            </button>
            <button 
              className={`tab ${activeTab === 'api-keys' ? 'active' : ''}`}
              onClick={() => setActiveTab('api-keys')}
            >
              <Key size={16} />
              API Keys
            </button>
            <button 
              className={`tab ${activeTab === 'web-search' ? 'active' : ''}`}
              onClick={() => setActiveTab('web-search')}
            >
              <Globe size={16} />
              Web Search
            </button>
          </div>

          <div className="settings-panel">
            {loading ? (
              <div className="loading">Loading...</div>
            ) : (
              <>
                {activeTab === 'general' && config && (
                  <div className="settings-section">
                    <h3>Model Configuration</h3>
                    <div className="setting-item">
                      <label>Model:</label>
                      <span className="value">{config.model_name}</span>
                    </div>
                    <div className="setting-item">
                      <label>Max Tokens:</label>
                      <span className="value">{config.max_tokens}</span>
                    </div>
                    <div className="setting-item">
                      <label>Temperature:</label>
                      <span className="value">{config.temperature}</span>
                    </div>
                    
                    <h3>Features</h3>
                    <div className="setting-item">
                      <label>Voice Enabled:</label>
                      <span className={`status ${config.voice_enabled ? 'enabled' : 'disabled'}`}>
                        {config.voice_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="setting-item">
                      <label>Memory Enabled:</label>
                      <span className={`status ${config.memory_enabled ? 'enabled' : 'disabled'}`}>
                        {config.memory_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="setting-item">
                      <label>Evolution Enabled:</label>
                      <span className={`status ${config.evolution_enabled ? 'enabled' : 'disabled'}`}>
                        {config.evolution_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="setting-item">
                      <label>Debug Mode:</label>
                      <span className={`status ${config.debug_mode ? 'enabled' : 'disabled'}`}>
                        {config.debug_mode ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                )}

                {activeTab === 'api-keys' && config && (
                  <div className="settings-section">
                    <h3>API Keys</h3>
                    <p className="section-description">
                      Configure your API keys for various services. Keys are masked for security.
                    </p>
                    
                    <div className="api-key-form">
                      <div className="form-group">
                        <label>OpenAI API Key:</label>
                        <div className="key-display">
                          <span className="masked-key">{config.openai_api_key_masked || 'Not set'}</span>
                        </div>
                        <input
                          type="password"
                          placeholder="Enter new OpenAI API key"
                          value={apiKeys.openai_api_key}
                          onChange={(e) => handleApiKeyChange('openai_api_key', e.target.value)}
                        />
                      </div>

                      <div className="form-group">
                        <label>ElevenLabs API Key:</label>
                        <div className="key-display">
                          <span className="masked-key">{config.elevenlabs_api_key_masked || 'Not set'}</span>
                        </div>
                        <input
                          type="password"
                          placeholder="Enter new ElevenLabs API key"
                          value={apiKeys.elevenlabs_api_key}
                          onChange={(e) => handleApiKeyChange('elevenlabs_api_key', e.target.value)}
                        />
                      </div>

                      <div className="form-group">
                        <label>SerpAPI Key:</label>
                        <div className="key-display">
                          <span className="masked-key">{config.serpapi_key_masked || 'Not set'}</span>
                        </div>
                        <input
                          type="password"
                          placeholder="Enter new SerpAPI key"
                          value={apiKeys.serpapi_key}
                          onChange={(e) => handleApiKeyChange('serpapi_key', e.target.value)}
                        />
                      </div>

                      <div className="form-group">
                        <label>Google API Key:</label>
                        <div className="key-display">
                          <span className="masked-key">{config.google_api_key_masked || 'Not set'}</span>
                        </div>
                        <input
                          type="password"
                          placeholder="Enter new Google API key"
                          value={apiKeys.google_api_key}
                          onChange={(e) => handleApiKeyChange('google_api_key', e.target.value)}
                        />
                      </div>

                      <div className="form-group">
                        <label>Google CSE ID:</label>
                        <div className="key-display">
                          <span className="masked-key">{config.google_cse_id_masked || 'Not set'}</span>
                        </div>
                        <input
                          type="password"
                          placeholder="Enter new Google CSE ID"
                          value={apiKeys.google_cse_id}
                          onChange={(e) => handleApiKeyChange('google_cse_id', e.target.value)}
                        />
                      </div>

                      <button 
                        className="update-btn" 
                        onClick={updateApiKeys}
                        disabled={loading}
                      >
                        Update API Keys
                      </button>
                    </div>
                  </div>
                )}

                {activeTab === 'web-search' && config && (
                  <div className="settings-section">
                    <h3>Web Search Configuration</h3>
                    <div className="setting-item">
                      <label>Web Search Enabled:</label>
                      <span className={`status ${config.web_search_enabled ? 'enabled' : 'disabled'}`}>
                        {config.web_search_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="setting-item">
                      <label>Max Results:</label>
                      <span className="value">{config.web_search_max_results}</span>
                    </div>
                    
                    <h3>Search Engines Status</h3>
                    <div className="setting-item">
                      <label>SerpAPI:</label>
                      <span className={`status ${config.serpapi_key_masked ? 'configured' : 'not-configured'}`}>
                        {config.serpapi_key_masked ? 'Configured' : 'Not Configured'}
                      </span>
                    </div>
                    <div className="setting-item">
                      <label>Google Custom Search:</label>
                      <span className={`status ${config.google_api_key_masked && config.google_cse_id_masked ? 'configured' : 'not-configured'}`}>
                        {config.google_api_key_masked && config.google_cse_id_masked ? 'Configured' : 'Not Configured'}
                      </span>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 