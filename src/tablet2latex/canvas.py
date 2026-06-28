"""
Canvas drawing operations for Tablet2LaTeX.
"""

from __future__ import annotations

import base64
import io
import math
from typing import Optional

import cairo


class Canvas:
    """Manages the drawing canvas and Cairo operations."""

    def __init__(self, width: int, height: int):
        """Initialize the canvas.

        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
        """
        self.width = width
        self.height = height
        self.surface: Optional[cairo.ImageSurface] = None
        self._init_surface()

    def _init_surface(self):
        """Initialize the Cairo drawing surface."""
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.set_source_rgb(1, 1, 1)  # White background
        cr.paint()

    def clear(self):
        """Clear the canvas to white background."""
        if self.surface:
            cr = cairo.Context(self.surface)
            cr.set_source_rgb(1, 1, 1)  # White background
            cr.paint()

    def draw_line(
        self, x1: float, y1: float, x2: float, y2: float, color: tuple, thickness: float
    ):
        """Draw a line on the canvas.

        Args:
            x1: Starting x coordinate.
            y1: Starting y coordinate.
            x2: Ending x coordinate.
            y2: Ending y coordinate.
            color: RGBA color tuple (r, g, b, a).
            thickness: Line width in pixels.
        """
        cr = cairo.Context(self.surface)
        cr.set_source_rgba(*color)
        cr.set_line_width(thickness)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

    def draw_circle(self, cx: float, cy: float, radius: float, color: tuple):
        """Draw a filled circle on the canvas.

        Args:
            cx: Circle center x coordinate.
            cy: Circle center y coordinate.
            radius: Circle radius in pixels.
            color: RGBA color tuple (r, g, b, a).
        """
        cr = cairo.Context(self.surface)
        cr.set_source_rgba(*color)
        cr.arc(cx, cy, radius, 0, math.pi * 2)
        cr.fill()

    def get_base64_image(self) -> str:
        """Convert the canvas to base64 encoded PNG image.

        Returns:
            Base64 encoded PNG image string.
        """
        buffer = io.BytesIO()
        if self.surface is None:
            # Return minimal valid transparent PNG base64 if no surface
            return ""
        self.surface.write_to_png(buffer)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode("utf-8")
