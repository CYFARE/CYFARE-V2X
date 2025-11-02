#!/usr/bin/env python3

import sys
import os
import subprocess
import pathlib
import shutil
import re
from PySide6.QtCore import (
    Qt,
    QProcess,
    QSettings,
    QSize,
    QUrl,
    QCoreApplication,
)
from PySide6.QtGui import QIcon, QPixmap, QAction, QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QTabWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QStyle,
    QStatusBar,
)

APP_STYLESHEET = """
/* Global */
QWidget {
    background-color: #2B2B2B;
    color: #F0F0F0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Helvetica Neue', Arial, sans-serif;
    font-size: 10pt;
    border: none;
}

/* Main Window and Dialogs */
QMainWindow, QDialog {
    background-color: #2B2B2B;
}

/* ToolBar */
QToolBar {
    background-color: #3C3C3C;
    border-bottom: 1px solid #2B2B2B;
    padding: 5px;
}
QToolBar QToolButton {
    background-color: transparent;
    padding: 8px;
    border-radius: 5px;
    color: #F0F0F0;
}
QToolBar QToolButton:hover {
    background-color: #555;
}
QToolBar QToolButton:pressed {
    background-color: #3498DB;
}

/* Banner */
QWidget#banner {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #3C3C3C, stop:1 #323232);
    border-bottom: 1px solid #555;
}
QLabel#banner_title {
    font-size: 28pt;
    font-weight: bold;
    color: #3498DB;
    background-color: transparent;
}
QLabel#banner_subtitle {
    font-size: 12pt;
    color: #AAAAAA;
    background-color: transparent;
}

/* Tab Widget */
QTabWidget::pane {
    border-top: 1px solid #3498DB;
    padding: 10px;
    background-color: #2B2B2B;
}
QTabBar::tab {
    background: #3C3C3C;
    border: 1px solid #3C3C3C;
    border-bottom: 1px solid #555;
    padding: 10px 25px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    color: #AAA;
}
QTabBar::tab:selected {
    background: #2B2B2B;
    color: #FFFFFF;
    border: 1px solid #3498DB;
    border-bottom: 1px solid #2B2B2B;
}
QTabBar::tab:!selected:hover {
    background: #4A4A4A;
    color: #F0F0F0;
}

/* File List */
QListWidget {
    background-color: #3C3C3C;
    border: 1px solid #444;
    border-radius: 5px;
    padding: 5px;
    alternate-background-color: #3F3F3F;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 3px;
    color: #F0F0F0;
}
QListWidget::item:hover {
    background-color: #4A4A4A;
}
QListWidget::item:selected {
    background-color: #3498DB;
    color: #FFFFFF;
}
QListWidget:focus {
    border: 1px solid #3498DB;
}
QListWidget::dnd-indicator {
    border: 2px dashed #3498DB;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #444;
    border-radius: 5px;
    margin-top: 10px;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px 5px 5px;
    left: 10px;
    color: #3498DB;
    font-weight: bold;
    font-size: 11pt;
}

/* Standard Buttons (Secondary) */
QPushButton {
    background-color: transparent;
    border: 1px solid #888;
    padding: 8px 15px;
    border-radius: 5px;
    min-width: 80px;
    color: #F0F0F0;
}
QPushButton:hover {
    background-color: #555;
    border-color: #AAA;
}
QPushButton:pressed {
    background-color: #4A4A4A;
}
QPushButton:disabled {
    background-color: #444;
    color: #888;
    border-color: #555;
}

/* Specialized Buttons */
QPushButton#run_button {
    background-color: #2ECC71;
    color: #FFFFFF;
    font-weight: bold;
    border: none;
}
QPushButton#run_button:hover {
    background-color: #25a25a;
}
QPushButton#run_button:pressed {
    background-color: #1e8449;
}
QPushButton#run_button:disabled {
    background-color: #444;
    color: #888;
    border: none;
}

QPushButton#cancel_button {
    background-color: #E74C3C;
    color: #FFFFFF;
    font-weight: bold;
    border: none;
}
QPushButton#cancel_button:hover {
    background-color: #c0392b;
}
QPushButton#cancel_button:pressed {
    background-color: #a93226;
}
QPushButton#cancel_button:disabled {
    background-color: #444;
    color: #888;
    border: none;
}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #555;
    padding: 5px 8px;
    border-radius: 3px;
    color: #F0F0F0;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #3498DB;
}

QComboBox::drop-down {
    border: none;
    background-color: #3498DB;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    width: 20px;
}
QComboBox::down-arrow {
    /* Let Qt handle the default arrow */
}
QComboBox QAbstractItemView { /* Dropdown list */
    background-color: #3C3C3C;
    border: 1px solid #555;
    selection-background-color: #3498DB;
    color: #F0F0F0;
}

/* CheckBox */
QCheckBox {
    spacing: 5px;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    background-color: #3C3C3C;
    border: 1px solid #555;
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background-color: #3498DB;
    /* image: url(check.png); */ /* Requires resource */
}

/* ProgressBar */
QProgressBar {
    border: 1px solid #555;
    border-radius: 5px;
    text-align: center;
    color: #F0F0F0;
    background-color: #3C3C3C;
    height: 25px;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #3498DB;
    border-radius: 5px;
}

/* Log View */
QTextEdit#log_view {
    background-color: #222;
    color: #E0E0E0;
    font-family: 'Consolas', 'Monaco', 'Monospace';
    font-size: 9pt;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 5px;
}

/* StatusBar */
QStatusBar {
    background-color: #3C3C3C;
    color: #F0F0F0;
    border-top: 1px solid #555;
}
QStatusBar::item {
    border: none;
}
"""


class SettingsDialog(QDialog):
    """The modal settings dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)

        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)

        self.create_general_page()
        self.create_ffmpeg_page()
        self.create_models_page()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        self.load_settings()

    def load_settings(self):
        self.row_v2x_path.setText(self.settings.value("v2x-path", ""))
        self.row_ffmpeg_path.setText(self.settings.value("ffmpeg-path", ""))
        self.row_output_folder.setText(self.settings.value("output-folder", ""))
        self.row_auto_path.setChecked(
            self.settings.value("auto-output-path", False, type=bool)
        )

        self.row_encoder.setText(self.settings.value("ffmpeg-encoder", "h264_nvenc"))
        self.row_encoder_opts.setText(
            self.settings.value("ffmpeg-opts", "preset=llhq,rc-lookahead=0")
        )

        self.row_realcugan_model.setText(
            self.settings.value("realcugan-model", "models-se")
        )
        self.row_rife_model.setText(self.settings.value("rife-model-name", "rife-v4.6"))

    def save_and_accept(self):
        self.settings.setValue("v2x-path", self.row_v2x_path.text())
        self.settings.setValue("ffmpeg-path", self.row_ffmpeg_path.text())
        self.settings.setValue("output-folder", self.row_output_folder.text())
        self.settings.setValue("auto-output-path", self.row_auto_path.isChecked())

        self.settings.setValue("ffmpeg-encoder", self.row_encoder.text())
        self.settings.setValue("ffmpeg-opts", self.row_encoder_opts.text())

        self.settings.setValue("realcugan-model", self.row_realcugan_model.text())
        self.settings.setValue("rife-model-name", self.row_rife_model.text())

        self.accept()

    def create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tab_widget.addTab(page, "General")

        group_paths = QGroupBox("Executable Paths")
        layout_paths = QFormLayout(group_paths)
        layout.addWidget(group_paths)

        self.row_v2x_path = QLineEdit()
        self.add_browse_button(
            layout_paths,
            "Video2X Executable",
            self.row_v2x_path,
            "Select Video2X AppImage",
        )

        self.row_ffmpeg_path = QLineEdit()
        self.add_browse_button(
            layout_paths,
            "FFmpeg Folder",
            self.row_ffmpeg_path,
            "Select FFmpeg Folder",
            is_folder=True,
        )

        group_output = QGroupBox("Output")
        layout_output = QFormLayout(group_output)
        layout.addWidget(group_output)

        self.row_output_folder = QLineEdit()
        self.add_browse_button(
            layout_output,
            "Default Output Folder",
            self.row_output_folder,
            "Select Output Folder",
            is_folder=True,
        )

        self.row_auto_path = QCheckBox("Save output in default folder")
        self.row_auto_path.setToolTip("If off, output is saved next to the input file")
        layout_output.addRow(self.row_auto_path)
        layout.addStretch()

    def create_ffmpeg_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tab_widget.addTab(page, "FFmpeg")

        group = QGroupBox("Encoder Settings")
        layout_group = QFormLayout(group)
        layout.addWidget(group)

        self.row_encoder = QLineEdit()
        layout_group.addRow("Encoder:", self.row_encoder)

        self.row_encoder_opts = QLineEdit()
        layout_group.addRow("Encoder Options:", self.row_encoder_opts)
        layout.addStretch()

    def create_models_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tab_widget.addTab(page, "Models")

        group_upscale = QGroupBox("Upscaler Models")
        layout_upscale = QFormLayout(group_upscale)
        layout.addWidget(group_upscale)

        self.row_realcugan_model = QLineEdit()
        layout_upscale.addRow("Real-CUGAN Model Name:", self.row_realcugan_model)

        group_stabilize = QGroupBox("Stabilizer Models")
        layout_stabilize = QFormLayout(group_stabilize)
        layout.addWidget(group_stabilize)

        self.row_rife_model = QLineEdit()
        layout_stabilize.addRow("RIFE Model Name:", self.row_rife_model)
        layout.addStretch()

    def add_browse_button(self, layout, label, line_edit, title, is_folder=False):
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(line_edit)

        button = QPushButton()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        button.setIcon(icon)
        button.setFixedSize(32, 32)
        button.clicked.connect(
            lambda: self.on_browse_clicked(line_edit, title, is_folder)
        )
        hbox.addWidget(button)
        layout.addRow(label, widget)

    def on_browse_clicked(self, line_edit, title, is_folder):
        path = ""
        if is_folder:
            path = QFileDialog.getExistingDirectory(self, title, line_edit.text())
        else:
            path, _ = QFileDialog.getOpenFileName(self, title, line_edit.text())

        if path:
            line_edit.setText(path)


class MainWindow(QMainWindow):
    """The main application window."""

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(800, 700)
        self.setWindowTitle("Video Enhancer")
        self.settings = settings

        self.process = QProcess(self)
        self.file_queue = []
        self.current_file = None
        self.progress_regex = re.compile(r"\((\d+\.?\d*)\s*%\)")

        self.setAcceptDrops(True)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vbox = QVBoxLayout(central_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        self.settings_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            "Settings",
            self,
        )
        self.settings_action.triggered.connect(self.on_settings_clicked)
        toolbar.addAction(self.settings_action)

        banner_widget = QWidget()
        banner_widget.setObjectName("banner")
        banner_widget.setMinimumHeight(180)
        banner_layout = QVBoxLayout(banner_widget)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("CYFARE 2X")
        title_label.setObjectName("banner_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("AI Video Upscaler & Stabilizer")
        subtitle_label.setObjectName("banner_subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        banner_layout.addWidget(title_label)
        banner_layout.addSpacing(5)
        banner_layout.addWidget(subtitle_label)
        main_vbox.addWidget(banner_widget)

        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)
        main_vbox.addWidget(container_widget, 1)

        self.view_stack = QTabWidget()
        container_layout.addWidget(self.view_stack, 1)

        self.upscale_page = self.create_upscale_page()
        self.stabilize_page = self.create_stabilize_page()

        self.view_stack.addTab(self.upscale_page, "Upscale")
        self.view_stack.addTab(self.stabilize_page, "Stabilize")

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        container_layout.addWidget(self.progress_bar)

        controls_box = QWidget()
        controls_layout = QHBoxLayout(controls_box)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(controls_box)

        self.run_button = QPushButton("Start Processing")
        self.run_button.setObjectName("run_button")
        self.run_button.clicked.connect(self.on_run_clicked)
        controls_layout.addWidget(self.run_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        controls_layout.addWidget(self.cancel_button)

        self.terminal_toggle = QCheckBox("Show Log")
        self.terminal_toggle.toggled.connect(self.on_toggle_terminal)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.terminal_toggle)

        self.textview_output = QTextEdit()
        self.textview_output.setObjectName("log_view")
        self.textview_output.setReadOnly(True)
        self.textview_output.setVisible(False)
        self.textview_output.setMinimumHeight(200)
        container_layout.addWidget(self.textview_output)

        self.process.readyReadStandardOutput.connect(self.on_stdout_read)
        self.process.readyReadStandardError.connect(self.on_stderr_read)
        self.process.finished.connect(self.process_finished)

    def set_default_size(self, width, height):
        self.resize(width, height)

    def create_batch_list_box(self, add_callback, clear_callback):
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        buttons_box = QWidget()
        buttons_layout = QHBoxLayout(buttons_box)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addStretch()
        layout.addWidget(buttons_box)

        btn_add = QPushButton("Add Video(s)...")
        btn_add.clicked.connect(add_callback)
        buttons_layout.addWidget(btn_add)

        btn_clear = QPushButton("Clear List")
        buttons_layout.addWidget(btn_clear)

        list_box = QListWidget()
        list_box.setMinimumHeight(150)
        list_box.setAlternatingRowColors(True)
        list_box.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        list_box.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        btn_clear.clicked.connect(list_box.clear)
        layout.addWidget(list_box)

        return box, list_box

    def create_upscale_page(self):
        page_box = QWidget()
        layout = QVBoxLayout(page_box)
        layout.setContentsMargins(0, 5, 0, 0)

        list_area, self.upscale_file_list = self.create_batch_list_box(
            self.on_add_files, None
        )
        layout.addWidget(list_area)

        group = QGroupBox("Upscale Options")
        layout_group = QFormLayout(group)
        layout_group.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.addWidget(group)

        self.upscale_model_combo = QComboBox()
        self.upscale_model_combo.addItems(["realcugan"])
        layout_group.addRow("AI Model:", self.upscale_model_combo)

        self.upscale_scale_spin = QDoubleSpinBox()
        self.upscale_scale_spin.setRange(1.0, 4.0)
        self.upscale_scale_spin.setSingleStep(1.0)
        self.upscale_scale_spin.setValue(2.0)
        self.upscale_scale_spin.setDecimals(0)
        layout_group.addRow("Upscale Ratio:", self.upscale_scale_spin)

        self.upscale_backend_combo = QComboBox()
        self.upscale_backend_combo.addItems(["gpu"])
        layout_group.addRow("AI Backend:", self.upscale_backend_combo)

        layout.addStretch()
        return page_box

    def create_stabilize_page(self):
        page_box = QWidget()
        layout = QVBoxLayout(page_box)
        layout.setContentsMargins(0, 5, 0, 0)

        list_area, self.stabilize_file_list = self.create_batch_list_box(
            self.on_add_files, None
        )
        layout.addWidget(list_area)

        group = QGroupBox("Stabilize Options (RIFE)")
        layout_group = QFormLayout(group)
        layout_group.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.addWidget(group)

        self.rife_factor_spin = QSpinBox()
        self.rife_factor_spin.setRange(2, 8)
        self.rife_factor_spin.setSingleStep(1)
        self.rife_factor_spin.setValue(2)
        layout_group.addRow("Interpolation Factor:", self.rife_factor_spin)

        layout.addStretch()
        return page_box

    def add_file_to_list(self, path_str):
        current_index = self.view_stack.currentIndex()
        list_box = None

        if current_index == 0:
            list_box = self.upscale_file_list
        elif current_index == 1:
            list_box = self.stabilize_file_list

        if list_box:
            item = QListWidgetItem(pathlib.Path(path_str).name)
            item.setData(Qt.ItemDataRole.UserRole, path_str)
            item.setToolTip(path_str)
            list_box.addItem(item)

    def on_add_files(self, button):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.mkv *.mov *.avi *.webm)",
        )
        if files:
            for file_path in files:
                self.add_file_to_list(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            mime_data = event.mimeData()
            # A simple check for video-like mimetypes or file extensions
            for url in mime_data.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    ext = pathlib.Path(path).suffix.lower()
                    if ext in [".mp4", ".mkv", ".mov", ".avi", ".webm"]:
                        event.acceptProposedAction()
                        return
            event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile()
                ext = pathlib.Path(path).suffix.lower()
                if ext in [".mp4", ".mkv", ".mov", ".avi", ".webm"]:
                    self.add_file_to_list(url.toLocalFile())
        event.acceptProposedAction()

    def on_settings_clicked(self, button):
        dialog = SettingsDialog(self.settings, self)
        dialog.exec()

    def on_toggle_terminal(self, checked):
        self.textview_output.setVisible(checked)

    def add_output_text(self, text):
        """Appends text to the QTextEdit."""
        self.textview_output.moveCursor(
            self.textview_output.textCursor().MoveOperation.End
        )
        self.textview_output.insertPlainText(text)
        self.textview_output.moveCursor(
            self.textview_output.textCursor().MoveOperation.End
        )

        if self.current_file:
            matches = self.progress_regex.findall(text)
            if matches:
                percent_str = matches[-1]
                try:
                    percent_float = float(percent_str)
                    self.progress_bar.setValue(int(percent_float))
                    file_name = pathlib.Path(self.current_file).name
                    self.progress_bar.setFormat(f"{file_name} [{percent_str}%]")
                except Exception as e:
                    print(f"Progress parse error: {e}")

    def send_toast(self, text):
        self.statusBar.showMessage(text, 5000)

    def set_processing_state(self, is_processing):
        self.run_button.setEnabled(not is_processing)
        self.cancel_button.setEnabled(is_processing)
        self.view_stack.setEnabled(not is_processing)
        self.settings_action.setEnabled(not is_processing)

    def on_cancel_clicked(self, widget):
        if self.process.state() == QProcess.ProcessState.Running:
            self.add_output_text("\n--- Cancelling process ---\n")
            self.process.terminate()
            self.file_queue.clear()
            self.current_file = None

    def process_finished(self, exit_code, exit_status):
        if self.current_file:
            self.add_output_text(f"\n--- Finished: {self.current_file} ---\n")
            self.current_file = None
        else:
            self.add_output_text("\n--- Process Finished ---\n")

        self.run_next_file()

    def on_stdout_read(self):
        data = self.process.readAllStandardOutput()
        try:
            text = bytes(data).decode("utf-8", errors="ignore")
            self.add_output_text(text)
        except Exception as e:
            print(f"STDOUT read error: {e}")

    def on_stderr_read(self):
        data = self.process.readAllStandardError()
        try:
            text = bytes(data).decode("utf-8", errors="ignore")
            self.add_output_text(text)
        except Exception as e:
            print(f"STDERR read error: {e}")

    def _find_ffmpeg_path(self):
        setting_path = self.settings.value("ffmpeg-path", "")
        if setting_path and (pathlib.Path(setting_path) / "ffmpeg").is_file():
            self.add_output_text(f"Using ffmpeg from settings: {setting_path}\n")
            return setting_path

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
            f"Warning: 'ffmpeg' not found in settings, {user_ffmpeg_dir}, or system PATH.\n"
        )
        return ""

    def generate_output_path(self, input_path_str):
        p = pathlib.Path(input_path_str)

        if self.settings.value("auto-output-path", False, type=bool):
            base_dir_str = self.settings.value("output-folder", "")
            if not base_dir_str:
                self.send_toast("Error: Default output folder not set in settings.")
                return None
            base_dir = pathlib.Path(base_dir_str)
        else:
            base_dir = p.parent

        base_dir.mkdir(parents=True, exist_ok=True)

        current_index = self.view_stack.currentIndex()
        suffix = "_upscaled"
        if current_index == 1:
            suffix = "_stabilized"

        return str(base_dir / f"{p.stem}{suffix}{p.suffix}")

    def on_run_clicked(self, widget):
        self.textview_output.clear()
        self.file_queue.clear()

        current_index = self.view_stack.currentIndex()
        list_box = None
        if current_index == 0:
            list_box = self.upscale_file_list
        elif current_index == 1:
            list_box = self.stabilize_file_list

        if not list_box:
            self.send_toast("Error: Could not find active file list.")
            return

        if list_box.count() == 0:
            self.send_toast("No files in batch list to process.")
            return

        for i in range(list_box.count()):
            item = list_box.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.file_queue.append(file_path)

        if not self.file_queue:
            self.send_toast("No files in batch list to process.")
            return

        self.set_processing_state(True)
        self.run_next_file()

    def run_next_file(self):
        if not self.file_queue:
            self.add_output_text("\n--- All jobs finished ---\n")
            self.set_processing_state(False)
            self.progress_bar.setFormat("Finished")
            self.progress_bar.setValue(100)
            self.current_file = None
            return

        input_file = self.file_queue.pop(0)
        self.current_file = input_file

        self.add_output_text(f"\n--- Processing: {input_file} ---\n")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"Starting {pathlib.Path(input_file).name}...")

        output_file = self.generate_output_path(input_file)
        if not output_file:
            self.add_output_text("Error: Could not generate output path. Skipping.\n")
            self.run_next_file()
            return

        v2x_path = self.settings.value("v2x-path", "")
        if not v2x_path or not pathlib.Path(v2x_path).is_file():
            self.add_output_text(
                f"Error: Video2X executable not found at '{v2x_path}'. Check Settings.\n"
            )
            self.set_processing_state(False)
            return

        command_args = ["-i", input_file, "-o", output_file]
        current_index = self.view_stack.currentIndex()

        try:
            if current_index == 0:
                model = self.upscale_model_combo.currentText()
                realcugan_model = self.settings.value("realcugan-model", "")
                scale = int(self.upscale_scale_spin.value())
                backend = self.upscale_backend_combo.currentText()

                command_args.extend(["-p", model])
                if model == "realcugan":
                    command_args.extend(["--realcugan-model", realcugan_model])
                command_args.extend(["-s", str(scale)])
                if backend == "gpu":
                    command_args.extend(["-d", "0"])

            elif current_index == 1:
                rife_model_name = self.settings.value("rife-model-name", "rife-v4.6")
                rife_factor = int(self.rife_factor_spin.value())

                if not rife_model_name:
                    raise ValueError("RIFE model name not set in settings.")

                command_args.extend(
                    [
                        "-p",
                        "rife",
                        "--rife-model",
                        rife_model_name,
                        "-m",
                        str(rife_factor),
                        "-d",
                        "0",
                    ]
                )

            encoder = self.settings.value("ffmpeg-encoder", "")
            if encoder:
                command_args.extend(["-c", encoder])

            encoder_opts = self.settings.value("ffmpeg-opts", "")
            if encoder_opts:
                for opt in encoder_opts.split(","):
                    command_args.extend(["-e", opt.strip()])

        except Exception as e:
            self.add_output_text(f"Error building command: {e}\n")
            self.set_processing_state(False)
            return

        env = QProcess.systemEnvironment()
        env_map = {
            item.split("=", 1)[0]: item.split("=", 1)[1] for item in env if "=" in item
        }

        env_map["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
        env_map["__NV_PRIME_RENDER_OFFLOAD"] = "1"
        env_map["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"

        ffmpeg_path = self._find_ffmpeg_path()
        if ffmpeg_path:
            env_map["PATH"] = f"{ffmpeg_path}:{env_map.get('PATH', '')}"

        process_env = self.process.processEnvironment()
        for key, value in env_map.items():
            process_env.insert(key, value)
        self.process.setProcessEnvironment(process_env)

        self.add_output_text(f"Command: {v2x_path} {' '.join(command_args)}\n")

        try:
            self.process.start(v2x_path, command_args)

        except Exception as e:
            self.add_output_text(f"Failed to start process: {e}\n")
            self.set_processing_state(False)


if __name__ == "__main__":
    QCoreApplication.setOrganizationName("Cyfare")
    QCoreApplication.setApplicationName("VideoEnhancer")

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    settings = QSettings()

    try:
        current_v2x_path = settings.value("v2x-path", "")

        if getattr(sys, "frozen", False):
            script_dir = pathlib.Path(sys.executable).parent
        else:
            script_dir = pathlib.Path(__file__).parent.resolve()

        detected_appimage_path = script_dir / "Video2X-x86_64.AppImage"

        if (
            not current_v2x_path or not pathlib.Path(current_v2x_path).is_file()
        ) and detected_appimage_path.is_file():
            print(f"Detected Video2X AppImage at: {detected_appimage_path}")
            settings.setValue("v2x-path", str(detected_appimage_path))
    except Exception as e:
        print(f"Warning: Could not auto-detect AppImage: {e}")

    win = MainWindow(settings=settings)
    win.show()
    sys.exit(app.exec())
