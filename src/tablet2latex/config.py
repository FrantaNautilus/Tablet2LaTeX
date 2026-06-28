"""
Configuration management for Tablet2LaTeX.
"""

import configparser
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def get_xdg_config_home() -> str:
    """Get the XDG_CONFIG_HOME directory.

    Returns:
        Path to the XDG_CONFIG_HOME directory.
    """
    config_home = os.getenv("XDG_CONFIG_HOME")
    if config_home:
        return os.path.expanduser(config_home)
    return os.path.join(os.path.expanduser("~"), ".config")


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration.

        Args:
            config_path: Optional path to config file. If None, uses XDG standard location.
        """
        self.config_path = self._resolve_config_path(config_path)
        self._config = self._load_config()
        self._validate_config()

    def _resolve_config_path(self, config_path: Optional[str] = None) -> str:
        """Resolve the configuration file path using XDG standards.

        Args:
            config_path: Optional custom config path.

        Returns:
            Resolved path to the configuration file.
        """
        if config_path is not None:
            return os.path.abspath(config_path)

        # XDG standard location
        xdg_config_home = get_xdg_config_home()
        xdg_path = os.path.join(xdg_config_home, "tablet2latex", "config.ini")

        # Priority: XDG location > legacy location
        if os.path.exists(xdg_path):
            return xdg_path
        elif os.path.exists("config.ini"):
            logger.warning(
                "SECURITY WARNING: Loading config from legacy config.ini in current directory. "
                "This is insecure and deprecated. Move to ~/.config/tablet2latex/config.ini"
            )
            return os.path.abspath("config.ini")
        else:
            return xdg_path

    def _validate_config(self):
        """Validate configuration file structure.

        Raises:
            ValueError: If configuration is invalid.
        """
        required_sections = ["API", "Canvas", "LLM", "Shortcuts"]

        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Missing required section: [{section}]")

        # Validate provider
        provider = self.get("API", "provider", fallback="openai")
        valid_providers = ["openai", "ollama", "llamacpp"]
        if provider not in valid_providers:
            raise ValueError(
                f"Invalid provider: {provider}. Must be one of {valid_providers}"
            )

        # Validate Canvas numeric values
        for key, default in [("width", "800"), ("height", "600")]:
            try:
                value = int(self.get("Canvas", key, fallback=default))
                if value <= 0:
                    raise ValueError(f"{key} must be positive")
            except ValueError as e:
                raise ValueError(f"Invalid numeric value for {key}: {e}")

        # Validate max_tokens from LLM section
        try:
            mt = int(self.get("LLM", "max_tokens", fallback="1000"))
            if mt <= 0:
                raise ValueError("max_tokens must be positive")
            if mt > 100000:
                raise ValueError("max_tokens too large")
        except ValueError as e:
            raise ValueError(f"Invalid numeric value for max_tokens: {e}")

    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from file.

        Returns:
            ConfigParser object with configuration values.
        """
        config = configparser.ConfigParser()

        if os.path.exists(self.config_path):
            config.read(self.config_path)
        else:
            # Create default config
            config["API"] = {
                "provider": "openai",
                "openai_api_key": "your_api_key_here",
                "openai_model": "gpt-4o",
                "openai_base_url": "https://api.openai.com/v1",
                "ollama_base_url": "http://localhost:11434/v1",
                "ollama_model": "llava",
                "llamacpp_base_url": "http://localhost:8080/v1",
                "llamacpp_model": "llava",
            }

        # Ensure required sections exist with defaults if not present
        if "Canvas" not in config:
            config["Canvas"] = {"width": "800", "height": "600"}
        if "LLM" not in config:
            config["LLM"] = {"max_tokens": "1000"}
        if "Shortcuts" not in config:
            config["Shortcuts"] = {
                "tool_pen": "<Control>c",
                "tool_eraser": "<Control>e",
                "clear_canvas": "<Control>d",
                "submit": "<Control>s",
            }

        return config

    def get(self, section: str, key: str, fallback: str = "") -> str:
        """Get a configuration value.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Default value if key not found.

        Returns:
            Configuration value as string.
        """
        return self._config.get(section, key, fallback=fallback)

    def save(self):
        """Save current configuration to file."""
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        with open(self.config_path, "w") as f:
            self._config.write(f)

    @property
    def width(self) -> int:
        """Get canvas width."""
        return int(self.get("Canvas", "width", fallback="800"))

    @property
    def height(self) -> int:
        """Get canvas height."""
        return int(self.get("Canvas", "height", fallback="600"))

    @property
    def max_tokens(self) -> int:
        """Get maximum tokens for LLM response."""
        return int(self.get("LLM", "max_tokens", fallback="1000"))

    @property
    def prompt(self) -> str:
        """Get LLM prompt for image conversion."""
        return self.get(
            "LLM",
            "prompt",
            fallback="Convert the handwritten text and mathematical formulas in this image to LaTeX. Only output the LaTeX code without any explanation or thinking.",
        )

    @property
    def shortcut_tool_pen(self) -> str:
        """Get keyboard shortcut for pen tool."""
        return self.get("Shortcuts", "tool_pen", fallback="<Control>c")

    @property
    def shortcut_tool_eraser(self) -> str:
        """Get keyboard shortcut for eraser tool."""
        return self.get("Shortcuts", "tool_eraser", fallback="<Control>e")

    @property
    def shortcut_clear_canvas(self) -> str:
        """Get keyboard shortcut for clearing canvas."""
        return self.get("Shortcuts", "clear_canvas", fallback="<Control>d")

    @property
    def shortcut_submit(self) -> str:
        """Get keyboard shortcut for submitting to LLM."""
        return self.get("Shortcuts", "submit", fallback="<Control>s")
