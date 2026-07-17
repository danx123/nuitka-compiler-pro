# nuitka_batch.py
import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QComboBox, QFileDialog, QProgressBar, QMessageBox,
    QAbstractItemView, QCheckBox, QFrame, QSizePolicy, QWidget,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QPalette


ENTERPRISE_STYLE = """
QDialog {
    background-color: #0F1117;
    color: #E2E8F0;
}
QLabel {
    color: #CBD5E1;
    font-family: 'Segoe UI', sans-serif;
}
QLabel[class="title"] {
    color: #F8FAFC;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
QLabel[class="section-header"] {
    color: #94A3B8;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
QListWidget {
    background-color: #1E2433;
    border: 1px solid #2D3748;
    border-radius: 6px;
    color: #CBD5E1;
    font-family: 'Consolas', monospace;
    font-size: 11px;
    padding: 4px;
    selection-background-color: #2563EB;
}
QListWidget::item {
    padding: 5px 8px;
    border-radius: 3px;
    border-bottom: 1px solid #252D3D;
}
QListWidget::item:hover {
    background-color: #252F45;
}
QListWidget::item:selected {
    background-color: #1D4ED8;
    color: #FFFFFF;
}
QComboBox {
    background-color: #1E2433;
    border: 1px solid #2D3748;
    border-radius: 6px;
    color: #CBD5E1;
    padding: 8px 12px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
    min-height: 36px;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748B;
}
QComboBox QAbstractItemView {
    background-color: #1E2433;
    border: 1px solid #3B4563;
    color: #CBD5E1;
    selection-background-color: #2563EB;
}
QCheckBox {
    color: #CBD5E1;
    spacing: 10px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3B4563;
    border-radius: 4px;
    background: #1E2433;
}
QCheckBox::indicator:checked {
    background: #2563EB;
    border-color: #2563EB;
}
QCheckBox::indicator:hover {
    border-color: #60A5FA;
}
QPushButton {
    background-color: #252F45;
    border: 1px solid #3B4563;
    border-radius: 6px;
    color: #CBD5E1;
    padding: 8px 16px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
    font-weight: 600;
    min-height: 34px;
}
QPushButton:hover {
    background-color: #2D3A55;
    border-color: #4A6FA5;
    color: #F1F5F9;
}
QPushButton:pressed {
    background-color: #1E2433;
}
QPushButton[class="primary"] {
    background-color: #1D4ED8;
    border: 1px solid #2563EB;
    color: #FFFFFF;
}
QPushButton[class="primary"]:hover {
    background-color: #2563EB;
    border-color: #3B82F6;
}
QPushButton[class="danger"] {
    background-color: #991B1B;
    border: 1px solid #DC2626;
    color: #FCA5A5;
}
QPushButton[class="danger"]:hover {
    background-color: #B91C1C;
}
QProgressBar {
    border: 1px solid #2D3748;
    border-radius: 4px;
    background-color: #1A2035;
    text-align: center;
    color: #94A3B8;
    font-size: 11px;
    font-weight: 600;
    height: 8px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1D4ED8, stop:1 #3B82F6);
    border-radius: 3px;
}
QFrame[class="separator"] {
    background-color: #1E2D3D;
    max-height: 1px;
}
"""


class CooldownDialog(QDialog):
    """Countdown dialog professional untuk hardware cooldown."""
    def __init__(self, seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Cooldown — Nuitka Compiler Pro")
        self.setFixedSize(520, 260)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setStyleSheet(ENTERPRISE_STYLE)

        self.total_seconds = seconds
        self.remaining = seconds

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 28)
        layout.setSpacing(0)

        # --- Header ---
        header_layout = QHBoxLayout()

        indicator = QLabel("●")
        indicator.setStyleSheet("color: #F59E0B; font-size: 14px;")
        header_layout.addWidget(indicator)

        header_layout.addSpacing(8)

        title = QLabel("THERMAL MANAGEMENT ACTIVE")
        title.setStyleSheet("font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #F59E0B; font-family: 'Segoe UI', sans-serif;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(16)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1E3A5F; max-height:1px;")
        layout.addWidget(sep)

        layout.addSpacing(20)

        # --- Body ---
        info_label = QLabel(
            "Pausing between compilation tasks to allow CPU and memory to recover.\n"
            "This protects hardware integrity and prevents thermal throttling."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #64748B; font-size: 12px; line-height: 1.6; font-family: 'Segoe UI', sans-serif;")
        layout.addWidget(info_label)

        layout.addSpacing(20)

        # --- Timer ---
        self.timer_label = QLabel(self._format_time(seconds))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(
            "font-size: 42px; font-weight: 700; color: #3B82F6; "
            "font-family: 'Consolas', monospace; letter-spacing: 4px;"
        )
        layout.addWidget(self.timer_label)

        layout.addSpacing(14)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setRange(0, seconds)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        layout.addWidget(self.progress)

        layout.addSpacing(10)

        self.sub_label = QLabel("Resuming compilation shortly...")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setStyleSheet("color: #334155; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        layout.addWidget(self.sub_label)

        # --- Timer Logic ---
        self.qt_timer = QTimer(self)
        self.qt_timer.timeout.connect(self._update_timer)
        self.qt_timer.start(1000)

    def _format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def _update_timer(self):
        self.remaining -= 1
        self.progress.setValue(self.total_seconds - self.remaining)
        self.timer_label.setText(self._format_time(self.remaining))

        if self.remaining <= 10:
            self.timer_label.setStyleSheet(
                "font-size: 42px; font-weight: 700; color: #F59E0B; "
                "font-family: 'Consolas', monospace; letter-spacing: 4px;"
            )

        if self.remaining <= 0:
            self.qt_timer.stop()
            self.accept()

    def reject(self):
        pass  # Prevent force-close via ESC


class BatchConfigDialog(QDialog):
    """Dialog enterprise-grade untuk memilih file .ncp dan konfigurasi batch."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Compilation Manager — Nuitka Compiler Pro")
        self.resize(580, 520)
        self.setStyleSheet(ENTERPRISE_STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        self.selected_files = []
        self.cooldown_seconds = 0
        self.shutdown_requested = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(0)

        # --- Title Bar ---
        title_row = QHBoxLayout()
        badge = QLabel("BATCH")
        badge.setStyleSheet(
            "background: #1D4ED8; color: #BFDBFE; font-size: 9px; font-weight: 700; "
            "letter-spacing: 1.5px; padding: 3px 8px; border-radius: 3px; font-family: 'Segoe UI', sans-serif;"
        )
        title_text = QLabel("Batch Compilation Manager")
        title_text.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #F1F5F9; "
            "font-family: 'Segoe UI', sans-serif; margin-left: 10px;"
        )
        title_row.addWidget(badge)
        title_row.addWidget(title_text)
        title_row.addStretch()
        layout.addLayout(title_row)

        layout.addSpacing(6)

        subtitle = QLabel("Queue multiple .ncp profiles and compile them sequentially with hardware protection.")
        subtitle.setStyleSheet("color: #475569; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        layout.addWidget(subtitle)

        layout.addSpacing(18)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1A2540; max-height:1px;")
        layout.addWidget(sep)

        layout.addSpacing(18)

        # --- Section 1: File Selection ---
        s1_label = QLabel("COMPILATION QUEUE")
        s1_label.setStyleSheet(
            "color: #475569; font-size: 9px; font-weight: 700; "
            "letter-spacing: 2px; font-family: 'Segoe UI', sans-serif;"
        )
        layout.addWidget(s1_label)
        layout.addSpacing(8)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(160)
        layout.addWidget(self.file_list)

        layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        add_btn = QPushButton("＋  Add Profiles")
        add_btn.setProperty("class", "primary")
        add_btn.setStyleSheet(add_btn.styleSheet())
        add_btn.clicked.connect(self._add_files)

        del_btn = QPushButton("✕  Remove Selected")
        del_btn.clicked.connect(self._remove_files)

        up_btn = QPushButton("↑")
        up_btn.setFixedWidth(36)
        up_btn.setToolTip("Move Up")
        up_btn.clicked.connect(self._move_up)

        dn_btn = QPushButton("↓")
        dn_btn.setFixedWidth(36)
        dn_btn.setToolTip("Move Down")
        dn_btn.clicked.connect(self._move_down)

        self.count_label = QLabel("0 profile(s) queued")
        self.count_label.setStyleSheet("color: #475569; font-size: 11px; font-family: 'Segoe UI', sans-serif;")

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(dn_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.count_label)
        layout.addLayout(btn_layout)

        self.file_list.model().rowsInserted.connect(self._update_count)
        self.file_list.model().rowsRemoved.connect(self._update_count)

        layout.addSpacing(20)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #1A2540; max-height:1px;")
        layout.addWidget(sep2)

        layout.addSpacing(18)

        # --- Section 2: Cooldown Strategy ---
        s2_label = QLabel("INTER-TASK COOLDOWN STRATEGY")
        s2_label.setStyleSheet(
            "color: #475569; font-size: 9px; font-weight: 700; "
            "letter-spacing: 2px; font-family: 'Segoe UI', sans-serif;"
        )
        layout.addWidget(s2_label)
        layout.addSpacing(8)

        self.cooldown_combo = QComboBox()
        self.cooldown_combo.addItem("●  5 Minutes  —  Standard (Recommended)", 300)
        self.cooldown_combo.addItem("●  10 Minutes  —  Heavy Load / Sustained Build", 600)
        self.cooldown_combo.addItem("●  15 Minutes  —  Maximum Thermal Safety", 900)
        self.cooldown_combo.addItem("○  No Delay  —  Bypass Cooldown (DWYOR)", 0)
        self.cooldown_combo.setToolTip("Time to wait between compilation tasks to allow CPU/RAM to recover.")
        layout.addWidget(self.cooldown_combo)

        layout.addSpacing(16)

        # --- Section 3: Post-Batch Action ---
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("background: #1A2540; max-height:1px;")
        layout.addWidget(sep3)

        layout.addSpacing(16)

        s3_label = QLabel("POST-BATCH ACTION")
        s3_label.setStyleSheet(
            "color: #475569; font-size: 9px; font-weight: 700; "
            "letter-spacing: 2px; font-family: 'Segoe UI', sans-serif;"
        )
        layout.addWidget(s3_label)
        layout.addSpacing(8)

        self.shutdown_check = QCheckBox("  Initiate system shutdown upon batch completion")
        self.shutdown_check.setStyleSheet(
            "color: #FCA5A5; font-weight: 600; font-family: 'Segoe UI', sans-serif;"
        )
        self.shutdown_check.setToolTip("Automatically powers off the computer when all profiles are processed.")
        layout.addWidget(self.shutdown_check)

        layout.addStretch()

        # --- Action Buttons ---
        layout.addSpacing(16)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        self.start_btn = QPushButton("▶  Start Batch Processing")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setStyleSheet(
            "background-color: #1D4ED8; border: 1px solid #2563EB; "
            "color: white; font-size: 13px; font-weight: 700; "
            "border-radius: 6px; padding: 0 20px; font-family: 'Segoe UI', sans-serif;"
        )
        self.start_btn.clicked.connect(self._validate_and_start)

        action_layout.addStretch()
        action_layout.addWidget(cancel_btn)
        action_layout.addWidget(self.start_btn)
        layout.addLayout(action_layout)

    def _update_count(self):
        n = self.file_list.count()
        self.count_label.setText(f"{n} profile(s) queued")

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Nuitka Profiles", "", "Nuitka Profiles (*.ncp)"
        )
        if files:
            for f in files:
                existing = [self.file_list.item(i).text() for i in range(self.file_list.count())]
                if f not in existing:
                    self.file_list.addItem(f)

    def _remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def _move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def _validate_and_start(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Empty Queue", "Please add at least one .ncp profile to the queue.")
            return

        self.selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        self.cooldown_seconds = self.cooldown_combo.currentData()
        self.shutdown_requested = self.shutdown_check.isChecked()
        self.accept()

    def get_data(self):
        return self.selected_files, self.cooldown_seconds, self.shutdown_requested
