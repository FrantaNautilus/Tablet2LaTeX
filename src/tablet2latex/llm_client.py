"""
LLM client management for Tablet2LaTeX.
"""

# ruff: noqa: E402 - gi.require_version must precede gi.repository imports

import logging
from typing import TYPE_CHECKING, Optional

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib
from openai import OpenAI

import pyperclip

from .llm_output import LLMOutputProcessor

if TYPE_CHECKING:
    from .config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """Manages LLM client initialization and API calls."""

    def __init__(self, config: "Config") -> None:
        """Initialize the LLM client.

        Args:
            config: Config object containing API configuration.
        """
        self.config = config
        self.client: Optional[OpenAI] = None
        self.model: Optional[str] = None
        self._init_client()

    def _init_client(self):
        """Initialize the OpenAI client based on configuration."""
        provider = self.config.get("API", "provider", fallback="openai")

        if provider == "openai":
            self._init_openai_client()
        elif provider == "ollama":
            self._init_ollama_client()
        elif provider == "llamacpp":
            self._init_llamacpp_client()
        else:
            self.client = None
            self.model = None

    def _init_openai_client(self):
        """Initialize OpenAI client."""
        api_key = self.config.get("API", "openai_api_key", fallback="")
        base_url = self.config.get(
            "API", "openai_base_url", fallback="https://api.openai.com/v1"
        )
        self.model = self.config.get("API", "openai_model", fallback="gpt-4o")

        if api_key and api_key != "your_api_key_here":
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None

    def _init_ollama_client(self):
        """Initialize Ollama client."""
        base_url = self.config.get(
            "API", "ollama_base_url", fallback="http://localhost:11434/v1"
        )
        self.model = self.config.get("API", "ollama_model", fallback="llava")
        self.client = OpenAI(api_key="ollama", base_url=base_url)

    def _init_llamacpp_client(self):
        """Initialize llama.cpp client."""
        base_url = self.config.get(
            "API", "llamacpp_base_url", fallback="http://localhost:8080/v1"
        )
        self.model = self.config.get("API", "llamacpp_model", fallback="llava")
        self.client = OpenAI(api_key="llamacpp", base_url=base_url)

    def is_configured(self) -> bool:
        """Check if the client is properly configured.

        Returns:
            True if client is configured and ready, False otherwise.
        """
        return self.client is not None and self.model is not None

    def submit_to_llm(
        self, image_base64: str, status_label, max_tokens: int = 1000
    ) -> Optional[str]:
        """Send the canvas image to the LLM and process the response.

        Args:
            image_base64: Base64 encoded PNG image.
            status_label: GTK Label for status updates.
            max_tokens: Maximum tokens for the response.

        Returns:
            Processed LaTeX string or None on error.
        """
        if not self.is_configured():
            GLib.idle_add(
                lambda: status_label.set_text(
                    "Error: LLM client not configured. Please check config.ini"
                )
            )
            return None

        # Local non-None references for mypy narrowing
        client = self.client
        model = self.model
        if client is None or model is None:
            return None

        try:
            GLib.idle_add(lambda: status_label.set_text("Sending to LLM..."))

            # Create the API request
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.config.prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
            )

            # Extract the response
            if not response.choices:
                GLib.idle_add(
                    lambda: status_label.set_text("Error: Empty response from LLM")
                )
                return None
            latex_output = response.choices[0].message.content or ""

            # Process the output
            latex_output = LLMOutputProcessor.process(latex_output)

            # Copy to clipboard (guard against excessive output)
            if latex_output and len(latex_output) < 10000:
                pyperclip.copy(latex_output)

            msg = f"Success! LaTeX copied to clipboard ({len(latex_output)} chars)"
            GLib.idle_add(lambda m=msg: status_label.set_text(m))

            return latex_output

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            GLib.idle_add(lambda m=error_msg: status_label.set_text(m))
            logger.exception("Error sending to LLM")
            return None
