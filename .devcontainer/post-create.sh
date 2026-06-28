#!/usr/bin/env bash
set -euo pipefail

echo "📦 Tablet2LaTeX Dev Container Post-Create Setup"

# Ensure runtime dir for Wayland/XDG exists
mkdir -p /tmp/runtime-vscode
chmod 700 /tmp/runtime-vscode || true

# Install 'just' if not already present (Dockerfile should have done it, but be defensive)
if ! command -v just &>/dev/null; then
  echo "Installing just..."
  curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
fi

# Install Python dev dependencies (in case Dockerfile layer is stale)
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel >/dev/null
pip install -r requirements_gtk.txt
pip install PyGObject ruff black mypy pytest pytest-cov

# Create a local bin dir for helper scripts
mkdir -p "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"

# Create just-powered helper scripts that replicate the Nix flake behavior
# These are thin wrappers that call `just <task>`

cat > "$HOME/.local/bin/tablet2latex-run" << 'EOF'
#!/usr/bin/env bash
exec just run "$@"
EOF

cat > "$HOME/.local/bin/tablet2latex-lint" << 'EOF'
#!/usr/bin/env bash
exec just lint "$@"
EOF

cat > "$HOME/.local/bin/tablet2latex-format" << 'EOF'
#!/usr/bin/env bash
exec just format "$@"
EOF

cat > "$HOME/.local/bin/tablet2latex-typecheck" << 'EOF'
#!/usr/bin/env bash
exec just typecheck "$@"
EOF

cat > "$HOME/.local/bin/tablet2latex-test" << 'EOF'
#!/usr/bin/env bash
exec just test "$@"
EOF

cat > "$HOME/.local/bin/tablet2latex-check" << 'EOF'
#!/usr/bin/env bash
exec just check "$@"
EOF

chmod +x "$HOME/.local/bin/tablet2latex-"*

echo "✅ Helper commands installed: tablet2latex-run, tablet2latex-lint, etc."

# Prepare Flatpak SDK (optional, non-fatal if user doesn't want to wait)
if command -v flatpak &>/dev/null; then
  echo "📦 Adding flathub remote (if missing)..."
  flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true
  echo "ℹ️  To install GNOME SDK for Flatpak builds: just flatpak-setup"
fi

echo ""
echo "🚀 Tablet2LaTeX dev environment is ready!"
echo "   Run 'just --list' to see available tasks."
echo "   Or use the tablet2latex-* helper commands."
