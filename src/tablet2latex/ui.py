"""
LibAdwaita user interface for Tablet2LaTeX.
"""

from concurrent.futures import ThreadPoolExecutor

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GLib  # noqa: E402


class UI:
    """Manages the LibAdwaita user interface."""

    def __init__(self, app, canvas, llm_client, config):
        """Initialize the UI.

        Args:
            app: LibAdwaita Application instance.
            canvas: Canvas object.
            llm_client: LLM client instance.
            config: Config instance with keyboard shortcuts.
        """
        self.app = app
        self.canvas = canvas
        self.llm_client = llm_client
        self.config = config

        # Drawing state
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.current_tool = "pen"  # 'pen' or 'eraser'
        self.previous_tool = "pen"  # Tool to restore after stylus eraser is released
        self.pen_size = 3
        self.eraser_size = 20
        self.using_stylus_eraser = False  # Track if stylus eraser is currently active

        # UI widgets
        self.window = None
        self.drawing_area = None
        self.status_label = None
        self.output_text = None
        self.toolbar = None

        # Bounded executor for LLM submissions (prevents unbounded thread creation)
        self._executor = ThreadPoolExecutor(max_workers=1)

    def create_header_bar(self) -> Adw.HeaderBar:
        """Create a LibAdwaita header bar with standard controls.

        Returns:
            HeaderBar widget.
        """
        header_bar = Adw.HeaderBar()
        header_bar.set_show_end_title_buttons(True)
        return header_bar

    def create_ui(self):
        """Create the LibAdwaita user interface."""
        # Create LibAdwaita window
        self.window = Adw.ApplicationWindow(application=self.app)
        self.window.set_title("Tablet2LaTeX")
        self.window.set_default_size(self.canvas.width + 40, self.canvas.height + 350)

        # Create AdwToolbarView with header bar
        toolbar_view = Adw.ToolbarView()
        header_bar = self.create_header_bar()
        toolbar_view.add_top_bar(header_bar)

        # Create main box with spacing
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)

        # Set toolbar view as window content
        toolbar_view.set_content(main_box)
        self.window.set_content(toolbar_view)

        # Create toolbar using Adw.Clamp for responsive layout
        toolbar_clamp = Adw.Clamp()
        toolbar_clamp.set_maximum_size(600)
        toolbar_clamp.set_tightening_threshold(400)

        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.toolbar.set_homogeneous(True)
        toolbar_clamp.set_child(self.toolbar)
        main_box.append(toolbar_clamp)

        # Tool buttons
        self._create_tool_buttons()

        # Status label with Adw style
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_box.set_halign(Gtk.Align.START)

        self.status_label = Gtk.Label(
            label="Ready. Select Pen or Eraser and start drawing."
        )
        self.status_label.add_css_class("dim-label")
        self.status_label.set_halign(Gtk.Align.START)
        status_box.append(self.status_label)
        main_box.append(status_box)

        # Create drawing area container with Adw.Bin for styling
        drawing_bin = Adw.Bin()
        drawing_bin.add_css_class("card")
        drawing_bin.set_overflow(Gtk.Overflow.HIDDEN)

        # Create drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_content_width(self.canvas.width)
        self.drawing_area.set_content_height(self.canvas.height)
        self.drawing_area.set_draw_func(self._on_draw)

        # Set up drawing event controllers
        self._setup_drawing_controllers()

        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()

        drawing_bin.set_child(self.drawing_area)
        main_box.append(drawing_bin)

        # Output section using Adw.PreferencesGroup for modern styling
        output_group = Adw.PreferencesGroup()
        output_group.set_title("LaTeX Output")

        # Text view for LaTeX output
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_size_request(-1, 150)
        scrolled_window.add_css_class("card")

        self.output_text = Gtk.TextView()
        self.output_text.set_editable(False)
        self.output_text.set_monospace(True)
        self.output_text.add_css_class("view")
        scrolled_window.set_child(self.output_text)

        output_group.add(scrolled_window)
        main_box.append(output_group)

        # Show window
        self.window.present()

        # Ensure executor is shut down on window close to avoid thread leaks
        self.window.connect("close-request", self._on_window_close)

    def _on_window_close(self, window):
        """Shutdown background executor on window close."""
        self._executor.shutdown(wait=False)
        return False  # allow the window to close

    def _create_tool_buttons(self):
        """Create tool buttons for the toolbar using styled buttons."""
        pen_btn = Gtk.Button()
        pen_btn.set_icon_name("document-edit-symbolic")
        pen_btn.set_tooltip_text("Pen")
        pen_btn.add_css_class("suggested-action")
        pen_btn.connect("clicked", lambda btn: self._set_tool_pen())
        self.toolbar.append(pen_btn)

        eraser_btn = Gtk.Button()
        eraser_btn.set_icon_name("edit-clear-all-symbolic")
        eraser_btn.set_tooltip_text("Eraser")
        eraser_btn.connect("clicked", lambda btn: self._set_tool_eraser())
        self.toolbar.append(eraser_btn)

        clear_btn = Gtk.Button()
        clear_btn.set_icon_name("edit-delete-symbolic")
        clear_btn.set_tooltip_text("Clear Canvas")
        clear_btn.connect("clicked", lambda btn: self._clear_canvas())
        self.toolbar.append(clear_btn)

        submit_btn = Gtk.Button()
        submit_btn.set_icon_name("mail-send-symbolic")
        submit_btn.set_tooltip_text("Submit to LLM")
        submit_btn.add_css_class("suggested-action")
        submit_btn.connect("clicked", lambda btn: self._submit_canvas())
        self.toolbar.append(submit_btn)

    def _setup_drawing_controllers(self):
        """Set up event controllers for drawing."""
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("motion", self._on_drawing_motion)
        self.drawing_area.add_controller(motion_controller)

        click_controller = Gtk.GestureClick()
        click_controller.set_button(Gdk.BUTTON_PRIMARY)
        click_controller.connect("pressed", self._on_drawing_button_press)
        click_controller.connect("released", self._on_drawing_button_release)
        self.drawing_area.add_controller(click_controller)

        # Set up stylus controller for eraser detection
        self._setup_stylus_controller()

    def _setup_stylus_controller(self):
        """Set up stylus gesture for detecting stylus eraser input."""
        try:
            stylus_gesture = Gtk.GestureStylus()
            stylus_gesture.set_button(0)  # Accept any button (0 = any)
            stylus_gesture.connect("down", self._on_stylus_down)
            stylus_gesture.connect("up", self._on_stylus_up)
            stylus_gesture.connect("motion", self._on_stylus_motion)
            self.drawing_area.add_controller(stylus_gesture)
        except Exception:
            # GestureStylus not available on this GTK version/platform
            pass

    def _is_stylus_eraser(self, gesture):
        """Check if the current stylus tool is the eraser.

        Args:
            gesture: The stylus gesture.

        Returns:
            True if the stylus eraser is being used, False otherwise.
        """
        try:
            device_tool = gesture.get_device_tool()
            if device_tool is None:
                return False

            # Get the tool type
            tool_type = device_tool.get_tool_type()

            # ERASER is the tool type for stylus eraser/rubber
            return tool_type == Gdk.DeviceToolType.ERASER
        except Exception:
            return False

    def _on_stylus_down(self, gesture, x, y):
        """Handle stylus press event.

        Args:
            gesture: Stylus gesture.
            x: X coordinate.
            y: Y coordinate.
        """
        if self._is_stylus_eraser(gesture):
            # Save current tool and switch to eraser
            self.previous_tool = self.current_tool
            self.current_tool = "eraser"
            self.using_stylus_eraser = True
            self.status_label.set_text("Tool: Eraser (Stylus)")

        # Start drawing
        self.drawing = True
        self.last_x = x
        self.last_y = y

    def _on_stylus_up(self, gesture, x, y):
        """Handle stylus release event.

        Args:
            gesture: Stylus gesture.
            x: X coordinate.
            y: Y coordinate.
        """
        self.drawing = False
        self.last_x = None
        self.last_y = None

        # Restore previous tool if we were using stylus eraser
        if self.using_stylus_eraser:
            self.current_tool = self.previous_tool
            self.using_stylus_eraser = False
            tool_name = "Pen" if self.current_tool == "pen" else "Eraser"
            self.status_label.set_text(f"Tool: {tool_name}")

    def _draw_current_tool(self, x: float, y: float):
        """Draw using current tool from last position to (x, y)."""
        if self.last_x is None or self.last_y is None:
            return
        if self.current_tool == "pen":
            color = (0.0, 0.0, 0.0, 1.0)
            size = self.pen_size
        else:
            color = (1.0, 1.0, 1.0, 1.0)
            size = self.eraser_size
        self.canvas.draw_line(self.last_x, self.last_y, x, y, color, size)

    def _on_stylus_motion(self, gesture, x, y):
        """Handle stylus motion event.

        Args:
            gesture: Stylus gesture.
            x: X coordinate.
            y: Y coordinate.
        """
        if not self.drawing:
            return

        self._draw_current_tool(x, y)
        self.last_x = x
        self.last_y = y
        self.drawing_area.queue_draw()

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for tools and actions."""
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.window.add_controller(key_controller)

        # Cache parsed accelerators (keyval, mods) for robust matching
        self._shortcuts = {}
        for name, accel in [
            ("pen", self.config.shortcut_tool_pen),
            ("eraser", self.config.shortcut_tool_eraser),
            ("clear", self.config.shortcut_clear_canvas),
            ("submit", self.config.shortcut_submit),
        ]:
            _ok, k, m = Gtk.accelerator_parse(accel)
            self._shortcuts[name] = (k, m)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard shortcut presses.

        Args:
            controller: Event controller.
            keyval: Key value.
            keycode: Key code.
            state: Modifier state (Ctrl, Alt, etc.).

        Returns:
            True if the key was handled, False otherwise.
        """
        pen_keyval, pen_mods = self._shortcuts.get("pen", (0, 0))
        eraser_keyval, eraser_mods = self._shortcuts.get("eraser", (0, 0))
        clear_keyval, clear_mods = self._shortcuts.get("clear", (0, 0))
        submit_keyval, submit_mods = self._shortcuts.get("submit", (0, 0))

        # Use mask check to ignore extra bits (NumLock, etc.)
        if keyval == pen_keyval and (state & pen_mods) == pen_mods:
            self._set_tool_pen()
            return True
        if keyval == eraser_keyval and (state & eraser_mods) == eraser_mods:
            self._set_tool_eraser()
            return True
        if keyval == clear_keyval and (state & clear_mods) == clear_mods:
            self._clear_canvas()
            return True
        if keyval == submit_keyval and (state & submit_mods) == submit_mods:
            self._submit_canvas()
            return True

        return False

    def _set_tool_pen(self):
        """Set current tool to pen."""
        # Reset stylus eraser state when manually switching tools
        self.using_stylus_eraser = False
        self.current_tool = "pen"
        self.previous_tool = "pen"
        self.status_label.set_text("Tool: Pen")

    def _set_tool_eraser(self):
        """Set current tool to eraser."""
        # Reset stylus eraser state when manually switching tools
        self.using_stylus_eraser = False
        self.current_tool = "eraser"
        self.previous_tool = "eraser"
        self.status_label.set_text("Tool: Eraser")

    def _clear_canvas(self):
        """Clear the canvas."""
        self.canvas.clear()
        self.drawing_area.queue_draw()

        if self.output_text:
            self.output_text.get_buffer().set_text("")

        self.status_label.set_text("Canvas cleared")
        self.drawing_area.queue_draw()

    def _submit_canvas(self):
        """Submit the canvas to the LLM."""
        max_tokens = self.config.max_tokens
        self._executor.submit(self._submit_canvas_thread, max_tokens)

    def _submit_canvas_thread(self, max_tokens: int):
        """Background thread target for LLM submission."""
        latex_output = self.llm_client.submit_to_llm(
            self.canvas.get_base64_image(), self.status_label, max_tokens
        )
        if latex_output and self.output_text:
            GLib.idle_add(lambda: self.output_text.get_buffer().set_text(latex_output))

    def _on_drawing_button_press(self, controller, n_presses, x, y):
        """Handle mouse press on drawing area.

        Args:
            controller: Event controller.
            n_presses: Number of button presses.
            x: X coordinate.
            y: Y coordinate.
        """
        self.drawing = True
        self.last_x = x
        self.last_y = y

    def _on_drawing_motion(self, controller, x, y):
        """Handle mouse motion on drawing area.

        Args:
            controller: Event controller.
            x: X coordinate.
            y: Y coordinate.
        """
        if not self.drawing:
            return

        self._draw_current_tool(x, y)
        self.last_x = x
        self.last_y = y
        self.drawing_area.queue_draw()

    def _on_drawing_button_release(self, controller, n_presses, x, y):
        """Handle mouse release on drawing area.

        Args:
            controller: Event controller.
            n_presses: Number of button presses.
            x: X coordinate.
            y: Y coordinate.
        """
        self.drawing = False
        self.last_x = None
        self.last_y = None

    def _on_draw(self, drawing_area, cr, width, height):
        """Draw function for the drawing area.

        Args:
            drawing_area: Drawing area widget.
            cr: Cairo context.
            width: Width of the area.
            height: Height of the area.
        """
        # Copy the surface to the widget
        cr.set_source_surface(self.canvas.surface, 0, 0)
        cr.paint()
