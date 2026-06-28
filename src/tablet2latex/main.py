"""
Main entry point for Tablet2LaTeX application.
"""

import sys

# ruff: noqa: E402 - gi.require_version must precede gi.repository imports

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from .config import Config
from .canvas import Canvas
from .llm_client import LLMClient
from .ui import UI


class Tablet2LaTeXApp(Adw.Application):
    """Main application class for Tablet2LaTeX."""

    def __init__(self):
        """Initialize the application."""
        super().__init__(
            application_id="io.github.frantanautilus.tablet2latex",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

        # Load configuration
        self.config = Config()

        # Initialize canvas
        self.canvas = Canvas(self.config.width, self.config.height)

        # Initialize LLM client
        self.llm_client = LLMClient(self.config)

        # Initialize UI
        self.ui = None

    def do_activate(self):
        """Handle application activation."""
        # Initialize UI with config for keyboard shortcuts
        self.ui = UI(self, self.canvas, self.llm_client, self.config)

        # Create and show UI
        self.ui.create_ui()

    def run(self):
        """Run the application."""
        return super().run(None)


def main():
    """Main entry point."""
    app = Tablet2LaTeXApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
