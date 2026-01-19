"""Control Panel UI - Main dashboard for system management."""

import sys
from typing import Optional
from pathlib import Path
from loguru import logger

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QTextEdit, QTabWidget,
        QGroupBox, QGridLayout, QSlider, QCheckBox, QLineEdit
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.error("PyQt6 not available - control panel cannot run")

from core.config import GameProfile, SystemConfig


if PYQT_AVAILABLE:
    class ControlPanel(QMainWindow):
        """Main control panel window."""

        def __init__(self, system_config: SystemConfig):
            """Initialize control panel."""
            super().__init__()
            self.system_config = system_config
            self.current_profile: Optional[GameProfile] = None
            self._setup_ui()

        def _setup_ui(self):
            """Setup UI components."""
            self.setWindowTitle("AI Vision Overlay - Control Panel")
            self.setGeometry(100, 100, 1200, 800)

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Main layout
            layout = QVBoxLayout(central_widget)

            # Header
            header = self._create_header()
            layout.addWidget(header)

            # Tabs
            tabs = QTabWidget()
            tabs.addTab(self._create_status_tab(), "📊 Status")
            tabs.addTab(self._create_profile_tab(), "🎮 Profiles")
            tabs.addTab(self._create_ai_tab(), "🤖 AI Vision")
            tabs.addTab(self._create_rules_tab(), "⚙️ Rules")
            tabs.addTab(self._create_hud_tab(), "🎯 HUD")
            tabs.addTab(self._create_diagnostics_tab(), "🔧 Diagnostics")

            layout.addWidget(tabs)

            # Footer
            footer = self._create_footer()
            layout.addWidget(footer)

        def _create_header(self) -> QWidget:
            """Create header section."""
            header = QWidget()
            layout = QHBoxLayout(header)

            # Title
            title = QLabel("AI Vision Overlay System")
            title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            layout.addWidget(title)

            layout.addStretch()

            # Status indicator
            self.status_label = QLabel("● STOPPED")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(self.status_label)

            return header

        def _create_status_tab(self) -> QWidget:
            """Create status overview tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # System Status
            status_group = QGroupBox("System Status")
            status_layout = QGridLayout()

            status_layout.addWidget(QLabel("Capture:"), 0, 0)
            self.capture_status = QLabel("Not Running")
            status_layout.addWidget(self.capture_status, 0, 1)

            status_layout.addWidget(QLabel("AI Vision:"), 1, 0)
            self.ai_status = QLabel("Not Running")
            status_layout.addWidget(self.ai_status, 1, 1)

            status_layout.addWidget(QLabel("Overlay:"), 2, 0)
            self.overlay_status = QLabel("Not Running")
            status_layout.addWidget(self.overlay_status, 2, 1)

            status_layout.addWidget(QLabel("FPS:"), 3, 0)
            self.fps_label = QLabel("0")
            status_layout.addWidget(self.fps_label, 3, 1)

            status_group.setLayout(status_layout)
            layout.addWidget(status_group)

            # Performance Metrics
            perf_group = QGroupBox("Performance Metrics")
            perf_layout = QGridLayout()

            perf_layout.addWidget(QLabel("Latency:"), 0, 0)
            self.latency_label = QLabel("0 ms")
            perf_layout.addWidget(self.latency_label, 0, 1)

            perf_layout.addWidget(QLabel("CPU Usage:"), 1, 0)
            self.cpu_label = QLabel("0%")
            perf_layout.addWidget(self.cpu_label, 1, 1)

            perf_layout.addWidget(QLabel("Memory:"), 2, 0)
            self.memory_label = QLabel("0 MB")
            perf_layout.addWidget(self.memory_label, 2, 1)

            perf_group.setLayout(perf_layout)
            layout.addWidget(perf_group)

            layout.addStretch()

            return tab

        def _create_profile_tab(self) -> QWidget:
            """Create profile management tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Profile selector
            profile_layout = QHBoxLayout()
            profile_layout.addWidget(QLabel("Active Profile:"))

            self.profile_combo = QComboBox()
            self.profile_combo.addItems(["None", "Dark Souls III", "Elden Ring", "Custom"])
            profile_layout.addWidget(self.profile_combo)

            load_btn = QPushButton("Load")
            profile_layout.addWidget(load_btn)

            new_btn = QPushButton("New")
            profile_layout.addWidget(new_btn)

            layout.addLayout(profile_layout)

            # Profile info
            info_group = QGroupBox("Profile Information")
            info_layout = QVBoxLayout()

            self.profile_info = QTextEdit()
            self.profile_info.setReadOnly(True)
            self.profile_info.setMaximumHeight(200)
            info_layout.addWidget(self.profile_info)

            info_group.setLayout(info_layout)
            layout.addWidget(info_group)

            layout.addStretch()

            return tab

        def _create_ai_tab(self) -> QWidget:
            """Create AI configuration tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Model settings
            model_group = QGroupBox("Model Settings")
            model_layout = QGridLayout()

            model_layout.addWidget(QLabel("Model:"), 0, 0)
            self.model_combo = QComboBox()
            self.model_combo.addItems(["yolov8n", "yolov8s", "yolov8m"])
            model_layout.addWidget(self.model_combo, 0, 1)

            model_layout.addWidget(QLabel("Confidence:"), 1, 0)
            self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
            self.confidence_slider.setRange(0, 100)
            self.confidence_slider.setValue(60)
            model_layout.addWidget(self.confidence_slider, 1, 1)

            model_layout.addWidget(QLabel("Device:"), 2, 0)
            self.device_combo = QComboBox()
            self.device_combo.addItems(["auto", "cpu", "cuda"])
            model_layout.addWidget(self.device_combo, 2, 1)

            model_group.setLayout(model_layout)
            layout.addWidget(model_group)

            # Detection preview
            preview_group = QGroupBox("Detection Preview")
            preview_layout = QVBoxLayout()

            self.detection_preview = QTextEdit()
            self.detection_preview.setReadOnly(True)
            self.detection_preview.setMaximumHeight(300)
            preview_layout.addWidget(self.detection_preview)

            preview_group.setLayout(preview_layout)
            layout.addWidget(preview_group)

            layout.addStretch()

            return tab

        def _create_rules_tab(self) -> QWidget:
            """Create rules editor tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Rules list
            rules_group = QGroupBox("Active Rules")
            rules_layout = QVBoxLayout()

            self.rules_list = QTextEdit()
            self.rules_list.setReadOnly(True)
            rules_layout.addWidget(self.rules_list)

            # Rule buttons
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(QPushButton("Add Rule"))
            btn_layout.addWidget(QPushButton("Edit Rule"))
            btn_layout.addWidget(QPushButton("Delete Rule"))
            rules_layout.addLayout(btn_layout)

            rules_group.setLayout(rules_layout)
            layout.addWidget(rules_group)

            return tab

        def _create_hud_tab(self) -> QWidget:
            """Create HUD configuration tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # HUD settings
            hud_group = QGroupBox("HUD Settings")
            hud_layout = QGridLayout()

            hud_layout.addWidget(QLabel("Theme:"), 0, 0)
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(["tactical_minimal", "modern", "retro"])
            hud_layout.addWidget(self.theme_combo, 0, 1)

            hud_layout.addWidget(QLabel("Opacity:"), 1, 0)
            self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
            self.opacity_slider.setRange(0, 100)
            self.opacity_slider.setValue(80)
            hud_layout.addWidget(self.opacity_slider, 1, 1)

            self.proximity_rings_check = QCheckBox("Show Proximity Rings")
            self.proximity_rings_check.setChecked(True)
            hud_layout.addWidget(self.proximity_rings_check, 2, 0, 1, 2)

            self.direction_arrows_check = QCheckBox("Show Direction Arrows")
            self.direction_arrows_check.setChecked(True)
            hud_layout.addWidget(self.direction_arrows_check, 3, 0, 1, 2)

            hud_group.setLayout(hud_layout)
            layout.addWidget(hud_group)

            layout.addStretch()

            return tab

        def _create_diagnostics_tab(self) -> QWidget:
            """Create diagnostics tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Logs
            logs_group = QGroupBox("System Logs")
            logs_layout = QVBoxLayout()

            self.log_viewer = QTextEdit()
            self.log_viewer.setReadOnly(True)
            self.log_viewer.setFont(QFont("Courier", 9))
            logs_layout.addWidget(self.log_viewer)

            # Log controls
            log_controls = QHBoxLayout()
            log_controls.addWidget(QPushButton("Clear Logs"))
            log_controls.addWidget(QPushButton("Export Logs"))

            self.log_level_combo = QComboBox()
            self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
            self.log_level_combo.setCurrentText("INFO")
            log_controls.addWidget(QLabel("Level:"))
            log_controls.addWidget(self.log_level_combo)

            logs_layout.addLayout(log_controls)

            logs_group.setLayout(logs_layout)
            layout.addWidget(logs_group)

            return tab

        def _create_footer(self) -> QWidget:
            """Create footer with main controls."""
            footer = QWidget()
            layout = QHBoxLayout(footer)

            # Start/Stop button
            self.start_stop_btn = QPushButton("▶ Start System")
            self.start_stop_btn.setStyleSheet("font-size: 14px; padding: 10px;")
            layout.addWidget(self.start_stop_btn)

            # Performance mode
            layout.addWidget(QLabel("Mode:"))
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["SAFE", "PERFORMANCE", "QUALITY", "DEBUG"])
            self.mode_combo.setCurrentText("PERFORMANCE")
            layout.addWidget(self.mode_combo)

            layout.addStretch()

            # Version
            version_label = QLabel("v0.1.0")
            version_label.setStyleSheet("color: gray;")
            layout.addWidget(version_label)

            return footer


def main():
    """Launch control panel."""
    if not PYQT_AVAILABLE:
        print("Error: PyQt6 is required for the control panel")
        print("Install with: pip install PyQt6")
        return 1

    system_config = SystemConfig()

    app = QApplication(sys.argv)
    panel = ControlPanel(system_config)
    panel.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
