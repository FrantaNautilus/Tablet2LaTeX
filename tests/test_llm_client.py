"""
Unit tests for the LLMClient class.
"""

import base64
import io
from unittest.mock import MagicMock, Mock, patch

import cairo
import pytest

from tablet2latex.llm_client import LLMClient


class MockConfig:
    """Mock Config class for testing."""

    def __init__(self, provider="openai", api_key="test_key"):
        self._provider = provider
        self._api_key = api_key
        self._data = {
            "API": {
                "provider": provider,
                "openai_api_key": api_key if provider == "openai" else "",
                "openai_model": "gpt-4o",
                "openai_base_url": "https://api.openai.com/v1",
                "ollama_base_url": "http://localhost:11434/v1",
                "ollama_model": "llava",
                "llamacpp_base_url": "http://localhost:8080/v1",
                "llamacpp_model": "llava",
            },
            "LLM": {
                "max_tokens": "1000",
                "prompt": "Convert handwritten text to LaTeX",
            },
        }

    def get(self, section, key, fallback=""):
        return self._data.get(section, {}).get(key, fallback)

    @property
    def prompt(self):
        return self._data["LLM"]["prompt"]


@pytest.fixture
def mock_openai_config():
    """Create a mock config for OpenAI provider."""
    return MockConfig(provider="openai", api_key="test_api_key")


@pytest.fixture
def mock_ollama_config():
    """Create a mock config for Ollama provider."""
    return MockConfig(provider="ollama")


@pytest.fixture
def mock_llamacpp_config():
    """Create a mock config for LlamaCpp provider."""
    return MockConfig(provider="llamacpp")


@pytest.fixture
def mock_unconfigured_config():
    """Create a mock config without valid API key."""
    config = MockConfig(provider="openai", api_key="your_api_key_here")
    return config


@pytest.fixture
def mock_surface():
    """Create a mock Cairo surface for testing."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    return surface


@pytest.fixture
def mock_status_label():
    """Create a mock status label."""
    label = MagicMock()
    label.set_text = MagicMock()
    return label


class TestLLMClientInitialization:
    """Tests for LLMClient initialization."""

    @patch("tablet2latex.llm_client.OpenAI")
    def test_init_openai_client(self, mock_openai_class, mock_openai_config):
        """Test initializing OpenAI client."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        assert client.config == mock_openai_config
        mock_openai_class.assert_called_once_with(
            api_key="test_api_key", base_url="https://api.openai.com/v1"
        )

    @patch("tablet2latex.llm_client.OpenAI")
    def test_init_openai_with_placeholder_key(
        self, mock_openai_class, mock_unconfigured_config
    ):
        """Test that client is None with placeholder API key."""
        client = LLMClient(mock_unconfigured_config)

        assert client.client is None
        # Model is still set even when client is None
        assert client.model == "gpt-4o"

    @patch("tablet2latex.llm_client.OpenAI")
    def test_init_ollama_client(self, mock_openai_class, mock_ollama_config):
        """Test initializing Ollama client."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_ollama_config)

        mock_openai_class.assert_called_once_with(
            api_key="ollama", base_url="http://localhost:11434/v1"
        )
        assert client.model == "llava"

    @patch("tablet2latex.llm_client.OpenAI")
    def test_init_llamacpp_client(self, mock_openai_class, mock_llamacpp_config):
        """Test initializing LlamaCpp client."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_llamacpp_config)

        mock_openai_class.assert_called_once_with(
            api_key="llamacpp", base_url="http://localhost:8080/v1"
        )
        assert client.model == "llava"


class TestLLMClientIsConfigured:
    """Tests for is_configured method."""

    @patch("tablet2latex.llm_client.OpenAI")
    def test_is_configured_true(self, mock_openai_class, mock_openai_config):
        """Test is_configured returns True when properly configured."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        assert client.is_configured() is True

    def test_is_configured_false_no_client(self, mock_unconfigured_config):
        """Test is_configured returns False when client is None."""
        client = LLMClient(mock_unconfigured_config)

        assert client.is_configured() is False

    @patch("tablet2latex.llm_client.OpenAI")
    def test_is_configured_false_no_model(self, mock_openai_class, mock_openai_config):
        """Test is_configured returns False when model is None."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)
        client.model = None

        assert client.is_configured() is False


class TestLLMClientSubmitToLLM:
    """Tests for submit_to_llm method."""

    @patch("tablet2latex.llm_client.GLib")
    @patch("tablet2latex.llm_client.OpenAI")
    def test_submit_not_configured(
        self, mock_openai_class, mock_glib, mock_unconfigured_config, mock_status_label
    ):
        """Test submit when not configured."""
        client = LLMClient(mock_unconfigured_config)

        result = client.submit_to_llm("base64_image", mock_status_label)

        assert result is None
        # UI update is now scheduled via GLib.idle_add
        mock_glib.idle_add.assert_called()
        # Simulate idle callback execution and verify label message
        call_args = mock_glib.idle_add.call_args
        callback = call_args[0][0]
        callback()
        mock_status_label.set_text.assert_called_with(
            "Error: LLM client not configured. Please check config.ini"
        )

    @patch("tablet2latex.llm_client.GLib")
    @patch("tablet2latex.llm_client.OpenAI")
    def test_submit_success(
        self,
        mock_openai_class,
        mock_glib,
        mock_openai_config,
        mock_status_label,
    ):
        """Test successful submission to LLM."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "```latex\\n\\\\frac{a}{b}\\n```"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        result = client.submit_to_llm("base64_image", mock_status_label, max_tokens=500)

        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args

        assert call_args[1]["model"] == "gpt-4o"
        assert call_args[1]["max_tokens"] == 500
        assert len(call_args[1]["messages"]) == 1

        # Verify result is processed
        assert result is not None
        assert r"\frac{a}{b}" in result

    @patch("tablet2latex.llm_client.GLib")
    @patch("tablet2latex.llm_client.OpenAI")
    def test_submit_api_error(
        self, mock_openai_class, mock_glib, mock_openai_config, mock_status_label
    ):
        """Test handling API error."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        result = client.submit_to_llm("base64_image", mock_status_label)

        assert result is None
        # Error UI update is scheduled via GLib.idle_add
        mock_glib.idle_add.assert_called()
        # Execute the last idle callback to verify message
        # The last call should be the error one
        calls = [c for c in mock_glib.idle_add.call_args_list]
        # Invoke last callback
        cb = calls[-1][0][0]
        cb()
        mock_status_label.set_text.assert_called()

    @patch("tablet2latex.llm_client.GLib")
    @patch("tablet2latex.llm_client.OpenAI")
    def test_submit_includes_image_in_request(
        self,
        mock_openai_class,
        mock_glib,
        mock_openai_config,
        mock_status_label,
    ):
        """Test that image is included in the API request."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "\\\\alpha"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        test_image = "test_base64_image_data"
        client.submit_to_llm(test_image, mock_status_label)

        # Check that image was included in the message
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        content = messages[0]["content"]

        # Should have text and image parts
        assert len(content) == 2
        assert content[1]["type"] == "image_url"
        assert test_image in content[1]["image_url"]["url"]

    @patch("tablet2latex.llm_client.GLib")
    @patch("tablet2latex.llm_client.OpenAI")
    def test_submit_uses_config_prompt(
        self,
        mock_openai_class,
        mock_glib,
        mock_openai_config,
        mock_status_label,
    ):
        """Test that configured prompt is used."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "result"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = LLMClient(mock_openai_config)

        client.submit_to_llm("image", mock_status_label)

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        content = messages[0]["content"]

        # First item should be the text with prompt
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "Convert handwritten text to LaTeX"


class TestLLMClientProviderVariants:
    """Tests for different LLM provider configurations."""

    @patch("tablet2latex.llm_client.OpenAI")
    def test_ollama_model_name(self, mock_openai_class):
        """Test Ollama model name is set correctly."""
        config = MockConfig(provider="ollama")
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(config)

        assert client.model == "llava"

    @patch("tablet2latex.llm_client.OpenAI")
    def test_llamacpp_model_name(self, mock_openai_class):
        """Test LlamaCpp model name is set correctly."""
        config = MockConfig(provider="llamacpp")
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(config)

        assert client.model == "llava"

    @patch("tablet2latex.llm_client.OpenAI")
    def test_openai_model_name(self, mock_openai_class):
        """Test OpenAI model name is set correctly."""
        config = MockConfig(provider="openai", api_key="test_key")
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = LLMClient(config)

        assert client.model == "gpt-4o"
