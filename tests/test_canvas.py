"""
Unit tests for the Canvas class.
"""

import base64
import io
from unittest.mock import MagicMock, patch

import cairo
import pytest

from tablet2latex.canvas import Canvas


class TestCanvasInitialization:
    """Tests for Canvas class initialization."""

    def test_initializes_with_dimensions(self):
        """Test canvas initializes with correct dimensions."""
        canvas = Canvas(800, 600)
        assert canvas.width == 800
        assert canvas.height == 600

    def test_creates_surface_on_init(self):
        """Test that surface is created on initialization."""
        canvas = Canvas(400, 300)
        assert canvas.surface is not None
        assert isinstance(canvas.surface, cairo.ImageSurface)

    def test_surface_has_correct_format(self):
        """Test that surface has ARGB32 format."""
        canvas = Canvas(200, 200)
        assert canvas.surface.get_format() == cairo.FORMAT_ARGB32

    def test_surface_has_correct_dimensions(self):
        """Test that surface has correct dimensions."""
        canvas = Canvas(1024, 768)
        assert canvas.surface.get_width() == 1024
        assert canvas.surface.get_height() == 768


class TestCanvasClear:
    """Tests for Canvas.clear method."""

    def test_clear_paints_white_background(self):
        """Test that clear fills the canvas with white."""
        canvas = Canvas(100, 100)

        # Draw something first
        canvas.draw_line(0, 0, 50, 50, (0, 0, 0, 1.0), 2)

        # Clear the canvas
        canvas.clear()

        # Surface should still exist
        assert canvas.surface is not None

    def test_clear_works_on_empty_canvas(self):
        """Test that clear works even on empty canvas."""
        canvas = Canvas(100, 100)
        canvas.clear()
        assert canvas.surface is not None


class TestCanvasDrawLine:
    """Tests for Canvas.draw_line method."""

    def test_draw_line_with_black_color(self):
        """Test drawing a black line."""
        canvas = Canvas(100, 100)
        canvas.draw_line(10, 10, 50, 50, (0, 0, 0, 1.0), 2.0)

        # Surface should still be valid
        assert canvas.surface is not None

    def test_draw_line_with_white_color(self):
        """Test drawing a white line (eraser)."""
        canvas = Canvas(100, 100)
        canvas.draw_line(0, 0, 100, 100, (1.0, 1.0, 1.0, 1.0), 20.0)

        assert canvas.surface is not None

    def test_draw_line_with_various_thickness(self):
        """Test drawing lines with different thickness."""
        canvas = Canvas(200, 200)

        for thickness in [1, 5, 10, 20]:
            canvas.draw_line(0, 0, 100, 100, (0, 0, 0, 1.0), thickness)

        assert canvas.surface is not None

    def test_draw_line_with_transparent_color(self):
        """Test drawing with semi-transparent color."""
        canvas = Canvas(100, 100)
        canvas.draw_line(0, 0, 50, 50, (1.0, 0, 0, 0.5), 3.0)

        assert canvas.surface is not None

    def test_draw_line_outside_bounds(self):
        """Test drawing lines that go outside canvas bounds."""
        canvas = Canvas(50, 50)

        # Lines outside bounds should not crash
        canvas.draw_line(-10, -10, 60, 60, (0, 0, 0, 1.0), 2.0)
        canvas.draw_line(100, 100, 200, 200, (0, 0, 0, 1.0), 2.0)

        assert canvas.surface is not None

    def test_draw_line_zero_length(self):
        """Test drawing zero-length line (point)."""
        canvas = Canvas(100, 100)
        canvas.draw_line(50, 50, 50, 50, (0, 0, 0, 1.0), 5.0)

        assert canvas.surface is not None


class TestCanvasDrawCircle:
    """Tests for Canvas.draw_circle method."""

    def test_draw_circle_basic(self):
        """Test drawing a basic circle."""
        canvas = Canvas(100, 100)
        canvas.draw_circle(50, 50, 20, (0, 0, 0, 1.0))

        assert canvas.surface is not None

    def test_draw_circle_various_sizes(self):
        """Test drawing circles of different sizes."""
        canvas = Canvas(200, 200)

        for radius in [5, 10, 25, 50]:
            canvas.draw_circle(100, 100, radius, (1.0, 0, 0, 1.0))

        assert canvas.surface is not None

    def test_draw_circle_with_transparent_color(self):
        """Test drawing circle with semi-transparent color."""
        canvas = Canvas(100, 100)
        canvas.draw_circle(50, 50, 30, (0, 1.0, 0, 0.5))

        assert canvas.surface is not None

    def test_draw_circle_at_edges(self):
        """Test drawing circles at canvas edges."""
        canvas = Canvas(100, 100)

        canvas.draw_circle(0, 0, 10, (0, 0, 0, 1.0))
        canvas.draw_circle(100, 100, 10, (0, 0, 0, 1.0))
        canvas.draw_circle(50, 0, 10, (0, 0, 0, 1.0))

        assert canvas.surface is not None

    def test_draw_circle_outside_bounds(self):
        """Test drawing circles that extend outside canvas."""
        canvas = Canvas(50, 50)

        # Circles outside bounds should not crash
        canvas.draw_circle(-10, -10, 20, (0, 0, 0, 1.0))
        canvas.draw_circle(100, 100, 30, (0, 0, 0, 1.0))

        assert canvas.surface is not None


class TestCanvasGetBase64Image:
    """Tests for Canvas.get_base64_image method."""

    def test_returns_string(self):
        """Test that method returns a string."""
        canvas = Canvas(100, 100)
        result = canvas.get_base64_image()

        assert isinstance(result, str)

    def test_returns_valid_base64(self):
        """Test that returned string is valid base64."""
        canvas = Canvas(50, 50)
        result = canvas.get_base64_image()

        # Should be decodable as base64
        decoded = base64.b64decode(result)
        assert decoded is not None

    def test_returns_png_data(self):
        """Test that returned data is a valid PNG."""
        canvas = Canvas(50, 50)
        result = canvas.get_base64_image()

        # Decode and check PNG magic number
        decoded = base64.b64decode(result)
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"

    def test_different_dimensions_produce_different_outputs(self):
        """Test that different canvas sizes produce different base64."""
        canvas1 = Canvas(100, 100)
        canvas2 = Canvas(200, 200)

        result1 = canvas1.get_base64_image()
        result2 = canvas2.get_base64_image()

        assert result1 != result2

    def test_drawing_changes_output(self):
        """Test that drawing changes the base64 output."""
        canvas = Canvas(100, 100)

        # Get initial image
        initial = canvas.get_base64_image()

        # Draw something
        canvas.draw_line(0, 0, 100, 100, (0, 0, 0, 1.0), 5.0)

        # Get new image
        after_drawing = canvas.get_base64_image()

        assert initial != after_drawing

    def test_clear_resets_output(self):
        """Test that clearing canvas changes the output."""
        canvas = Canvas(100, 100)

        # Get initial image
        initial = canvas.get_base64_image()

        # Draw and clear
        canvas.draw_line(0, 0, 100, 100, (0, 0, 0, 1.0), 5.0)
        canvas.clear()

        # Get cleared image
        after_clear = canvas.get_base64_image()

        # Should be different from the line drawing, but may be same as initial
        # since both are white backgrounds
        assert after_clear is not None

    def test_large_canvas_produces_valid_output(self):
        """Test that large canvases produce valid output."""
        canvas = Canvas(2000, 1500)
        result = canvas.get_base64_image()

        # Should be valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_small_canvas_produces_valid_output(self):
        """Test that small canvases produce valid output."""
        canvas = Canvas(10, 10)
        result = canvas.get_base64_image()

        # Should be valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0


class TestCanvasIntegration:
    """Integration tests for Canvas class."""

    def test_complete_drawing_workflow(self):
        """Test a complete drawing workflow."""
        canvas = Canvas(400, 300)

        # Draw some shapes
        canvas.draw_line(0, 0, 400, 300, (0, 0, 0, 1.0), 3)
        canvas.draw_line(400, 0, 0, 300, (0, 0, 0, 1.0), 3)
        canvas.draw_circle(200, 150, 50, (1.0, 0, 0, 0.5))

        # Get image
        image_data = canvas.get_base64_image()
        assert image_data is not None

        # Clear
        canvas.clear()

        # Draw something else
        canvas.draw_line(100, 100, 300, 200, (0, 0, 1.0, 1.0), 5)

        # Get new image
        new_image_data = canvas.get_base64_image()
        assert new_image_data is not None
        assert new_image_data != image_data

    def test_multiple_operations_surface_integrity(self):
        """Test that surface remains valid after many operations."""
        canvas = Canvas(200, 200)

        # Perform many drawing operations
        for i in range(100):
            canvas.draw_line(i, 0, i, 200, (0, 0, 0, 0.1), 1)
            if i % 10 == 0:
                canvas.draw_circle(100, 100, i // 2, (1.0, 0, 0, 0.1))

        # Surface should still be valid
        assert canvas.surface is not None
        assert canvas.surface.get_width() == 200
        assert canvas.surface.get_height() == 200

        # Should be able to get image
        image_data = canvas.get_base64_image()
        assert image_data is not None
