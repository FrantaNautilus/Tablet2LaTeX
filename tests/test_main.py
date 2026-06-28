"""
Unit tests for the main Tablet2LaTeXApp class.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest


# Mock gi.repository modules before importing main
@pytest.fixture(scope="module", autouse=True)
def mock_gtk_modules():
    """Mock GTK modules for testing."""
    mock_gi = MagicMock()
    mock_gi.require_version = MagicMock()

    mock_gtk = MagicMock()
    mock_gtk.ApplicationFlags = MagicMock()
    mock_gtk.ApplicationFlags.DEFAULT_FLAGS = 0

    mock_adw = MagicMock()
    mock_gio = MagicMock()
    mock_glib = MagicMock()
    mock_gdk = MagicMock()

    # Setup mock classes
    mock_adw.Application = MagicMock
    mock_adw.ApplicationWindow = MagicMock
    mock_adw.HeaderBar = MagicMock
    mock_adw.ToolbarView = MagicMock
    mock_adw.Clamp = MagicMock
    mock_adw.Bin = MagicMock
    mock_adw.PreferencesGroup = MagicMock

    mock_gtk.Box = MagicMock
    mock_gtk.DrawingArea = MagicMock
    mock_gtk.Label = MagicMock
    mock_gtk.Button = MagicMock
    mock_gtk.TextView = MagicMock
    mock_gtk.ScrolledWindow = MagicMock
    mock_gtk.EventControllerMotion = MagicMock
    mock_gtk.GestureClick = MagicMock
    mock_gtk.EventControllerKey = MagicMock
    mock_gtk.Orientation = MagicMock
    mock_gtk.Orientation.VERTICAL = 0
    mock_gtk.Orientation.HORIZONTAL = 1
    mock_gtk.Align = MagicMock
    mock_gtk.Align.START = 0
    mock_gtk.Overflow = MagicMock
    mock_gtk.PolicyType = MagicMock

    mock_gdk.BUTTON_PRIMARY = 1
    mock_gdk.DeviceToolType = MagicMock()
    mock_gdk.DeviceToolType.ERASER = 1

    modules = {
        "gi": mock_gi,
        "gi.repository": MagicMock(),
        "gi.repository.Gtk": mock_gtk,
        "gi.repository.Adw": mock_adw,
        "gi.repository.Gio": mock_gio,
        "gi.repository.GLib": mock_glib,
        "gi.repository.Gdk": mock_gdk,
    }

    with patch.dict("sys.modules", modules):
        with patch("gi.require_version", mock_gi.require_version):
            yield


class TestMainAppInitialization:
    """Tests for Tablet2LaTeXApp initialization."""

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_app_initializes_components(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that app initializes all components on creation."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        # Import after mocking
        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()

        # Verify components were initialized
        mock_config_class.assert_called_once()
        mock_canvas_class.assert_called_once_with(800, 600)
        mock_llm_client_class.assert_called_once_with(mock_config)

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_app_stores_components(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that app stores references to components."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()

        assert app.config == mock_config
        assert app.canvas == mock_canvas
        assert app.llm_client == mock_llm_client

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_app_initializes_ui_none(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that UI is initially None."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas_class.return_value = MagicMock()
        mock_llm_client_class.return_value = MagicMock()

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()

        assert app.ui is None


class TestMainAppActivate:
    """Tests for Tablet2LaTeXApp.do_activate."""

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    @patch("tablet2latex.main.UI")
    def test_activate_creates_ui(
        self,
        mock_ui_class,
        mock_llm_client_class,
        mock_canvas_class,
        mock_config_class,
        mock_adw_init,
    ):
        """Test that activation creates the UI."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        mock_ui = MagicMock()
        mock_ui_class.return_value = mock_ui

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()
        app.do_activate()

        # Verify UI was created and initialized
        mock_ui_class.assert_called_once_with(
            app, mock_canvas, mock_llm_client, mock_config
        )
        mock_ui.create_ui.assert_called_once()

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    @patch("tablet2latex.main.UI")
    def test_activate_stores_ui_reference(
        self,
        mock_ui_class,
        mock_llm_client_class,
        mock_canvas_class,
        mock_config_class,
        mock_adw_init,
    ):
        """Test that UI reference is stored after activation."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        mock_ui = MagicMock()
        mock_ui_class.return_value = mock_ui

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()
        app.do_activate()

        assert app.ui == mock_ui


class TestMainAppRun:
    """Tests for Tablet2LaTeXApp.run."""

    @patch("tablet2latex.main.Adw.Application.run")
    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_run_calls_parent_run(
        self,
        mock_llm_client_class,
        mock_canvas_class,
        mock_config_class,
        mock_adw_init,
        mock_super_run,
    ):
        """Test that run calls parent class run method."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas_class.return_value = MagicMock()
        mock_llm_client_class.return_value = MagicMock()

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()
        app.run()

        mock_super_run.assert_called_once_with(None)


class TestMainFunction:
    """Tests for main entry point."""

    @patch("tablet2latex.main.Tablet2LaTeXApp")
    @patch("sys.exit")
    def test_main_creates_app_and_runs(self, mock_exit, mock_app_class):
        """Test that main creates app and runs it."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        from tablet2latex.main import main

        main()

        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()
        mock_exit.assert_called_once()


class TestCanvasIntegration:
    """Tests for Canvas integration with app."""

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_canvas_created_with_config_dimensions(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that canvas is created with dimensions from config."""
        mock_config = MagicMock()
        mock_config.width = 1024
        mock_config.height = 768
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client_class.return_value = MagicMock()

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()

        mock_canvas_class.assert_called_once_with(1024, 768)
        assert app.canvas == mock_canvas

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_custom_canvas_dimensions(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that custom canvas dimensions are used."""
        mock_config = MagicMock()
        mock_config.width = 1920
        mock_config.height = 1080
        mock_config_class.return_value = mock_config

        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        mock_llm_client_class.return_value = MagicMock()

        from tablet2latex.main import Tablet2LaTeXApp

        Tablet2LaTeXApp()

        mock_canvas_class.assert_called_once_with(1920, 1080)


class TestLLMClientIntegration:
    """Tests for LLMClient integration with app."""

    @patch("tablet2latex.main.Adw.Application.__init__")
    @patch("tablet2latex.main.Config")
    @patch("tablet2latex.main.Canvas")
    @patch("tablet2latex.main.LLMClient")
    def test_llm_client_created_with_config(
        self, mock_llm_client_class, mock_canvas_class, mock_config_class, mock_adw_init
    ):
        """Test that LLM client is created with config."""
        mock_config = MagicMock()
        mock_config.width = 800
        mock_config.height = 600
        mock_config_class.return_value = mock_config

        mock_canvas_class.return_value = MagicMock()

        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        from tablet2latex.main import Tablet2LaTeXApp

        app = Tablet2LaTeXApp()

        mock_llm_client_class.assert_called_once_with(mock_config)
        assert app.llm_client == mock_llm_client
