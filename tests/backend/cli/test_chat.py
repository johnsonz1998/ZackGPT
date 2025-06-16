import pytest
from unittest.mock import Mock, patch, MagicMock
from src.zackgpt.cli.chat import run_text_mode

class TestChatCLI:
    """Test CLI chat functionality."""
    
    @patch('src.zackgpt.cli.chat.CoreAssistant')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_text_mode_exit(self, mock_print, mock_input, mock_assistant_class):
        """Test that text mode exits properly."""
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        mock_input.return_value = "exit"
        
        run_text_mode()
        
        mock_assistant_class.assert_called_once()
    
    @patch('src.zackgpt.cli.chat.CoreAssistant')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_text_mode_conversation(self, mock_print, mock_input, mock_assistant_class):
        """Test basic conversation flow."""
        mock_assistant = Mock()
        mock_assistant.process_input.return_value = "Test response"
        mock_assistant_class.return_value = mock_assistant
        
        # Simulate: user input -> rating -> exit
        mock_input.side_effect = ["Hello", "5", "exit"]
        
        run_text_mode()
        
        mock_assistant.process_input.assert_called_with("Hello")
    
    @patch('src.zackgpt.cli.chat.CoreAssistant')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_text_mode_keyboard_interrupt(self, mock_print, mock_input, mock_assistant_class):
        """Test handling keyboard interrupt."""
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        mock_input.side_effect = KeyboardInterrupt()
        
        # Should not raise exception
        run_text_mode() 