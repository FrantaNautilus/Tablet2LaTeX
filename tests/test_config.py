"""
Unit tests for the Config class.
"""

import os
from pathlib import Path

import pytest

from tablet2latex.config import Config, get_xdg_config_home


class TestGetXdgConfigHome:
    """Tests for get_xdg_config_home function."""

    def test_returns_env_variable_when_set(self, monkeypatch, temp_dir):
        """Test that XDG_CONFIG_HOME env variable is used when set."""
        monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)
        result = get_xdg_config_home()
        assert result == temp_dir

    def test_returns_default_when_env_not_set(self, monkeypatch):
        """Test that default ~/.config is used when XDG_CONFIG_HOME not set."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_xdg_config_home()
        assert result == os.path.join(os.path.expanduser("~"), ".config")

    def test_expands_user_in_env_variable(self, monkeypatch):
        """Test that ~ is expanded in XDG_CONFIG_HOME."""
        monkeypatch.setenv("XDG_CONFIG_HOME", "~/custom_config")
        result = get_xdg_config_home()
        assert result == os.path.expanduser("~/custom_config")


class TestConfigInitialization:
    """Tests for Config class initialization."""

    def test_loads_config_from_provided_path(self, mock_config_file):
        """Test loading configuration from a specific file path."""
        config = Config(mock_config_file)
        assert config.config_path == mock_config_file

    def test_creates_default_config_when_file_missing(self, temp_dir):
        """Test that default config is created when file doesn't exist."""
        config_path = Path(temp_dir) / "nonexistent" / "config.ini"
        config = Config(str(config_path))

        # Should not raise error and should have default values
        assert config.get("API", "provider") == "openai"
        assert config.width == 800
        assert config.height == 600

    def test_adds_missing_sections_with_defaults(
        self, mock_config_file_missing_section
    ):
        """Test that missing sections are automatically added with defaults."""
        # The config class adds default sections if they're missing
        config = Config(mock_config_file_missing_section)
        # Should not raise error and have default values for shortcuts
        assert config.shortcut_tool_pen == "<Control>c"
        assert config.shortcut_tool_eraser == "<Control>e"

    def test_validates_provider(self, mock_config_file_invalid_provider):
        """Test that validation fails for invalid provider."""
        with pytest.raises(ValueError, match="Invalid provider"):
            Config(mock_config_file_invalid_provider)

    def test_validates_numeric_values(self, mock_config_file_invalid_numbers):
        """Test that validation fails for invalid numeric values."""
        with pytest.raises(ValueError, match="Invalid numeric value"):
            Config(mock_config_file_invalid_numbers)


class TestConfigProperties:
    """Tests for Config properties."""

    def test_width_property(self, mock_config_file):
        """Test width property returns correct value."""
        config = Config(mock_config_file)
        assert config.width == 800

    def test_height_property(self, mock_config_file):
        """Test height property returns correct value."""
        config = Config(mock_config_file)
        assert config.height == 600

    def test_max_tokens_property(self, mock_config_file):
        """Test max_tokens property returns correct value."""
        config = Config(mock_config_file)
        assert config.max_tokens == 1000

    def test_prompt_property(self, mock_config_file):
        """Test prompt property returns correct value."""
        config = Config(mock_config_file)
        assert config.prompt == "Convert the handwritten text to LaTeX."

    def test_shortcut_properties(self, mock_config_file):
        """Test shortcut properties return correct values."""
        config = Config(mock_config_file)
        assert config.shortcut_tool_pen == "<Control>c"
        assert config.shortcut_tool_eraser == "<Control>e"
        assert config.shortcut_clear_canvas == "<Control>d"
        assert config.shortcut_submit == "<Control>s"

    def test_properties_with_fallback(self, temp_dir):
        """Test properties use fallback values when keys missing."""
        config_path = Path(temp_dir) / "minimal_config.ini"
        config_content = """[API]
provider = openai

[Canvas]
width = 800
height = 600

[LLM]
max_tokens = 1000

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
        config_path.write_text(config_content)
        config = Config(str(config_path))

        # Should use fallback for missing prompt
        assert "Convert the handwritten text" in config.prompt


class TestConfigGetMethod:
    """Tests for Config.get method."""

    def test_get_existing_value(self, mock_config_file):
        """Test getting an existing configuration value."""
        config = Config(mock_config_file)
        value = config.get("API", "provider")
        assert value == "openai"

    def test_get_with_fallback(self, mock_config_file):
        """Test fallback value for non-existent key."""
        config = Config(mock_config_file)
        value = config.get("API", "nonexistent_key", fallback="default_value")
        assert value == "default_value"

    def test_get_fallback_when_section_missing(self, mock_config_file):
        """Test fallback when entire section is missing."""
        config = Config(mock_config_file)
        value = config.get("NonExistentSection", "key", fallback="default")
        assert value == "default"


class TestConfigSave:
    """Tests for Config.save method."""

    def test_save_creates_directory_if_needed(self, temp_dir):
        """Test that save creates parent directories if they don't exist."""
        config_path = Path(temp_dir) / "subdir" / "config.ini"
        config = Config(str(config_path))
        config.save()

        assert config_path.exists()

    def test_save_persists_values(self, temp_dir):
        """Test that saved config can be reloaded with same values."""
        config_path = Path(temp_dir) / "config.ini"

        # Create and save config
        config1 = Config(str(config_path))
        config1.save()

        # Load saved config
        config2 = Config(str(config_path))
        assert config2.get("API", "provider") == config1.get("API", "provider")


class TestConfigProviderSpecific:
    """Tests for different provider configurations."""

    def test_openai_provider_config(self, mock_config_file):
        """Test OpenAI provider configuration."""
        config = Config(mock_config_file)
        assert config.get("API", "provider") == "openai"
        assert config.get("API", "openai_api_key") == "test_api_key"
        assert config.get("API", "openai_model") == "gpt-4o"

    def test_ollama_provider_config(self, mock_config_file_ollama):
        """Test Ollama provider configuration."""
        config = Config(mock_config_file_ollama)
        assert config.get("API", "provider") == "ollama"
        assert config.get("API", "ollama_model") == "llava"
        assert config.width == 1024
        assert config.height == 768
        assert config.max_tokens == 2000

    def test_llamacpp_provider_config(self, mock_config_file_llamacpp):
        """Test LlamaCpp provider configuration."""
        config = Config(mock_config_file_llamacpp)
        assert config.get("API", "provider") == "llamacpp"
        assert config.get("API", "llamacpp_model") == "llava"
        assert config.width == 512
        assert config.height == 384
        assert config.max_tokens == 500


class TestConfigXdgResolution:
    """Tests for XDG config path resolution."""

    def test_uses_xdg_config_home_when_set(self, monkeypatch, temp_dir):
        """Test that XDG_CONFIG_HOME is used when set."""
        xdg_config = Path(temp_dir) / "xdg_config"
        xdg_config.mkdir()
        config_file = xdg_config / "tablet2latex" / "config.ini"
        config_file.parent.mkdir(parents=True)

        # Create valid config
        config_content = """[API]
provider = openai

[Canvas]
width = 800
height = 600

[LLM]
max_tokens = 1000

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
        config_file.write_text(config_content)

        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))

        config = Config()
        assert config.config_path == str(config_file)
