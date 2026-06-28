#!/bin/bash
# Flatpak build script for Tablet2LaTeX GTK4 version

set -e

echo "🔨 Building Tablet2LaTeX GTK4 Flatpak..."

# Check if flatpak-builder is installed
if ! command -v flatpak-builder &> /dev/null; then
    echo "❌ flatpak-builder not found. Please install it:"
    echo "   sudo apt install flatpak-builder"
    echo "   flatpak install flathub org.flatpak.Builder"
    exit 1
fi

# Check if we have the manifest
if [ ! -f "io.github.frantanautilus.tablet2latex.json" ]; then
    echo "❌ Flatpak manifest not found: io.github.frantanautilus.tablet2latex.json"
    exit 1
fi

# Build the Flatpak
echo "📦 Building Flatpak package..."
flatpak-builder --force-clean build-dir io.github.frantanautilus.tablet2latex.json

echo "✅ Flatpak build completed successfully!"
echo ""
echo "📦 To install locally:"
echo "   flatpak-builder --install --user build-dir io.github.frantanautilus.tablet2latex.json"
echo ""
echo "🚀 To run the application:"
echo "   flatpak run io.github.frantanautilus.tablet2latex"
echo ""
echo "📦 To create a bundle:"
echo "   flatpak build-export export build-dir"
echo "   flatpak build-bundle export tablet2latex.flatpak io.github.frantanautilus.tablet2latex"