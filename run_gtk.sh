#!/bin/bash
# Run script for GTK4 version of Tablet2LaTeX

echo "Starting Tablet2LaTeX GTK4 version..."

# Check if we're in the correct directory
if [ ! -f "tablet2latex_gtk.py" ]; then
    echo "Error: tablet2latex_gtk.py not found in current directory"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import gi, cairo" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: GTK4 dependencies not installed"
    echo "Please install GTK4 and PyCairo dependencies:"
    echo "  sudo apt install python3-gi python3-cairo gir1.2-gtk-4.0 gir1.2-adw-1"
    echo "Or use the Nix development environment:"
    echo "  nix develop"
    exit 1
fi

# Run the application
python3 tablet2latex_gtk.py