 # Tablet2LaTeX - Agent Guidelines

## Project Overview

Tablet2LaTeX is a GTK4-based Python application for converting handwritten text and mathematical formulas to LaTeX using vision-enabled LLMs (OpenAI, Ollama, LlamaCpp). Refactored as a proper Python package with modular architecture.

## Development Environment

### Starting the Development Environment

**Option A – Nix (recommended on NixOS / with Nix installed)**

```bash
nix develop
```

This provides Python 3.12 with GTK4, libadwaita, and all dependencies.

**Option B – Dev Container (alternative for non-Nix users)**

1. Open the repository in VS Code.
2. Run **Dev Containers: Reopen in Container** (or use GitHub Codespaces).
3. The container uses Python 3.14 on Debian trixie and includes:
   - GTK4 + libadwaita + PyGObject
   - All Python dependencies
   - `just`, `ruff`, `black`, `mypy`, `pytest`
   - `flatpak` + `flatpak-builder` (for building the Flatpak package)

After the container starts, run:
```bash
just --list
```

 ### Running the Application

```bash
# In Nix dev shell or devcontainer
python tablet2latex.py
# or (after setup)
tablet2latex-run

# Or using nix run
nix run .#run

# Or using just (devcontainer or anywhere with just installed)
just run
```

## Build, Lint, and Test Commands

 ### Code Quality

```bash
# Run ruff linter
just lint
# or (Nix)
nix run .#lint
# or (inside dev shell)
tablet2latex-lint

# Format code with black
just format
# or (Nix)
nix run .#format
# or (inside dev shell)
tablet2latex-format

# Type checking with mypy
just typecheck
# or (Nix)
nix run .#typecheck
# or (inside dev shell)
tablet2latex-typecheck

# Run tests with pytest
just test
# or (Nix)
nix run .#test
# or (inside dev shell)
tablet2latex-test

# Run all checks (lint, format check, typecheck, test)
just check
# or (Nix)
nix run .#check
# or (inside dev shell)
tablet2latex-check
```

### Build Commands

```bash
# Using just (recommended in devcontainer)
just flatpak-setup      # install GNOME SDK once
just flatpak-build
just flatpak-install
just flatpak-clean

# Or using the script (anywhere)
./build-flatpak.sh

# Or using nix
nix build
```

 ## Code Style Guidelines

### Import Organization

- Import standard library modules first
- Import third-party packages (gi, PIL, numpy, etc.) second
- Import local modules last
- Group related imports together

```python
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GLib

import configparser
import base64
import io
import os
import sys
from PIL import Image
import numpy as np
import pyperclip
from openai import OpenAI
import cairo
```

 ### Naming Conventions

- **Classes**: PascalCase (e.g., `Tablet2LaTeXApp`, `Adw.ApplicationWindow`, `Canvas`, `Config`, `LLMClient`)
- **Methods**: snake_case (e.g., `_load_config`, `create_ui`, `on_activate`)
- **Private methods**: Leading underscore (e.g., `_init_surface`, `_send_to_llm`)
- **Variables**: snake_case (e.g., `drawing_area`, `status_label`, `api_key`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `FORMAT_ARGB32`, `GDK_BUTTON_PRIMARY`)

### Method Documentation

All public methods should have docstrings with:
- Brief description
- Parameters (when applicable)
- Return values

```python
def _load_config(self):
    """Load configuration from config.ini file."""
    # implementation
```

 ### GTK/Gi Repository Imports

Always require GTK versions and import from gi.repository:

```python
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GLib
```

### Error Handling

- Use try/except for API calls and external operations
- Use GLib.idle_add for UI updates to avoid blocking the main thread
- Print errors for debugging
- Update status labels for user feedback

```python
try:
    response = self.client.chat.completions.create(...)
    GLib.idle_add(lambda: status_label.set_text("Success!"))
except Exception as e:
    GLib.idle_add(lambda: status_label.set_text(f"Error: {str(e)}"))
    print(f"Error: {e}")
```

### Cairo Drawing

- Use `cairo.ImageSurface` with `FORMAT_ARGB32` for canvas
- Use `cr.set_source_rgb()` for solid colors
- Use `cr.set_source_rgba()` for transparent colors
- Always create new Context for each drawing operation
- Call `queue_draw()` to update the widget

```python
cr = cairo.Context(self.surface)
cr.set_source_rgb(1, 1, 1)  # White background
cr.paint()
```

### GTK Signal Handling

Use event controllers for mouse/touch handling:

```python
motion_controller = Gtk.EventControllerMotion()
motion_controller.connect("motion", self._on_drawing_motion, self.drawing_area)
self.drawing_area.add_controller(motion_controller)

click_controller = Gtk.GestureClick()
click_controller.set_button(Gdk.BUTTON_PRIMARY)
click_controller.connect("pressed", self._on_drawing_button_press, self.drawing_area)
self.drawing_area.add_controller(click_controller)
```

  ### Configuration Management

Use the Config class for INI-based configuration:
- Section format: `config.get("SECTION", "key", fallback="default")`
- Fallback values should be sensible defaults
- Validate required fields before use
- Configuration is automatically loaded from XDG standard location (~/.config/tablet2latex/config.ini)
- Supports legacy config.ini location for backward compatibility

```python
config = Config()
api_key = config.get("API", "openai_api_key", fallback="")
width = config.width  # Returns int
height = config.height  # Returns int
max_tokens = config.max_tokens  # Returns int
```

**Configuration Location:**
- Primary: `~/.config/tablet2latex/config.ini` (XDG standard location)
- Fallback: `config.ini` in application directory (legacy)
- Custom path can be provided: `Config("/path/to/custom/config.ini")`

 ### LLM Integration

- Initialize client based on configured provider
- Handle multiple providers: openai, ollama, llamacpp
- Use base64 encoding for image transmission
- Process output to extract LaTeX code

```python
from .llm_client import LLMClient
from .llm_output import LLMOutputProcessor
from .canvas import Canvas

# Initialize client
llm_client = LLMClient(config)
canvas = Canvas(config.width, config.height)

# Submit to LLM
latex_output = llm_client.submit_to_llm(
    canvas.get_base64_image(),
    status_label,
    max_tokens=config.max_tokens
)
# Process output
cleaned_output = LLMOutputProcessor.process(latex_output)
# Copy to clipboard
LLMOutputProcessor.copy_to_clipboard(cleaned_output)
```

### Output Processing

Clean LLM output by:
- Removing markdown code blocks with ```latex
- Stripping thinking/explanation text
- Preserving LaTeX code structure

```python
from .llm_output import LLMOutputProcessor

cleaned_output = LLMOutputProcessor.process(latex_output)
LLMOutputProcessor.copy_to_clipboard(cleaned_output)
```

### Module Responsibilities

- **main.py**: Application entry point, initializes components
- **config.py**: Configuration loading and defaults
- **canvas.py**: Cairo drawing operations and surface management
- **llm_client.py**: LLM client initialization and API calls
- **llm_output.py**: Output processing and clipboard operations
- **ui.py**: GTK4 user interface creation and event handling

## Entry Point Script

The application can be run using the entry point script:

```bash
python tablet2latex.py
```

This script adds the parent directory to the Python path and imports from the package.

## Project Structure

```
tablet2latex/
├── tablet2latex.py        # Entry point script
├── tablet2latex_gtk.py    # Original single-file version (deprecated)
├── config.ini             # Configuration file
├── requirements_gtk.txt   # Python dependencies
├── flake.nix              # Nix development environment
├── build-flatpak.sh       # Flatpak build script
└── src/tablet2latex/      # Python package
    ├── __init__.py        # Package initialization
    ├── main.py            # Application entry point
    ├── config.py          # Configuration management
    ├── canvas.py          # Drawing operations
    ├── llm_client.py      # LLM integration
    ├── llm_output.py      # Output processing
    └── ui.py              # GTK4 user interface
```

 ## Common Patterns

### Drawing State Management

Track drawing state in class attributes:
- `drawing`: Boolean for current drawing state
- `last_x`, `last_y`: Previous position for drawing lines
- `current_tool`: Current tool ('pen' or 'eraser')

### UI Update Pattern

Update UI from background threads using GLib.idle_add:

```python
GLib.idle_add(lambda: status_label.set_text("Processing..."))
GLib.idle_add(lambda: output_text.set_text(latex_output))
```

### Base64 Image Conversion

Convert Cairo surfaces to base64 for LLM API:

```python
from .canvas import Canvas

canvas = Canvas(width, height)
image_base64 = canvas.get_base64_image()
```

## Testing

pytest is configured and ready to use. To add tests:
 1. Create test files in `tests/` directory (e.g., `tests/test_config.py`)
 2. Use pytest as the test runner via `nix run .#test` or `tablet2latex-test`
 3. Mock GTK widgets and external API calls
 4. Test drawing operations, configuration loading, and LLM integration
 5. Test each module in isolation

### Example Test File

Create `tests/test_config.py`:
```python
import pytest
from tablet2latex.config import Config

def test_config_defaults():
    config = Config()
    assert config.width == 800
    assert config.height == 600
```

### Running Tests

```bash
# Run all tests
nix run .#test
# or
tablet2latex-test

# Run with coverage
nix run .#test -- --cov=src/tablet2latex

# Run specific test file
tablet2latex-test tests/test_config.py
```

## Flatpak Packaging

Build and install Flatpak package:

```bash
# Build
./build-flatpak.sh

# Install locally
flatpak-builder --install --user com.example.tablet2latex.json

# Run
flatpak run com.example.tablet2latex
```

## Key Dependencies

- **GTK4**: Modern GTK framework
- **libadwaita**: GNOME UI components
- **Pillow**: Image processing
- **NumPy**: Canvas operations
- **OpenAI**: LLM API client
- **Pyperclip**: Clipboard integration
- **PyGObject**: GTK Python bindings
- **ConfigParser**: Configuration management
- **Cairo**: Drawing operations

## Development Workflow

1. Make changes to `src/tablet2latex/` modules
2. Run all checks: `nix run .#check` or `tablet2latex-check`
3. Format code if needed: `nix run .#format` or `tablet2latex-format`
4. Test manually: `python tablet2latex.py` or `nix run .#run`
5. Verify configuration: Check `config.ini` has valid API key
6. Build flatpak when ready: `./build-flatpak.sh`

