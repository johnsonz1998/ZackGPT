import pytest
from unittest.mock import Mock, patch
import numpy as np

class TestWhisperListener:
    """Test whisper listener functionality."""
    
    def test_module_imports(self):
        """Test that the module imports correctly."""
        from src.zackgpt.voice.whisper_listener import (
            transcribe_audio,
            listen_for_audio,
            listen_until_silence,
            reload_whisper_model
        )
        # If we get here, imports work
        assert True
    
    @patch('src.zackgpt.voice.whisper_listener.whisper_model')
    @patch('src.zackgpt.voice.whisper_listener.engine_type', 'openai-whisper')
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_transcribe_audio_basic(self, mock_config, mock_model):
        """Test basic transcription functionality."""
        from src.zackgpt.voice.whisper_listener import transcribe_audio
        
        mock_config.DEBUG_MODE = False
        mock_config.TEMP_AUDIO_FILE = Mock()
        mock_config.TEMP_AUDIO_FILE.exists.return_value = True
        
        mock_model.transcribe.return_value = {"text": "Hello world"}
        
        with patch('src.zackgpt.voice.whisper_listener.write'):
            audio_data = np.array([1, 2, 3, 4, 5], dtype=np.int16)
            result = transcribe_audio(audio_data)
            
            assert result == "Hello world"
    
    @patch('src.zackgpt.voice.whisper_listener.sd')
    @patch('src.zackgpt.voice.whisper_listener.transcribe_audio')
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_listen_for_audio_basic(self, mock_config, mock_transcribe, mock_sd):
        """Test basic audio recording."""
        from src.zackgpt.voice.whisper_listener import listen_for_audio
        
        mock_config.RECORD_DURATION = 3.0
        mock_config.SAMPLE_RATE = 16000
        
        mock_audio = np.array([1, 2, 3], dtype=np.int16)
        mock_sd.rec.return_value = mock_audio
        mock_transcribe.return_value = "Test transcription"
        
        result = listen_for_audio()
        
        assert result == "Test transcription"
    
    @patch('src.zackgpt.voice.whisper_listener.whisper_model')
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_transcribe_audio_faster_whisper(self, mock_config, mock_model):
        """Test transcribing audio with FasterWhisper."""
        mock_config.TRANSCRIBE_ENGINE = "faster-whisper"
        mock_config.DEBUG_MODE = False
        
        # Mock segment with text attribute
        mock_segment = Mock()
        mock_segment.text = "Hello world"
        mock_model.transcribe.return_value = ([mock_segment], None)
        
        audio_data = np.array([1, 2, 3, 4, 5], dtype=np.int16)
        result = transcribe_audio(audio_data)
        
        assert result == "Hello world"
    
    @patch('src.zackgpt.voice.whisper_listener.webrtcvad.Vad')
    @patch('src.zackgpt.voice.whisper_listener.sd.RawInputStream')
    @patch('src.zackgpt.voice.whisper_listener.transcribe_audio')
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_listen_until_silence(self, mock_config, mock_transcribe, mock_stream_class, mock_vad_class):
        """Test listening until silence detection."""
        mock_config.DEBUG_MODE = False
        mock_config.MIN_FRAMES = 2
        
        # Mock VAD
        mock_vad = Mock()
        mock_vad.is_speech.side_effect = [True, True, False, False]  # Speech then silence
        mock_vad_class.return_value = mock_vad
        
        # Mock audio stream
        mock_stream = Mock()
        mock_audio_data = b'\x00\x01' * 160  # 160 samples for 20ms at 16kHz
        mock_stream.read.return_value = (mock_audio_data, None)
        mock_stream_class.return_value.__enter__.return_value = mock_stream
        
        mock_transcribe.return_value = "Silence test"
        
        result = listen_until_silence()
        
        assert result == "Silence test"
    
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_reload_whisper_model_openai(self, mock_config):
        """Test reloading OpenAI Whisper model."""
        mock_config.TRANSCRIBE_ENGINE = "openai-whisper"
        mock_config.WHISPER_MODEL = "base"
        
        with patch('src.zackgpt.voice.whisper_listener.whisper') as mock_whisper:
            mock_model = Mock()
            mock_whisper.load_model.return_value = mock_model
            
            reload_whisper_model()
            
            mock_whisper.load_model.assert_called_once_with("base")
    
    @patch('src.zackgpt.voice.whisper_listener.config')
    def test_reload_whisper_model_faster(self, mock_config):
        """Test reloading FasterWhisper model."""
        mock_config.TRANSCRIBE_ENGINE = "faster-whisper"
        mock_config.WHISPER_MODEL = "base"
        
        with patch('src.zackgpt.voice.whisper_listener.WhisperModel') as mock_whisper_model:
            mock_model = Mock()
            mock_whisper_model.return_value = mock_model
            
            reload_whisper_model()
            
            mock_whisper_model.assert_called_once_with("base", compute_type="int8") 