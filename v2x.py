#!/usr/bin/env python3

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GLib, Pango, Adw, Gio, Gdk
import subprocess
import os
import shutil
import pathlib


class Video2XApp(Adw.Application):
    """The main GTK Application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        """Called when the application is activated."""
        win = MainWindow(application=app)
        win.present()


class MainWindow(Gtk.ApplicationWindow):
    """The main application window."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(700, 600)

        self.process = None
        self.stdout_watch_id = 0
        self.stderr_watch_id = 0

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            #log_view {
                font-family: Monospace;
                font-size: 10pt;
            }
            """
        )

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_title_widget(Adw.WindowTitle(title="CYFARE V2X WRAPPER"))
        self.set_titlebar(self.header_bar)

        # Minimize Button
        btn_minimize = Gtk.Button.new_from_icon_name("window-minimize-symbolic")
        btn_minimize.connect("clicked", lambda w: self.minimize())
        self.header_bar.pack_start(btn_minimize)

        # Run Button
        self.run_button = Gtk.Button.new_with_label("Run")
        self.run_button.add_css_class("suggested-action")
        self.run_button.connect("clicked", self.on_run)
        self.header_bar.pack_end(self.run_button)

        # Cancel Button
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.add_css_class("destructive-action")
        self.cancel_button.connect("clicked", self.on_cancel)
        self.cancel_button.set_sensitive(False)
        self.header_bar.pack_end(self.cancel_button)

        # Main Layout Box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_vbox.set_margin_top(10)
        main_vbox.set_margin_bottom(10)
        main_vbox.set_margin_start(10)
        main_vbox.set_margin_end(10)
        self.set_child(main_vbox)

        # Preferences Group for Files
        prefs_group = Adw.PreferencesGroup()
        prefs_group.set_title("File Selection")
        main_vbox.append(prefs_group)

        # Input File Row
        self.entry_input = Gtk.Entry(
            hexpand=True, placeholder_text="Path to input video"
        )
        btn_input = Gtk.Button.new_with_label("Browse...")
        btn_input.connect("clicked", self.on_browse_input)

        input_row = Adw.ActionRow.new()
        input_row.set_title("Input File")
        input_row.add_suffix(self.entry_input)
        input_row.add_suffix(btn_input)
        prefs_group.add(input_row)

        # Output File Row
        self.entry_output = Gtk.Entry(
            hexpand=True, placeholder_text="Path to output video"
        )
        btn_output = Gtk.Button.new_with_label("Save As...")
        btn_output.connect("clicked", self.on_browse_output)

        output_row = Adw.ActionRow.new()
        output_row.set_title("Output File")
        output_row.add_suffix(self.entry_output)
        output_row.add_suffix(btn_output)
        prefs_group.add(output_row)

        # Output Log
        log_label = Gtk.Label(label="Process Log")
        log_label.set_halign(Gtk.Align.START)
        log_label.set_margin_top(10)
        log_label.add_css_class("title-4")
        main_vbox.append(log_label)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        main_vbox.append(self.scrolled_window)

        self.textview_output = Gtk.TextView.new()
        self.textview_output.set_editable(False)
        self.textview_output.set_cursor_visible(False)
        self.textview_output.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview_output.set_name("log_view")

        self.textbuffer_output = self.textview_output.get_buffer()
        self.scrolled_window.set_child(self.textview_output)

    def on_browse_input(self, widget):
        """Show native file chooser for input file."""
        dialog = Gtk.FileChooserNative.new(
            title="Please choose an input file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.set_modal(True)
        dialog.connect("response", self.on_input_dialog_response)
        dialog.show()

    def on_input_dialog_response(self, dialog, response):
        """Handle input file chooser response."""
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                self.entry_input.set_text(file.get_path())
        dialog.destroy()

    def on_browse_output(self, widget):
        """Show native file chooser for output file."""
        dialog = Gtk.FileChooserNative.new(
            title="Please choose an output file",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.set_modal(True)
        dialog.set_current_name("output.mkv")
        dialog.connect("response", self.on_output_dialog_response)
        dialog.show()

    def on_output_dialog_response(self, dialog, response):
        """Handle output file chooser response."""
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                self.entry_output.set_text(file.get_path())
        dialog.destroy()

    def add_output_text(self, text):
        """Appends text to the Gtk.TextView from the main GUI thread."""
        end_iter = self.textbuffer_output.get_end_iter()
        self.textbuffer_output.insert(end_iter, text)
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    def on_cancel(self, widget):
        """Terminates the running subprocess."""
        if self.process and self.process.poll() is None:
            GLib.idle_add(self.add_output_text, "\n--- Cancelling process ---\n")
            self.process.terminate()

    def process_finished(self, pid, condition):
        """Callback when the subprocess finishes."""
        if self.stdout_watch_id > 0:
            GLib.source_remove(self.stdout_watch_id)
            self.stdout_watch_id = 0
        if self.stderr_watch_id > 0:
            GLib.source_remove(self.stderr_watch_id)
            self.stderr_watch_id = 0

        self.run_button.set_sensitive(True)
        self.run_button.set_label("Run")
        self.cancel_button.set_sensitive(False)
        self.process = None

        GLib.idle_add(self.add_output_text, "\n--- Process Finished ---\n")

    def on_stdout_read(self, fd, condition):
        """Callback to read from stdout pipe."""
        if condition & GLib.IO_HUP:
            return False

        try:
            data = os.read(fd, 4096)
            if data:
                text = data.decode("utf-8", errors="ignore")
                GLib.idle_add(self.add_output_text, text)
        except Exception as e:
            print(f"STDOUT read error: {e}")

        return True

    def on_stderr_read(self, fd, condition):
        """Callback to read from stderr pipe."""
        if condition & GLib.IO_HUP:
            return False

        try:
            data = os.read(fd, 4096)
            if data:
                text = data.decode("utf-8", errors="ignore")
                GLib.idle_add(self.add_output_text, f"[STDERR] {text}")
        except Exception as e:
            print(f"STDERR read error: {e}")

        return True

    def _find_ffmpeg_path(self):
        """
        Finds the ffmpeg directory.
        Priority 1: /home/USERNAME/ffmpeg
        Priority 2: System PATH (via `which ffmpeg`)
        """
        user_ffmpeg_dir = pathlib.Path.home() / "ffmpeg"
        if (user_ffmpeg_dir / "ffmpeg").is_file():
            self.add_output_text(f"Using ffmpeg from: {user_ffmpeg_dir}\n")
            return str(user_ffmpeg_dir)

        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            ffmpeg_dir = str(pathlib.Path(system_ffmpeg).parent)
            self.add_output_text(f"Using system ffmpeg from: {ffmpeg_dir}\n")
            return ffmpeg_dir

        self.add_output_text(
            f"Warning: 'ffmpeg' not found in {user_ffmpeg_dir} or system PATH.\n"
            f"Attempting to use {user_ffmpeg_dir} anyway as fallback.\n"
        )
        return str(user_ffmpeg_dir)

    def on_run(self, widget):
        """Starts the Video2X subprocess."""
        input_file = self.entry_input.get_text()
        output_file = self.entry_output.get_text()

        if not input_file or not output_file:
            self.add_output_text("Error: Please select both input and output files.\n")
            return

        self.textbuffer_output.set_text("")
        self.add_output_text("Starting process...\n")
        self.run_button.set_sensitive(False)
        self.run_button.set_label("Running...")
        self.cancel_button.set_sensitive(True)

        # Set up the command and environment
        env = os.environ.copy()
        env["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
        env["__NV_PRIME_RENDER_OFFLOAD"] = "1"
        env["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"

        # DYNAMIC FFMPEG PATH
        ffmpeg_path = self._find_ffmpeg_path()
        env["PATH"] = f"{ffmpeg_path}:{env.get('PATH', '')}"
        self.add_output_text(f"Updated PATH: {env['PATH']}\n")

        command = [
            "./Video2X-x86_64.AppImage",
            "-i",
            input_file,
            "-o",
            output_file,
            "-p",
            "realcugan",
            "--realcugan-model",
            "models-se",
            "-s",
            "4",
            "-c",
            "h264_nvenc",
            "-e",
            "preset=llhq",
            "-e",
            "rc-lookahead=0",
            "-e",
            "no-scenecut=1",
            "-e",
            "zerolatency=1",
            "-e",
            "delay=0",
            "-e",
            "aud=1",
        ]

        try:
            self.process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # --- Set pipes to non-blocking ---
            os.set_blocking(self.process.stdout.fileno(), False)
            os.set_blocking(self.process.stderr.fileno(), False)

            # --- Watch file descriptors for reading ---
            self.stdout_watch_id = GLib.io_add_watch(
                self.process.stdout.fileno(),
                GLib.IO_IN | GLib.IO_HUP,
                self.on_stdout_read,
            )
            self.stderr_watch_id = GLib.io_add_watch(
                self.process.stderr.fileno(),
                GLib.IO_IN | GLib.IO_HUP,
                self.on_stderr_read,
            )

            GLib.child_watch_add(self.process.pid, self.process_finished)

        except Exception as e:
            self.add_output_text(f"Failed to start process: {e}\n")
            self.run_button.set_sensitive(True)
            self.run_button.set_label("Run")
            self.cancel_button.set_sensitive(False)


if __name__ == "__main__":
    app = Video2XApp(application_id="com.example.video2xwrapper")
    sys.exit(app.run(sys.argv))
