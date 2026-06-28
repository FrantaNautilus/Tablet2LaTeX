# Tablet2LaTeX Development Tasks
# Run `just` or `just --list` to see available commands.

set shell := ["bash", "-c"]

# Default: show available tasks
default:
    @just --list

# Run the application
run *args:
    export PYTHONPATH="$PWD/src:$PYTHONPATH"; \
    python tablet2latex.py {{args}}

# Run ruff linter
lint *args:
    ruff check src/tablet2latex/ {{args}}

# Format code with black
format *args:
    black src/tablet2latex/ {{args}}

# Run mypy type checker
typecheck *args:
    mypy src/tablet2latex/ {{args}}

# Run tests (handles tablet2latex.py import conflict)
test *args:
    #!/usr/bin/env bash
    set -e
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    mv "$PWD/tablet2latex.py" "$PWD/tablet2latex.py.bak" 2>/dev/null || true
    pytest -v tests {{args}} || TEST_EXIT=$?
    mv "$PWD/tablet2latex.py.bak" "$PWD/tablet2latex.py" 2>/dev/null || true
    exit ${TEST_EXIT:-0}

# Run all checks (lint + format check + typecheck + test)
check:
    @echo "🔍 Running all checks..."
    @echo ""
    @echo "=== Ruff Linter ==="
    just lint || exit 1
    @echo ""
    @echo "=== Black Formatter Check ==="
    black --check src/tablet2latex/ || exit 1
    @echo ""
    @echo "=== Mypy Type Checker ==="
    just typecheck || exit 1
    @echo ""
    @if [ -d "tests" ]; then \
        echo "=== Pytest ==="; \
        just test || exit 1; \
    else \
        echo "⚠️  No tests directory found, skipping pytest"; \
    fi
    @echo ""
    @echo "✅ All checks passed!"

# === Flatpak tasks ===

# Install required GNOME SDK/Platform for Flatpak builds (runtime-version 50)
flatpak-setup:
    @echo "📦 Installing GNOME 50 SDK and Platform..."
    flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50

# Build Flatpak (non-installing)
flatpak-build:
    @echo "🔨 Building Tablet2LaTeX Flatpak..."
    flatpak-builder --force-clean build-dir io.github.frantanautilus.tablet2latex.json
    @echo "✅ Build complete. Use 'just flatpak-install' to install locally."

# Build and install Flatpak locally for the current user
flatpak-install:
    @echo "📦 Building and installing Tablet2LaTeX Flatpak..."
    flatpak-builder --force-clean --install --user build-dir io.github.frantanautilus.tablet2latex.json
    @echo "✅ Installed. Run with: flatpak run io.github.frantanautilus.tablet2latex"

# Clean Flatpak build artifacts
flatpak-clean:
    rm -rf build-dir .flatpak-builder export tablet2latex.flatpak || true
    @echo "🧹 Flatpak build artifacts cleaned."
