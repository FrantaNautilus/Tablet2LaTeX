FROM mcr.microsoft.com/devcontainers/python:3.14-trixie

# Install system dependencies for GTK4 + libadwaita development,
# PyGObject, Cairo, pkg-config, and Flatpak building support.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        # GTK4 / libadwaita + introspection
        libgtk-4-dev \
        libadwaita-1-dev \
        gir1.2-gtk-4.0 \
        gir1.2-adw-1 \
        gobject-introspection \
        libgirepository1.0-dev \
        # Cairo
        libcairo2-dev \
        # Build tooling
        pkg-config \
        build-essential \
        python3-dev \
        # Flatpak
        flatpak \
        flatpak-builder \
        # General dev tools
        git \
        curl \
        ca-certificates \
        # Clipboard helpers (for the app)
        wl-clipboard \
        xclip \
    && rm -rf /var/lib/apt/lists/*

# Install 'just' task runner (https://github.com/casey/just)
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Upgrade pip and install Python dependencies
COPY requirements_gtk.txt /tmp/requirements_gtk.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements_gtk.txt \
    # PyGObject is required for gi.repository but not in requirements_gtk.txt
    && pip install PyGObject \
    # Dev / test / lint tools (matching the Nix flake)
    && pip install ruff black mypy pytest pytest-cov

# Pre-add flathub remote (SDK install is done via `just flatpak-setup` to keep image smaller)
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true

WORKDIR /workspaces/tablet2latex

# Default to bash with a helpful message
CMD ["bash", "-c", "echo 'Tablet2LaTeX devcontainer ready. Use `just` for tasks (just --list).'; exec bash"]
