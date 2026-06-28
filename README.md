 # Tablet2LaTeX - GTK4 Version

A modern GTK4 version of Tablet2LaTeX for converting handwritten text and mathematical formulas to LaTeX using vision-enabled LLMs. Refactored as a proper Python package with modular architecture.

## Features

- **Modern GTK4 Interface**: Built with GTK4 and LibAdwaita for a native GNOME experience
- **Canvas Drawing**: Draw handwritten text and formulas with pen and eraser tools
- **LLM Integration**: Supports multiple LLM providers:
  - OpenAI API (GPT-4 Vision, GPT-4o, etc.)
  - Ollama (local LLM with vision capabilities)
  - LlamaCpp (local LLM server)
- **Clipboard Integration**: Automatically copies the generated LaTeX to your system clipboard
- **Easy Configuration**: Simple INI-based configuration file

## Installation

### Option 1: Using Nix (Recommended on NixOS / with Nix)

1. Clone the repository:
```bash
git clone https://github.com/VlastimilHudecek/Tablet2LaTeX.git
cd Tablet2LaTeX
```

 2. Enter the development shell:
 ```bash
 nix develop
 ```

 3. Run the application:
 ```bash
 python tablet2latex.py
 ```

### Option 2: Using Dev Container (VS Code / Codespaces)

1. Open the repository in Visual Studio Code.
2. Run the command **Dev Containers: Reopen in Container**.
3. After the container builds, run:
   ```bash
   just --list
   just run
   ```

The devcontainer provides Python 3.14, GTK4, libadwaita, `just`, and full Flatpak build support. It is the recommended alternative for users without Nix.

### Option 3: Manual Installation (host system)

1. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject python3-cairo gtk4 libadwaita

# Arch Linux
sudo pacman -S python-gobject python-cairo gtk4 libadwaita
```

 2. Install Python dependencies:
 ```bash
 pip install -r requirements_gtk.txt
 ```

 3. Run the application:
 ```bash
 python tablet2latex.py
 ```

### Option 4: Using Flatpak

TODO

## Configuration

Edit `config.ini` to configure your LLM provider. The configuration file is located at:

- **Primary (recommended)**: `~/.config/tablet2latex/config.ini` (XDG standard location)
- **Fallback**: `config.ini` in the application directory (legacy)

The application will automatically use the XDG standard location if available.

### Configuration File Location

Tablet2LaTeX uses the XDG Base Directory specification for configuration files.

**New Location (recommended):**
```bash
~/.config/tablet2latex/config.ini
```

**Legacy Location (deprecated):**
```bash
config.ini (in application directory)
```

**Migration:**
1. The application automatically migrates existing configurations to the XDG location
2. If you have a `config.ini` in the application directory, it will be copied to `~/.config/tablet2latex/`
3. No manual migration required

### OpenAI
```ini
[API]
provider = openai
openai_api_key = your_api_key_here
openai_model = gpt-4o
openai_base_url = https://api.openai.com/v1
```

### Ollama (Local)
```ini
[API]
provider = ollama
ollama_base_url = http://localhost:11434/v1
ollama_model = llava
```

### LlamaCpp (Local)
```ini
[API]
provider = llamacpp
llamacpp_base_url = http://localhost:8080/v1
llamacpp_model = llava
```

 ## Usage

 1. Run the application:
 ```bash
 python tablet2latex.py
 ```

2. Use the tools:
   - Click **Pen** to switch to drawing mode
   - Click **Eraser** to switch to eraser mode
   - Click **Clear** to clear the canvas
   - Draw your handwritten text or mathematical formulas on the canvas
   - Click **Submit** to send the image to the LLM

3. The generated LaTeX will be:
   - Displayed in the output text box
   - Automatically copied to your system clipboard

## Requirements

- Python 3.8+
- Linux operating system
- Graphic tablet (optional, mouse also works)
- LLM provider (OpenAI API key or local Ollama/LlamaCpp server)

## Dependencies

### System Dependencies
- GTK4 (>= 4.0)
- LibAdwaita (>= 1.0)
- Python 3 GObject bindings
- Python Cairo bindings

  ### Python Dependencies
  - `Pillow>=10.0.0` - Image processing
  - `OpenAI>=1.0.0` - LLM API client
  - `Pyperclip>=1.8.2` - Clipboard integration
  - `NumPy>=1.24.0` - Canvas operations
  - `PyCairo>=1.24.0` - Cairo graphics
  - `PyGObject` (provides `gi` for GTK)

## Project Structure

```
tablet2latex/
├── tablet2latex.py        # Entry point script
├── tablet2latex_gtk.py    # Original single-file version (deprecated)
├── config.ini             # Configuration file
├── requirements_gtk.txt   # Python dependencies
├── flake.nix              # Nix development environment
├── Justfile                 # just tasks (run, lint, test, flatpak-*, …)
├── build-flatpak.sh       # Flatpak build script
├── .devcontainer/         # Dev container (VS Code / Codespaces) – Python 3.14 + Flatpak support
└── src/tablet2latex/      # Python package
    ├── __init__.py        # Package initialization
    ├── main.py            # Application entry point
    ├── config.py          # Configuration management
    ├── canvas.py          # Drawing operations
    ├── llm_client.py      # LLM integration
    ├── llm_output.py      # Output processing
    └── ui.py              # GTK4 user interface
```

  ## Running the Application

  ### Using the entry point script:
  ```bash
  python tablet2latex.py
  ```

  ### From the nix development environment:
  ```bash
  nix run .#run
  ```

  ### From a devcontainer (with `just`):
  ```bash
  just run
  ```

## Comparison with Dear PyGui Version

| Feature | Dear PyGui Version | GTK4 Version |
|---------|-------------------|--------------|
| UI Framework | Dear PyGui | GTK4 + LibAdwaita |
| Native Look | No | Yes |
| Platform Integration | Limited | Full |
| Performance | Good | Excellent |
| Dependencies | Python-only | System + Python |
| Memory Usage | Moderate | Low |
| Modern Features | Limited | Full |
| Accessibility | Limited | Full |

## Known Issues

1. **Drawing Performance**: Large canvas sizes may cause performance issues
2. **Wayland**: Some features may behave differently on Wayland vs X11
3. **High DPI**: High DPI displays may require scaling adjustments

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

You have two recommended options:

**A. Nix (fastest on NixOS / with Nix installed)**
```bash
nix develop
```

**B. Dev Container (works everywhere with VS Code or GitHub Codespaces)**
1. Open in VS Code → **Dev Containers: Reopen in Container**
2. After startup:
   ```bash
   just --list
   ```

Then:
3. Make your changes
4. Run `just check` (or `tablet2latex-check`)
5. Submit a pull request