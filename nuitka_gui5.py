# nuitka_gui.py  —  Nuitka Compiler Pro v7.5.0
import sys
import os
import shutil
import zipfile
import multiprocessing
import json
import time
import gc
import subprocess
import platform

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDockWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QFileDialog, QTextEdit, QCheckBox, QLabel, QGroupBox,
    QListWidget, QAbstractItemView, QInputDialog, QFormLayout,
    QMessageBox, QComboBox, QFrame, QTabWidget, QScrollArea,
    QSizePolicy, QProgressBar, QStatusBar, QToolBar
)
from PySide6.QtCore import (
    QObject, Signal, QThread, Qt, QTimer, QProcess, QProcessEnvironment,
    QSettings, QSize, QPoint
)
from PySide6.QtGui import QIcon, QCloseEvent, QAction, QPalette

from nuitka_batch import BatchConfigDialog, CooldownDialog
from nuitka_editor import NuitkaProfileEditor
from nuitka_menu import MenuHandler

# Platform flag dipakai di banyak tempat untuk menyesuaikan flag Nuitka,
# ekstensi output, cache path, dan perintah shutdown.
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


# ══════════════════════════════════════════════════════════
#  THEME DEFINITIONS
# ══════════════════════════════════════════════════════════

DARK = {
    "bg":           "#0F1117",
    "bg2":          "#111827",
    "bg3":          "#1A2035",
    "border":       "#1E2D4A",
    "border2":      "#222F45",
    "text":         "#CBD5E1",
    "text2":        "#94A3B8",
    "text3":        "#475569",
    "text4":        "#334155",
    "accent":       "#2563EB",
    "accent2":      "#1D4ED8",
    "accent_light": "#60A5FA",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "danger_bg":    "#450A0A",
    "log_bg":       "#080D14",
    "mono":         "#94A3B8",
}

LIGHT = {
    "bg":           "#F1F5F9",
    "bg2":          "#FFFFFF",
    "bg3":          "#F8FAFC",
    "border":       "#CBD5E1",
    "border2":      "#E2E8F0",
    "text":         "#0F172A",
    "text2":        "#334155",
    "text3":        "#64748B",
    "text4":        "#94A3B8",
    "accent":       "#2563EB",
    "accent2":      "#1D4ED8",
    "accent_light": "#3B82F6",
    "success":      "#059669",
    "warning":      "#D97706",
    "danger":       "#DC2626",
    "danger_bg":    "#FEF2F2",
    "log_bg":       "#F8FAFC",
    "mono":         "#334155",
}


def make_stylesheet(t: dict) -> str:
    return f"""
QWidget {{
    background-color: {t['bg']};
    color: {t['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    border: none;
    outline: none;
}}
QMainWindow, QDialog {{
    background-color: {t['bg']};
}}
QMainWindow::separator {{
    background: {t['border']};
    width: 4px; height: 4px;
}}
QMainWindow::separator:hover {{ background: {t['accent']}; }}

QDockWidget {{
    background: {t['bg2']};
    color: {t['text']};
    border: 1px solid {t['border']};
}}
QDockWidget::title {{
    background: {t['bg3']};
    padding: 6px 10px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px;
    color: {t['text3']};
    border-bottom: 1px solid {t['border']};
    text-align: left;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    background: transparent; border: none; padding: 2px;
}}
QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
    background: {t['border']}; border-radius: 3px;
}}

QToolBar {{
    background: {t['bg2']};
    border-bottom: 1px solid {t['border']};
    spacing: 2px; padding: 2px 8px;
}}
QToolBar QToolButton {{
    background: transparent;
    color: {t['text2']};
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px; font-weight: 600;
}}
QToolBar QToolButton:hover {{
    background: {t['bg3']};
    border-color: {t['border']};
    color: {t['text']};
}}
QToolBar QToolButton:pressed {{ background: {t['border']}; }}
QToolBar QToolButton:checked {{
    background: {t['accent2']};
    color: white;
    border-color: {t['accent']};
}}
QToolBar::separator {{
    background: {t['border']}; width: 1px; margin: 4px 2px;
}}

QMenuBar {{
    background: {t['bg2']};
    color: {t['text2']};
    border-bottom: 1px solid {t['border']};
    padding: 2px 4px; font-size: 12px;
}}
QMenuBar::item {{
    padding: 5px 12px; border-radius: 4px; background: transparent;
}}
QMenuBar::item:selected {{
    background: {t['bg3']}; color: {t['text']};
}}
QMenuBar::item:pressed {{
    background: {t['accent2']}; color: white;
}}
QMenu {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    border-radius: 6px; padding: 4px;
    color: {t['text']}; font-size: 12px;
}}
QMenu::item {{ padding: 7px 20px 7px 14px; border-radius: 4px; }}
QMenu::item:selected {{ background: {t['bg3']}; color: {t['text']}; }}
QMenu::item:disabled {{ color: {t['text4']}; }}
QMenu::separator {{
    height: 1px; background: {t['border']}; margin: 4px 8px;
}}

QGroupBox {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    margin-top: 18px;
    padding: 10px 10px 10px 10px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px; color: {t['text3']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px; padding: 2px 8px;
    color: {t['text3']};
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px;
    background: {t['bg2']};
}}

QLineEdit {{
    background: {t['bg3']};
    border: 1px solid {t['border2']};
    border-radius: 5px;
    color: {t['text']};
    padding: 6px 10px; font-size: 12px;
    selection-background-color: {t['accent']};
    selection-color: white;
}}
QLineEdit:focus {{ border-color: {t['accent']}; }}

QComboBox {{
    background: {t['bg3']};
    border: 1px solid {t['border2']};
    border-radius: 5px;
    color: {t['text']};
    padding: 6px 32px 6px 10px;
    font-size: 12px; min-height: 28px;
}}
QComboBox:focus {{ border-color: {t['accent']}; }}
QComboBox:hover {{ border-color: {t['text4']}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px; border: none;
    border-left: 1px solid {t['border2']};
}}
QComboBox::down-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {t['text3']};
    width: 0; height: 0;
}}
QComboBox QAbstractItemView {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    color: {t['text']};
    selection-background-color: {t['bg3']};
    selection-color: {t['text']};
    padding: 4px; outline: none;
}}

QCheckBox {{
    color: {t['text2']}; spacing: 8px;
    font-size: 12px; background: transparent;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid {t['border']};
    border-radius: 3px; background: {t['bg3']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
}}
QCheckBox::indicator:hover {{ border-color: {t['accent_light']}; }}
QCheckBox:hover {{ color: {t['text']}; }}

QPushButton {{
    background: {t['bg3']};
    border: 1px solid {t['border2']};
    border-radius: 5px; color: {t['text2']};
    padding: 6px 14px; font-size: 12px;
    font-weight: 600; min-height: 28px;
    min-width: 60px;
}}
QPushButton:hover {{
    border-color: {t['text4']}; color: {t['text']};
    background: {t['bg3']};
}}
QPushButton:pressed {{ background: {t['border']}; }}
QPushButton:disabled {{
    background: {t['bg3']};
    border-color: {t['border2']}; color: {t['text4']};
}}

QListWidget {{
    background: {t['bg3']};
    border: 1px solid {t['border2']};
    border-radius: 5px; color: {t['text2']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px; padding: 3px;
    selection-background-color: {t['accent2']};
    selection-color: white; outline: none;
}}
QListWidget::item {{
    padding: 4px 8px; border-radius: 3px;
}}
QListWidget::item:hover {{ background: {t['border2']}; }}
QListWidget::item:selected {{
    background: {t['accent2']}; color: white;
}}

QTextEdit {{
    background: {t['log_bg']};
    border: 1px solid {t['border']};
    border-radius: 5px; color: {t['mono']};
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px; padding: 6px;
    selection-background-color: {t['accent']};
}}

QTabWidget::pane {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    border-top: none;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
}}
QTabBar {{ background: transparent; }}
QTabBar::tab {{
    background: {t['bg3']}; color: {t['text3']};
    padding: 7px 18px;
    border: 1px solid {t['border']};
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.5px; margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {t['bg2']}; color: {t['accent_light']};
}}
QTabBar::tab:hover:!selected {{
    background: {t['bg3']}; color: {t['text2']};
}}

QScrollBar:vertical {{
    background: {t['bg']}; width: 8px; margin: 0; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {t['border']}; border-radius: 4px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {t['text4']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {t['bg']}; height: 8px; margin: 0; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {t['border']}; border-radius: 4px; min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QStatusBar {{
    background: {t['bg2']};
    color: {t['text3']};
    border-top: 1px solid {t['border']};
    font-size: 11px; padding: 0 4px;
}}
QStatusBar::item {{ border: none; }}

QProgressBar {{
    border: none; border-radius: 3px;
    background: {t['border']};
    text-align: center; color: transparent;
    font-size: 0px; max-height: 6px; min-height: 6px;
}}
QProgressBar::chunk {{
    border-radius: 3px; background: {t['accent']};
}}

QSplitter::handle {{ background: {t['border']}; }}
QSplitter::handle:hover {{ background: {t['accent']}; }}

QLabel {{ background: transparent; color: {t['text2']}; }}

QFrame[frameShape="4"] {{
    color: {t['border']}; max-height: 1px;
    border: none; background: {t['border']};
}}
QFrame[frameShape="5"] {{
    color: {t['border']}; max-width: 1px;
    border: none; background: {t['border']};
}}

QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
"""


def compile_btn_style(t: dict) -> str:
    return f"""
QPushButton {{
    background: {t['accent2']};
    border: 1px solid {t['accent']};
    border-radius: 6px; color: white;
    font-size: 13px; font-weight: 700;
    padding: 0 22px; min-height: 34px;
    letter-spacing: 0.3px;
}}
QPushButton:hover {{
    background: {t['accent']};
    border-color: {t['accent_light']};
}}
QPushButton:pressed {{ background: {t['accent2']}; }}
QPushButton:disabled {{
    background: {t['bg3']}; color: {t['text4']};
    border-color: {t['border2']};
}}
"""


# ══════════════════════════════════════════════════════════
#  WORKER THREADS
# ══════════════════════════════════════════════════════════

class CompilerWorker(QObject):
    progress_update = Signal(str)
    finished        = Signal(str)

    def __init__(self, command: str):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            if "PROCESSOR_ARCHITECTURE" not in env:
                import platform
                env["PROCESSOR_ARCHITECTURE"] = "AMD64" if platform.machine().endswith("64") else "x86"

            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                shell=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            for line in iter(self.process.stdout.readline, ''):
                s = line.rstrip()
                if s:
                    self.progress_update.emit(s)

            self.process.wait()
            rc = self.process.returncode
            if rc == 0:
                self.finished.emit("COMPILATION_SUCCESSFUL")
            else:
                self.finished.emit(f"COMPILATION_FAILED:{rc}")
        except Exception as e:
            self.finished.emit(f"COMPILATION_ERROR:{e}")


class AssetCopyWorker(QObject):
    finished = Signal(str)

    def __init__(self, src, dst):
        super().__init__()
        self.src, self.dst = src, dst

    def run(self):
        try:
            if os.path.isdir(self.dst):
                shutil.rmtree(self.dst)
            shutil.copytree(self.src, self.dst)
            self.finished.emit("ASSET_COPY_SUCCESS")
        except Exception as e:
            self.finished.emit(f"ASSET_COPY_FAILED:{e}")


class ZipWorker(QObject):
    progress_update = Signal(str)
    finished = Signal(str)

    def __init__(self, src, zip_path, is_onefile):
        super().__init__()
        self.src, self.zip_path, self.is_onefile = src, zip_path, is_onefile

    def run(self):
        try:
            with zipfile.ZipFile(self.zip_path, 'w', compression=zipfile.ZIP_LZMA) as zf:
                if self.is_onefile:
                    zf.write(self.src, arcname=os.path.basename(self.src))
                else:
                    files = [os.path.join(r, f)
                             for r, _, fs in os.walk(self.src) for f in fs]
                    for i, fp in enumerate(files):
                        zf.write(fp, arcname=os.path.relpath(fp, self.src))
                        if (i + 1) % 150 == 0:
                            self.progress_update.emit(f"  {i+1}/{len(files)} files...")
            self.finished.emit(f"ZIP_SUCCESS:{self.zip_path}")
        except Exception as e:
            self.finished.emit(f"ZIP_FAILED:{e}")


# ══════════════════════════════════════════════════════════
#  STATUS BAR MONITOR
# ══════════════════════════════════════════════════════════

class SysMonitor(QWidget):
    def __init__(self, theme: dict, parent=None):
        super().__init__(parent)
        self.t = theme
        lo = QHBoxLayout(self)
        lo.setContentsMargins(4, 0, 8, 0)
        lo.setSpacing(5)

        def _bar():
            b = QProgressBar()
            b.setFixedWidth(64)
            b.setTextVisible(False)
            return b

        cpu_lbl = QLabel("CPU")
        cpu_lbl.setStyleSheet(f"color:{theme['text4']};font-size:9px;font-weight:700;letter-spacing:1px;")
        lo.addWidget(cpu_lbl)
        self.cpu_bar = _bar()
        lo.addWidget(self.cpu_bar)
        self.cpu_pct = QLabel("0%")
        self.cpu_pct.setFixedWidth(30)
        self.cpu_pct.setStyleSheet(f"color:{theme['text3']};font-family:'Consolas',monospace;font-size:11px;")
        lo.addWidget(self.cpu_pct)

        lo.addSpacing(8)

        ram_lbl = QLabel("RAM")
        ram_lbl.setStyleSheet(f"color:{theme['text4']};font-size:9px;font-weight:700;letter-spacing:1px;")
        lo.addWidget(ram_lbl)
        self.ram_bar = _bar()
        lo.addWidget(self.ram_bar)
        self.ram_pct = QLabel("0%")
        self.ram_pct.setFixedWidth(30)
        self.ram_pct.setStyleSheet(f"color:{theme['text3']};font-family:'Consolas',monospace;font-size:11px;")
        lo.addWidget(self.ram_pct)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.tick)
        self._timer.start(1500)
        self.tick()

    def _bar_style(self, color):
        return (f"QProgressBar{{border:none;border-radius:3px;"
                f"background:{self.t['border']};max-height:6px;min-height:6px;}}"
                f"QProgressBar::chunk{{border-radius:3px;background:{color};}}")

    def apply_theme(self, theme):
        self.t = theme
        self.tick()

    def tick(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            self.cpu_bar.setValue(int(cpu))
            self.cpu_pct.setText(f"{int(cpu)}%")
            c = self.t['danger'] if cpu > 85 else (self.t['warning'] if cpu > 60 else self.t['success'])
            self.cpu_bar.setStyleSheet(self._bar_style(c))

            ram = psutil.virtual_memory()
            self.ram_bar.setValue(int(ram.percent))
            self.ram_pct.setText(f"{int(ram.percent)}%")
            c = self.t['danger'] if ram.percent > 85 else (self.t['warning'] if ram.percent > 65 else self.t['accent'])
            self.ram_bar.setStyleSheet(self._bar_style(c))
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════

class NuitkaGui(QMainWindow):
    batch_step_finished = Signal()

    def __init__(self):
        super().__init__()
        self.compiler_thread = None
        self.compiler_worker = None
        self.asset_thread = None
        self.asset_worker = None
        self.zip_thread = None
        self.zip_worker = None
        self.settings = QSettings("Danx", "NuitkaCompilerPro")
        self.current_profile_path = None
        self.is_batch_running = False
        self.batch_queue = []
        self.batch_cooldown_time = 0
        self.batch_current_index = 0
        self.batch_shutdown_mode = False
        self.compilation_start_time = 0
        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.setInterval(1000)
        self.elapsed_timer.timeout.connect(self._tick_elapsed)

        saved = self.settings.value("app/theme", "dark")
        self._theme_name = saved
        self._t = DARK if saved == "dark" else LIGHT

        self._build_ui()
        self._load_settings()
        QApplication.instance().setStyleSheet(make_stylesheet(self._t))
        self._apply_dynamic()

        if len(sys.argv) > 1 and sys.argv[1].endswith(".ncp"):
            QTimer.singleShot(500, lambda: self.load_profile_direct(sys.argv[1]))

    # ── Build UI ─────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("Nuitka Compiler Pro")
        self.setMinimumSize(900, 640)
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks |
            QMainWindow.DockOption.AnimatedDocks
        )

        icon_path = "compiler.ico"
        # Support both PyInstaller (_MEIPASS) and Nuitka (__compiled__ / sys.frozen)
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
            icon_path = os.path.join(base, "compiler.ico")
        elif hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "compiler.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_toolbar()

        # Central widget
        cw = QWidget()
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(8)
        cl.addWidget(self._make_io_group())
        cl.addWidget(self._make_tabs())
        cl.addWidget(self._make_include_group())
        cl.addWidget(self._make_action_bar())
        self.setCentralWidget(cw)

        self._build_log_dock()
        self._build_status_bar()

        # Menu bar — built last so it can reference _log_dock & _theme_action
        self.menu_handler = MenuHandler(self)

    def _build_toolbar(self):
        tb = QToolBar("Toolbar")
        tb.setObjectName("MainToolbar")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        def _act(label, tip, shortcut, fn):
            a = QAction(label, self)
            if tip: a.setToolTip(tip)
            if shortcut: a.setShortcut(shortcut)
            a.triggered.connect(fn)
            tb.addAction(a)
            return a

        _act("New",      "Reset (Ctrl+N)",      "Ctrl+N", self.reset_ui)
        _act("Save",     "Save profile (Ctrl+S)","Ctrl+S", self.save_profile)
        _act("Save As",  "",                    "Ctrl+Shift+S", self.save_profile_as)
        _act("Load",     "Load profile (Ctrl+O)","Ctrl+O", self.load_profile)
        tb.addSeparator()
        _act("Batch",    "Batch mode (Ctrl+B)", "Ctrl+B", self.open_batch_dialog)
        _act("Preview",  "Preview command",     "Ctrl+P", self.preview_command)
        _act("JSON Ed.", "Raw JSON editor",     "Ctrl+E", self.open_profile_editor)
        _act("Cache",    "Clear Nuitka cache",  "",       self.clear_nuitka_cache)
        tb.addSeparator()

        # Theme toggle
        self._theme_action = QAction("☀ Light", self)
        self._theme_action.setCheckable(True)
        self._theme_action.setChecked(self._theme_name == "light")
        self._theme_action.triggered.connect(self._toggle_theme)
        tb.addAction(self._theme_action)

        tb.addSeparator()
        _act("Reload",   "Restart app",         "Ctrl+R", self.reload_application)

        # Spacer
        sp = QWidget()
        sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sp.setStyleSheet("background:transparent;")
        tb.addWidget(sp)

        # Compile button embedded in toolbar
        self.compile_btn = QPushButton("▶  Compile")
        self.compile_btn.setFixedHeight(30)
        self.compile_btn.setMinimumWidth(110)
        self.compile_btn.clicked.connect(self.run_compilation)
        tb.addWidget(self.compile_btn)

    def _make_io_group(self):
        grp = QGroupBox("INPUT / OUTPUT")
        fl = QFormLayout(grp)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(8)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        fl.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.script_edit = QLineEdit()
        self.script_edit.setPlaceholderText("Select .py entry point...")
        sb = QPushButton("Browse")
        sb.setMinimumWidth(70)
        sb.setFixedHeight(30)
        sb.clicked.connect(lambda: self._browse_file(self.script_edit, "Python Files (*.py *.pyw)"))
        sr = QHBoxLayout(); sr.setSpacing(4)
        sr.addWidget(self.script_edit); sr.addWidget(sb)
        fl.addRow(self._fl("Script:"), sr)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Leave empty to use script directory...")
        ob = QPushButton("Browse")
        ob.setMinimumWidth(70)
        ob.setFixedHeight(30)
        ob.clicked.connect(lambda: self._browse_dir(self.output_edit))
        or_ = QHBoxLayout(); or_.setSpacing(4)
        or_.addWidget(self.output_edit); or_.addWidget(ob)
        fl.addRow(self._fl("Output Dir:"), or_)
        return grp

    def _make_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_build_tab(),    "BUILD OPTIONS")
        self.tabs.addTab(self._make_advanced_tab(), "ADVANCED")
        self.tabs.addTab(self._make_metadata_tab(), "METADATA")
        return self.tabs

    def _make_build_tab(self):
        tab = QWidget()
        outer = QHBoxLayout(tab)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(16)

        # Left — checkboxes
        left = QVBoxLayout()
        left.setSpacing(7)
        onefile_label = "One-File Mode  (.exe)" if IS_WINDOWS else "One-File Mode  (single binary)"
        self.onefile_check         = QCheckBox(onefile_label)
        self.disable_console_check = QCheckBox("Disable Console Window")
        if not IS_WINDOWS:
            self.disable_console_check.setEnabled(False)
            self.disable_console_check.setToolTip("Windows only (--windows-disable-console). Ignored on Linux.")
        self.antibloat_check       = QCheckBox("Anti-Bloat  (Reduce Size)")
        self.antibloat_check.setToolTip("Strips pytest/setuptools. May break imports.")
        self.deploy_zip_check      = QCheckBox("Deploy as .zip  (LZMA)")
        self.multimedia_check      = QCheckBox("Multimedia Plugin  (PySide6)")
        self.multimedia_check.setToolTip("Copy PySide6 DLLs — One-Directory mode only")
        self.shutdown_check        = QCheckBox("Shutdown PC when done")
        for cb in [self.onefile_check, self.disable_console_check,
                   self.antibloat_check, self.deploy_zip_check,
                   self.multimedia_check, self.shutdown_check]:
            left.addWidget(cb)
        left.addStretch()

        # Right — QFormLayout
        right_form = QFormLayout()
        right_form.setSpacing(9)
        right_form.setContentsMargins(0, 0, 0, 0)
        right_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.jobs_combo = QComboBox()
        cpu = multiprocessing.cpu_count()
        for n in ['1','2','4','8','12','16','24','32']:
            if int(n) <= max(cpu * 2, 8):
                self.jobs_combo.addItem(n)
        self.jobs_combo.setCurrentText('4')
        self.jobs_combo.setToolTip("CPU cores for compilation")
        right_form.addRow(self._fl("Cores:"), self.jobs_combo)

        self.lto_combo = QComboBox()
        self.lto_combo.addItem("No LTO  (Faster Build)", "no")
        self.lto_combo.addItem("LTO Enabled  (Smaller Binary)", "yes")
        self.lto_combo.addItem("Thin LTO  (Balanced)", "thin")
        self.lto_combo.setToolTip("No=fastest, Yes=smallest, Thin=balanced")
        right_form.addRow(self._fl("LTO:"), self.lto_combo)

        self.python_exe_edit = QLineEdit()
        self.python_exe_edit.setPlaceholderText("Default: python in PATH...")
        pyb = QPushButton("Browse")
        pyb.setMinimumWidth(70)
        pyb.setFixedHeight(30)
        pyb.clicked.connect(lambda: self._browse_file(self.python_exe_edit, "Executable (*.exe *)"))
        py_r = QHBoxLayout(); py_r.setSpacing(4)
        py_r.addWidget(self.python_exe_edit); py_r.addWidget(pyb)
        right_form.addRow(self._fl("Python Exe:"), py_r)

        self.icon_edit = QLineEdit()
        icon_filter = "Icon Files (*.ico)" if IS_WINDOWS else "Icon Files (*.ico *.png *.xpm *.svg)"
        self.icon_edit.setPlaceholderText("Select .ico file..." if IS_WINDOWS else "Select .ico / .png / .svg file...")
        icob = QPushButton("Browse")
        icob.setMinimumWidth(70)
        icob.setFixedHeight(30)
        icob.clicked.connect(lambda: self._browse_file(self.icon_edit, icon_filter))
        ico_r = QHBoxLayout(); ico_r.setSpacing(4)
        ico_r.addWidget(self.icon_edit); ico_r.addWidget(icob)
        right_form.addRow(self._fl("App Icon:"), ico_r)

        rw = QWidget(); rw.setLayout(right_form)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine)
        outer.addLayout(left, 1)
        outer.addWidget(sep)
        outer.addWidget(rw, 1)
        return tab

    def _make_advanced_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        fl = QFormLayout(inner)
        fl.setContentsMargins(14, 12, 14, 12)
        fl.setSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        fl.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.msvc_combo = QComboBox()
        self.msvc_combo.addItem("Auto-detect  (no flag)", "")
        self.msvc_combo.addItem("MSVC 14.3  (VS 2022)", "14.3")
        self.msvc_combo.addItem("MSVC 14.2  (VS 2019)", "14.2")
        self.msvc_combo.addItem("MSVC 14.1  (VS 2017)", "14.1")
        self.msvc_combo.addItem("Clang / MinGW  (no flag)", "none")
        if not IS_WINDOWS:
            self.msvc_combo.setEnabled(False)
            self.msvc_combo.setToolTip("Windows only (--msvc). Nuitka uses gcc/clang automatically on Linux.")
        fl.addRow(self._fl("MSVC Version:"), self.msvc_combo)

        self.opt_combo = QComboBox()
        self.opt_combo.addItem("None  (default)", "")
        self.opt_combo.addItem("Level 1  (-O, strip asserts)", "1")
        self.opt_combo.addItem("Level 2  (-OO, strip docstrings)", "2")
        fl.addRow(self._fl("Python Opt:"), self.opt_combo)

        self.output_filename_edit = QLineEdit()
        self.output_filename_edit.setPlaceholderText("Leave empty to use script name...")
        fl.addRow(self._fl("Output Name:"), self.output_filename_edit)

        fl.addRow(self._hsep())

        # Checkboxes in a container (avoids the empty-label column bug)
        self.follow_imports_check = QCheckBox("--follow-imports")
        self.follow_imports_check.setToolTip("Recursively include all imported modules")
        self.show_scons_check = QCheckBox("--show-scons")
        self.show_scons_check.setToolTip("Show detailed SCons build output")
        self.assume_yes_check = QCheckBox("--assume-yes-for-downloads")
        self.assume_yes_check.setToolTip("Auto-accept download prompts")
        self.remove_output_check = QCheckBox("--remove-output  (clean .build folder)")
        self.remove_output_check.setChecked(True)
        self.no_pyc_check = QCheckBox("--no-pyi-file")
        self.no_pyc_check.setToolTip("Skip .pyi stub generation")

        cb_box = QGroupBox("FLAGS")
        cb_inner = QVBoxLayout(cb_box)
        cb_inner.setSpacing(6)
        cb_inner.setContentsMargins(8, 8, 8, 8)
        for cb in [self.follow_imports_check, self.show_scons_check,
                   self.assume_yes_check, self.remove_output_check, self.no_pyc_check]:
            cb_inner.addWidget(cb)
        fl.addRow(cb_box)

        fl.addRow(self._hsep())

        self.extra_flags_edit = QLineEdit()
        self.extra_flags_edit.setPlaceholderText("--prefer-source-code --python-flag=no_site ...")
        fl.addRow(self._fl("Extra Flags:"), self.extra_flags_edit)

        scroll.setWidget(inner)
        return scroll

    def _make_metadata_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        fl = QFormLayout(inner)
        fl.setContentsMargins(14, 12, 14, 12)
        fl.setSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        fl.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        def _e(ph):
            e = QLineEdit(); e.setPlaceholderText(ph); return e

        self.product_name_edit     = _e("My Application")
        self.product_version_edit  = _e("1.0.0.0")
        self.file_version_edit     = _e("1.0.0.0")
        self.file_description_edit = _e("Application description")
        self.copyright_edit        = _e("© 2026 Company Name")
        self.trademarks_edit       = _e("Optional trademark string")

        fl.addRow(self._fl("Product Name:"),    self.product_name_edit)
        fl.addRow(self._fl("Product Version:"), self.product_version_edit)
        fl.addRow(self._fl("File Version:"),    self.file_version_edit)
        fl.addRow(self._fl("Description:"),     self.file_description_edit)
        fl.addRow(self._fl("Copyright:"),       self.copyright_edit)
        fl.addRow(self._fl("Trademarks:"),      self.trademarks_edit)

        scroll.setWidget(inner)
        return scroll

    def _make_include_group(self):
        grp = QGroupBox("INCLUDE FILES, FOLDERS & MODULES")
        lo = QHBoxLayout(grp)
        lo.setContentsMargins(10, 8, 10, 8)
        lo.setSpacing(10)

        def _col(title, add_fn, rem_fn):
            col = QVBoxLayout(); col.setSpacing(4)
            hdr = QLabel(title)
            hdr.setStyleSheet(f"color:{self._t['text4']};font-size:9px;font-weight:700;letter-spacing:1.5px;")
            col.addWidget(hdr)
            lw = QListWidget()
            lw.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            lw.setMinimumHeight(70)
            col.addWidget(lw, 1)
            btns = QHBoxLayout(); btns.setSpacing(4)
            ab = QPushButton("＋ Add"); ab.setFixedHeight(24); ab.clicked.connect(add_fn)
            rb = QPushButton("✕"); rb.setFixedWidth(26); rb.setFixedHeight(24); rb.clicked.connect(rem_fn)
            btns.addWidget(ab); btns.addWidget(rb)
            col.addLayout(btns)
            return col, lw

        fc, self.file_list_widget   = _col("FILES",   self._add_files,  self._rem_files)
        dc, self.folder_list_widget = _col("FOLDERS", self._add_folder, self._rem_folders)
        mc, self.module_list_widget = _col("MODULES", self._add_module, self._rem_modules)
        lo.addLayout(fc); lo.addLayout(dc); lo.addLayout(mc)
        return grp

    def _make_action_bar(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        lo = QHBoxLayout(w)
        lo.setContentsMargins(0, 4, 0, 0)
        lo.setSpacing(6)
        clr = QPushButton("Clear Log"); clr.clicked.connect(self.clear_log)
        lo.addWidget(clr)
        lo.addStretch()
        self.compile_btn2 = QPushButton("▶  Start Compilation")
        self.compile_btn2.setMinimumHeight(36)
        self.compile_btn2.setMinimumWidth(170)
        self.compile_btn2.clicked.connect(self.run_compilation)
        lo.addWidget(self.compile_btn2)
        return w

    def _build_log_dock(self):
        dock = QDockWidget("COMPILATION LOG", self)
        dock.setObjectName("LogDock")
        dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        inner = QWidget()
        lo = QVBoxLayout(inner)
        lo.setContentsMargins(8, 6, 8, 8)
        lo.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        self.status_indicator = QLabel("●  IDLE")
        self.status_indicator.setStyleSheet(
            f"color:{self._t['text4']};font-size:10px;font-weight:700;letter-spacing:1px;"
        )
        self.elapsed_label = QLabel("00:00:00")
        self.elapsed_label.setStyleSheet(
            f"color:{self._t['text4']};font-family:'Consolas',monospace;font-size:11px;"
            f"padding:1px 6px;background:{self._t['bg']};border:1px solid {self._t['border']};border-radius:3px;"
        )
        hdr.addWidget(self.status_indicator)
        hdr.addStretch()
        el = QLabel("Elapsed:")
        el.setStyleSheet(f"color:{self._t['text4']};font-size:11px;")
        hdr.addWidget(el)
        hdr.addWidget(self.elapsed_label)
        lo.addLayout(hdr)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        lo.addWidget(self.log_output, 1)

        foot = QHBoxLayout()
        clr = QPushButton("Clear"); clr.setFixedHeight(24); clr.clicked.connect(self.clear_log)
        foot.addWidget(clr); foot.addStretch()
        lo.addLayout(foot)

        dock.setWidget(inner)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self._log_dock = dock

    def _build_status_bar(self):
        sb = QStatusBar()
        sb.setObjectName("MainStatusBar")
        self.setStatusBar(sb)

        self._sb_msg = QLabel("Ready")
        self._sb_msg.setStyleSheet(f"color:{self._t['text3']};padding:0 6px;")
        sb.addWidget(self._sb_msg)

        # OS + bit (no CPU name)
        bits = "64-bit" if sys.maxsize > 2**32 else "32-bit"
        os_str = f"{platform.system()} {platform.release()}  ·  {bits}"
        os_lbl = QLabel(os_str)
        os_lbl.setStyleSheet(f"color:{self._t['text4']};font-size:11px;padding:0 8px;")
        sb.addPermanentWidget(os_lbl)

        self._sys_monitor = SysMonitor(self._t)
        sb.addPermanentWidget(self._sys_monitor)

    # ── Theme ─────────────────────────────────────────────

    def _toggle_theme(self, checked):
        self._theme_name = "light" if checked else "dark"
        self._t = LIGHT if checked else DARK
        self.settings.setValue("app/theme", self._theme_name)
        self._theme_action.setText("☀ Light" if checked else "🌙 Dark")
        QApplication.instance().setStyleSheet(make_stylesheet(self._t))
        self._apply_dynamic()
        # Sync View menu checkbox if menu is built
        if hasattr(self, 'menu_handler') and hasattr(self.menu_handler, '_view_theme_action'):
            self.menu_handler._view_theme_action.setChecked(checked)

    def _apply_dynamic(self):
        t = self._t
        cs = compile_btn_style(t)
        self.compile_btn.setStyleSheet(cs)
        self.compile_btn2.setStyleSheet(cs)
        self.antibloat_check.setStyleSheet(f"color:{t['warning']};font-weight:600;")
        self.shutdown_check.setStyleSheet(f"color:{t['danger']};font-weight:600;")
        # Re-style status indicator based on current state
        txt = self.status_indicator.text()
        if "RUNNING" in txt:   self._set_status("RUNNING", t['warning'])
        elif "SUCCESS" in txt: self._set_status("SUCCESS", t['success'])
        elif "FAILED" in txt:  self._set_status("FAILED",  t['danger'])
        else:                  self._set_status("IDLE",    t['text4'])
        # Elapsed label
        self.elapsed_label.setStyleSheet(
            f"color:{t['text4']};font-family:'Consolas',monospace;font-size:11px;"
            f"padding:1px 6px;background:{t['bg']};border:1px solid {t['border']};border-radius:3px;"
        )
        if hasattr(self, '_sys_monitor'):
            self._sys_monitor.apply_theme(t)
        if hasattr(self, '_sb_msg'):
            self._sb_msg.setStyleSheet(f"color:{t['text3']};padding:0 6px;")

    # ── Helpers ───────────────────────────────────────────

    def _fl(self, text) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(
            f"color:{self._t['text3']};font-size:11px;font-weight:600;"
            f"min-width:110px;background:transparent;"
        )
        return l

    def _hsep(self) -> QFrame:
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine); return f

    def _browse_file(self, edit, filt="All Files (*.*)"):
        f, _ = QFileDialog.getOpenFileName(self, "Select File", "", filt)
        if f: edit.setText(f)

    def _browse_dir(self, edit):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if d: edit.setText(d)

    def _add_files(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*.*)")
        if fs: self.file_list_widget.addItems(fs)

    def _rem_files(self):
        for i in self.file_list_widget.selectedItems():
            self.file_list_widget.takeItem(self.file_list_widget.row(i))

    def _add_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder")
        if d: self.folder_list_widget.addItem(d)

    def _rem_folders(self):
        for i in self.folder_list_widget.selectedItems():
            self.folder_list_widget.takeItem(self.folder_list_widget.row(i))

    def _add_module(self):
        t, ok = QInputDialog.getText(self, "Add Module", "Module name:")
        if ok and t.strip(): self.module_list_widget.addItem(t.strip())

    def _rem_modules(self):
        for i in self.module_list_widget.selectedItems():
            self.module_list_widget.takeItem(self.module_list_widget.row(i))

    def open_profile_editor(self):
        NuitkaProfileEditor(self).exec()

    # ── Recent files ──────────────────────────────────────

    def _add_recent(self, path):
        if not path or not os.path.exists(path): return
        path = os.path.normpath(path)
        r = self._get_recent()
        if path in r: r.remove(path)
        r.insert(0, path)
        self.settings.setValue("recent_files", r[:10])
        # Sync with menu bar handler if available
        if hasattr(self, 'menu_handler'):
            self.menu_handler.refresh_recent_menu()

    def _get_recent(self):
        r = self.settings.value("recent_files", [])
        if isinstance(r, str): r = [r] if r else []
        return [f for f in r if os.path.exists(f)]

    # ── Batch ─────────────────────────────────────────────

    def open_batch_dialog(self):
        if self.compiler_thread and self.compiler_thread.isRunning():
            QMessageBox.warning(self, "Busy", "Compilation is already running."); return
        dlg = BatchConfigDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            files, cd, sd = dlg.get_data()
            self._start_batch(files, cd, sd)

    def _start_batch(self, files, cooldown, shutdown):
        if not files: return
        self.is_batch_running = True
        self.batch_queue = list(files)
        self.batch_cooldown_time = cooldown
        self.batch_shutdown_mode = shutdown
        self.batch_current_index = 0
        self._log(f"<font color='{self._t['accent_light']}'>{'─'*48}</font>")
        self._log(f"<font color='{self._t['accent_light']}'>=== STARTED BATCH PROCESSING ({len(files)} files) ===</font>")
        try: self.batch_step_finished.disconnect()
        except Exception: pass
        self.batch_step_finished.connect(self._next_batch)
        self._next_batch(first=True)

    def _next_batch(self, first=False):
        # Cooldown — skip di iterasi pertama
        if not first and self.batch_cooldown_time > 0:
            self._log(f"<font color='{self._t['warning']}'> --- Cooling down {self.batch_cooldown_time}s ---</font>")
            CooldownDialog(self.batch_cooldown_time, self).exec()
            self._log(f"<font color='{self._t['success']}'> --- Cooldown complete. Resuming... ---</font>")

        # Semua item selesai
        if self.batch_current_index >= len(self.batch_queue):
            self.is_batch_running = False
            self._log(f"<font color='#A78BFA'>=== BATCH PROCESSING COMPLETED ===</font>")
            try: self.batch_step_finished.disconnect()
            except Exception: pass

            if self.batch_shutdown_mode:
                self._log(f"<font color='{self._t['danger']}'><b> BATCH COMPLETE. INITIATING SHUTDOWN...</b></font>")
                QTimer.singleShot(3000, self._shutdown)
            else:
                QMessageBox.information(self, "Done",
                    f"All {len(self.batch_queue)} profiles processed.")
            return

        profile = self.batch_queue[self.batch_current_index]
        self.batch_current_index += 1

        self._log(f"<font color='{self._t['accent_light']}'> --- Batch Step {self.batch_current_index}/{len(self.batch_queue)}: {os.path.basename(profile)} ---</font>")
        self._reset_internal()
        gc.collect()

        if self.load_profile_direct(profile):
            # QTimer memberi waktu event loop bersihkan state sebelumnya
            QTimer.singleShot(1500, self.run_compilation)
        else:
            self._log(f"<font color='{self._t['danger']}'> Skipping invalid profile: {profile}</font>")
            QTimer.singleShot(500, self.batch_step_finished.emit)

    # ── Compilation ───────────────────────────────────────

    def run_compilation(self):
        cmd = self._build_cmd()
        if not cmd:
            if self.is_batch_running:
                self._log(f"<font color='{self._t['danger']}'> Batch Error: Invalid command. Skipping...</font>")
                self.batch_step_finished.emit()
            return

        if not self._check_linux_build_deps():
            if self.is_batch_running:
                self._log(f"<font color='{self._t['danger']}'> Batch Error: Missing Linux build tools. Skipping...</font>")
                self.batch_step_finished.emit()
            return

        # Pengecekan thread aktif — persis seperti nuitka_gui_26
        if self.compiler_thread is not None:
            if self.compiler_thread.isRunning():
                if not self.is_batch_running:
                    QMessageBox.warning(self, "Busy", "Already compiling."); return
                return
            else:
                # Thread ada tapi sudah selesai — force cleanup
                self.compiler_thread = None

        if not self.is_batch_running: self.clear_log()

        self._log(f"<font color='{self._t['text4']}'> CMD: {cmd}</font>")
        self._set_btn_state(False, "Compiling...")
        self._set_status("RUNNING", self._t['warning'])
        self._sb_msg.setText("Compiling...")
        self.compilation_start_time = time.time()
        self.elapsed_timer.start()

        self.compiler_thread = QThread()
        self.compiler_worker = CompilerWorker(cmd)
        self.compiler_worker.moveToThread(self.compiler_thread)

        self.compiler_thread.started.connect(self.compiler_worker.run)
        self.compiler_worker.finished.connect(self._compile_done)
        self.compiler_worker.progress_update.connect(self._log)

        self.compiler_worker.finished.connect(self.compiler_thread.quit)
        self.compiler_thread.finished.connect(self.compiler_thread.deleteLater)
        self.compiler_worker.finished.connect(self.compiler_worker.deleteLater)
        # Cleanup referensi setelah thread benar-benar selesai
        self.compiler_thread.finished.connect(self._cleanup_compiler_refs)

        self.compiler_thread.start()

    # ── Linux build-tool preflight check ─────────────────
    #
    # Nuitka di Windows auto-download MinGW64 + ccache kalau belum ada.
    # Di Linux TIDAK ada auto-download sama sekali — gcc/g++ dan patchelf
    # wajib sudah terpasang lewat package manager distro. Tanpa cek ini,
    # user Linux baru tahu pas compile langsung FATAL error.

    def _suggest_linux_install_cmd(self):
        distro_id, id_like = "", ""
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro_id = line.split("=", 1)[1].strip().strip('"').lower()
                    elif line.startswith("ID_LIKE="):
                        id_like = line.split("=", 1)[1].strip().strip('"').lower()
        except Exception:
            pass
        combined = f"{distro_id} {id_like}"

        if any(x in combined for x in ("debian", "ubuntu")):
            return "sudo apt install build-essential patchelf"
        if any(x in combined for x in ("fedora", "rhel", "centos")):
            return "sudo dnf install gcc gcc-c++ patchelf"
        if "arch" in combined:
            return "sudo pacman -S base-devel patchelf"
        if any(x in combined for x in ("opensuse", "suse")):
            return "sudo zypper install gcc gcc-c++ patchelf"
        if "alpine" in combined:
            return "sudo apk add build-base patchelf"
        return "install gcc, g++, and patchelf using your distro's package manager"

    def _check_linux_build_deps(self):
        """Return True kalau boleh lanjut compile, False kalau user membatalkan."""
        if not IS_LINUX:
            return True
        if getattr(self, "_linux_deps_ok", False):
            return True  # sudah pernah dicek/di-acknowledge di sesi ini

        missing = []
        if not (shutil.which("gcc") or shutil.which("cc") or shutil.which("clang")):
            missing.append("C compiler (gcc / clang)")
        if not shutil.which("patchelf"):
            missing.append("patchelf")

        if not missing:
            self._linux_deps_ok = True
            return True

        missing_str = "\n".join(f"  •  {m}" for m in missing)
        install_cmd = self._suggest_linux_install_cmd()
        text = (
            "Beberapa tool yang dibutuhkan Nuitka untuk compile di Linux belum terdeteksi:\n\n"
            f"{missing_str}\n\n"
            "Nuitka TIDAK auto-download tool ini di Linux (beda dengan Windows yang "
            "auto-download MinGW64 + ccache). Install dulu dengan:\n\n"
            f"  {install_cmd}\n\n"
            "Lanjutkan compile sekarang? (kemungkinan besar akan gagal dengan FATAL error)"
        )
        reply = QMessageBox.warning(
            self, "Build Tools Belum Lengkap (Linux)", text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._linux_deps_ok = True  # jangan tanya lagi di sesi berjalan ini
            return True
        return False

    def _cleanup_compiler_refs(self):
        self.compiler_thread = None
        self.compiler_worker = None

    def _compile_done(self, result):
        self.elapsed_timer.stop(); self._tick_elapsed()
        # Cek sukses dengan toleran terhadap string — sama seperti versi yang bekerja
        if "SUCCESSFUL" in result.upper():
            self._log(f"<font color='{self._t['success']}'> ✔ SUCCESSFUL</font>")
            self._set_status("SUCCESS", self._t['success'])
            self._do_asset_copy()
        else:
            code = result.split(":", 1)[1] if ":" in result else result
            self._log(f"<font color='{self._t['danger']}'> ✖ FAILED: {code}</font>")
            self._set_status("FAILED", self._t['danger'])
            self._set_btn_state(True)
            if self.is_batch_running:
                QTimer.singleShot(1000, self.batch_step_finished.emit)

    def _do_asset_copy(self):
        if not self.multimedia_check.isChecked() or self.onefile_check.isChecked():
            self._do_zip(); return
        script = self.script_edit.text().strip()
        if not script: self._do_zip(); return
        base = self.output_edit.text().strip() or os.path.dirname(script)
        name = os.path.splitext(os.path.basename(script))[0]
        dst = os.path.join(base, f"{name}.dist", "PySide6")
        src = os.path.join("assets", "PySide6")
        if not os.path.isdir(src):
            self._log(f"<font color='{self._t['warning']}'> ⚠ Assets folder tidak ditemukan: {src} — skip multimedia plugin</font>")
            self._do_zip(); return

        self._log(f"<font color='{self._t['text2']}'> --- Starting Multimedia Plugin Task (Async) ---</font>")
        self.asset_thread = QThread()
        self.asset_worker = AssetCopyWorker(src, dst)
        self.asset_worker.moveToThread(self.asset_thread)
        self.asset_worker.finished.connect(self._asset_copy_done)
        self.asset_worker.finished.connect(self.asset_thread.quit)
        self.asset_thread.finished.connect(self.asset_thread.deleteLater)
        self.asset_thread.started.connect(self.asset_worker.run)
        self.asset_thread.start()

    def _asset_copy_done(self, result):
        if result == "ASSET_COPY_SUCCESS":
            self._log(f"<font color='{self._t['success']}'> ✔ Multimedia assets copied</font>")
        else:
            self._log(f"<font color='{self._t['danger']}'> ✖ Asset copy failed: {result}</font>")
        self.asset_worker = None
        self._do_zip()

    def _do_zip(self):
        if not self.deploy_zip_check.isChecked():
            self._pipeline_done(); return
        script = self.script_edit.text().strip()
        if not script: self._pipeline_done(); return

        base = self.output_edit.text().strip() or os.path.dirname(script)
        name = os.path.splitext(os.path.basename(script))[0]
        is_onefile = self.onefile_check.isChecked()

        # Cari output yang dihasilkan nuitka
        if is_onefile:
            ext = ".exe" if IS_WINDOWS else ""
            candidates = [
                os.path.join(base, f"{name}{ext}"),
                os.path.join(base, f"{name}.dist", f"{name}{ext}"),
            ]
        else:
            candidates = [
                os.path.join(base, f"{name}.dist"),
                os.path.join(base, name),
            ]

        src = next((c for c in candidates if os.path.exists(c)), None)
        if not src:
            self._log(f"<font color='{self._t['danger']}'> ✖ Deploy ZIP: output tidak ditemukan di {base}  (dicari: {[os.path.basename(c) for c in candidates]})</font>")
            self._pipeline_done(); return

        zip_path = src + ".zip"
        self._log(f"<font color='{self._t['text2']}'> --- Starting Deployment Task (Async) ---</font>")

        self.zip_thread = QThread()
        self.zip_worker = ZipWorker(src, zip_path, is_onefile)
        self.zip_worker.moveToThread(self.zip_thread)
        self.zip_worker.progress_update.connect(self._log)
        self.zip_worker.finished.connect(self._zip_done)
        self.zip_worker.finished.connect(self.zip_thread.quit)
        self.zip_thread.finished.connect(self.zip_thread.deleteLater)
        self.zip_thread.started.connect(self.zip_worker.run)
        self.zip_thread.start()

    def _zip_done(self, result):
        if result.startswith("ZIP_SUCCESS"):
            zip_path = result.split(":", 1)[1] if ":" in result else ""
            self._log(f"<font color='{self._t['success']}'> ✔ Archive created: {os.path.basename(zip_path)}</font>")
        else:
            self._log(f"<font color='{self._t['danger']}'> ✖ ZIP failed: {result}</font>")
        self.zip_worker = None
        self._pipeline_done()

    def _pipeline_done(self):
        self._set_btn_state(True)
        self._sb_msg.setText("Done")

        if self.is_batch_running:
            self._log(f"<font color='cyan'> --- Batch Item Finished. Moving to next... ---</font>")
            # Gunakan QTimer agar stack frame selesai dulu sebelum lanjut ke item berikutnya
            QTimer.singleShot(1000, self.batch_step_finished.emit)
            return

        self._log(f"<font color='{self._t['success']}'> All tasks complete.</font>")
        # Cek shutdown: prioritaskan batch_shutdown_mode, fallback ke checkbox per-script
        if self.batch_shutdown_mode or self.shutdown_check.isChecked():
            self._shutdown()

    def _shutdown(self):
        self._log(f"<font color='{self._t['danger']}'><b> SHUTTING DOWN...</b></font>")
        QApplication.processEvents()
        if IS_WINDOWS:
            os.system("shutdown /s /f /t 1")
        elif IS_LINUX:
            # Butuh privilege poweroff (biasanya OK via systemd/polkit tanpa sudo password
            # pada banyak distro desktop). Fallback ke shutdown klasik jika systemctl gagal.
            if os.system("systemctl poweroff") != 0:
                os.system("shutdown -h now")

    # ── Command builder ───────────────────────────────────

    def _find_python(self) -> str:
        """
        Resolve the correct Python executable to invoke Nuitka.
        Selalu log hasilnya ke output agar mudah di-debug.
        """
        self._log(f"<font color='{self._t['text4']}'> [DEBUG] sys.executable = {sys.executable}</font>")
        self._log(f"<font color='{self._t['text4']}'> [DEBUG] frozen={getattr(sys,'frozen',False)}, __compiled__={getattr(sys,'__compiled__',False)}</font>")

        # 1. User override selalu menang
        user = self.python_exe_edit.text().strip()
        if user:
            if os.path.isfile(user):
                self._log(f"<font color='{self._t['success']}'> [DEBUG] Python (user override): {user}</font>")
                return user
            else:
                self._log(f"<font color='{self._t['danger']}'> [DEBUG] User-specified Python tidak ditemukan: {user}</font>")

        # 2. Frozen/compiled binary — sys.executable adalah exe kita sendiri, bukan python
        is_frozen = getattr(sys, 'frozen', False) or getattr(sys, '__compiled__', False)
        if is_frozen:
            for candidate in ("python.exe", "python3.exe", "python"):
                found = shutil.which(candidate)
                if found:
                    self._log(f"<font color='{self._t['success']}'> [DEBUG] Python (PATH, frozen): {found}</font>")
                    return found
            # Fallback: cek folder yang sama dengan exe kita
            exe_dir = os.path.dirname(sys.executable)
            for candidate in ("python.exe", "python3.exe"):
                p = os.path.join(exe_dir, candidate)
                if os.path.isfile(p):
                    self._log(f"<font color='{self._t['success']}'> [DEBUG] Python (exe dir): {p}</font>")
                    return p
            QMessageBox.critical(
                self, "Python Not Found",
                "Tidak dapat menemukan Python interpreter di PATH.\n\n"
                "Silakan set path manual di:\nBuild Options → Python Exe"
            )
            return ""

        # 3. Berjalan sebagai .py script biasa
        # Validasi dulu — sys.executable harus benar-benar python, bukan exe lain
        exe = sys.executable
        if os.path.isfile(exe):
            # Double-check: pastikan ini benar python, bukan exe lain yang mengandung nama lain
            exe_lower = os.path.basename(exe).lower()
            if "python" in exe_lower:
                self._log(f"<font color='{self._t['success']}'> [DEBUG] Python (sys.executable): {exe}</font>")
                return exe
            else:
                self._log(f"<font color='{self._t['danger']}'> [DEBUG] sys.executable bukan python: {exe} — fallback ke PATH</font>")

        # 4. Fallback universal — cari "python" di PATH
        for candidate in ("python.exe", "python3.exe", "python"):
            found = shutil.which(candidate)
            if found:
                self._log(f"<font color='{self._t['success']}'> [DEBUG] Python (fallback PATH): {found}</font>")
                return found

        self._log(f"<font color='{self._t['danger']}'> [DEBUG] Python tidak ditemukan sama sekali!</font>")
        QMessageBox.critical(
            self, "Python Not Found",
            "Tidak dapat menemukan Python interpreter.\n\n"
            "Silakan set path manual di:\nBuild Options → Python Exe"
        )
        return ""

    def _build_cmd(self):
        script = self.script_edit.text().strip()
        if not script:
            QMessageBox.warning(self, "Missing Script", "Please select a Python script.")
            return None

        python = self._find_python()
        if not python:
            return None

        # -u = unbuffered stdout — WAJIB agar output realtime, tidak nunggu buffer penuh
        cmd = [f'"{python}"', "-u", "-m", "nuitka", "--standalone"]

        if self.onefile_check.isChecked(): cmd.append("--onefile")
        if IS_WINDOWS and self.disable_console_check.isChecked():
            cmd.append("--windows-disable-console")

        lto = self.lto_combo.currentData()
        if lto and lto != "no": cmd.append(f"--lto={lto}")

        if self.antibloat_check.isChecked():
            cmd += ["--enable-plugin=anti-bloat",
                    "--noinclude-pytest-mode=nofollow",
                    "--noinclude-setuptools-mode=nofollow",
                    "--noinclude-unittest-mode=nofollow"]

        qt = self._detect_qt(script)
        if qt: cmd.append(f"--enable-plugin={qt}")

        out = self.output_edit.text().strip()
        if out: cmd.append(f'--output-dir="{out}"')

        fname = self.output_filename_edit.text().strip()
        if fname: cmd.append(f'--output-filename="{fname}"')

        ico = self.icon_edit.text().strip()
        if ico:
            if IS_WINDOWS:
                cmd.append(f'--windows-icon-from-ico="{ico}"')
            else:
                # Nuitka's Linux icon flag (used for desktop/AppImage integration)
                cmd.append(f'--linux-icon="{ico}"')

        if IS_WINDOWS:
            msvc = self.msvc_combo.currentData()
            if msvc and msvc != "none": cmd.append(f"--msvc={msvc}")

        opt = self.opt_combo.currentData()
        if opt == "1": cmd.append("--python-flag=optimize")
        elif opt == "2": cmd += ["--python-flag=optimize", "--python-flag=no_docstrings"]

        meta = {
            "product-name":    self.product_name_edit.text().strip(),
            "product-version": self.product_version_edit.text().strip(),
            "file-version":    self.file_version_edit.text().strip(),
            "file-description":self.file_description_edit.text().strip(),
            "copyright":       self.copyright_edit.text().strip(),
            "trademarks":      self.trademarks_edit.text().strip(),
        }
        for k, v in meta.items():
            if v: cmd.append(f'--{k}="{v}"')

        for i in range(self.file_list_widget.count()):
            s = self.file_list_widget.item(i).text()
            cmd.append(f'--include-data-file="{s}"="{os.path.basename(s)}"')
        for i in range(self.folder_list_widget.count()):
            s = self.folder_list_widget.item(i).text()
            cmd.append(f'--include-data-dir="{s}"="{os.path.basename(s)}"')
        for i in range(self.module_list_widget.count()):
            cmd.append(f'--include-module={self.module_list_widget.item(i).text()}')

        if self.follow_imports_check.isChecked(): cmd.append("--follow-imports")
        if self.show_scons_check.isChecked(): cmd.append("--show-scons")
        if self.assume_yes_check.isChecked(): cmd.append("--assume-yes-for-downloads")
        if self.remove_output_check.isChecked(): cmd.append("--remove-output")
        if self.no_pyc_check.isChecked(): cmd.append("--no-pyi-file")

        cmd += ["--show-progress", "--show-memory", f"--jobs={self.jobs_combo.currentText()}"]

        extra = self.extra_flags_edit.text().strip()
        if extra: cmd.extend(extra.split())

        cmd.append(f'"{script}"')
        return " ".join(cmd)

    def _detect_qt(self, path):
        if not os.path.exists(path): return None
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read(8192)
            for k, v in [("PySide6","pyside6"),("PyQt6","pyqt6"),
                          ("PyQt5","pyqt5"),("PySide2","pyside2")]:
                if k in c: return v
        except Exception: pass
        return None

    # ── Profile ───────────────────────────────────────────

    def _collect(self):
        return {
            "script_path":       self.script_edit.text(),
            "output_dir":        self.output_edit.text(),
            "icon_path":         self.icon_edit.text(),
            "python_exe":        self.python_exe_edit.text(),
            "onefile":           self.onefile_check.isChecked(),
            "disable_console":   self.disable_console_check.isChecked(),
            "antibloat":         self.antibloat_check.isChecked(),
            "lto":               self.lto_combo.currentData(),
            "deploy_zip":        self.deploy_zip_check.isChecked(),
            "multimedia_plugin": self.multimedia_check.isChecked(),
            "shutdown":          self.shutdown_check.isChecked(),
            "jobs":              self.jobs_combo.currentText(),
            "msvc":              self.msvc_combo.currentData(),
            "python_opt":        self.opt_combo.currentData(),
            "output_filename":   self.output_filename_edit.text(),
            "follow_imports":    self.follow_imports_check.isChecked(),
            "show_scons":        self.show_scons_check.isChecked(),
            "assume_yes":        self.assume_yes_check.isChecked(),
            "remove_output":     self.remove_output_check.isChecked(),
            "no_pyc":            self.no_pyc_check.isChecked(),
            "extra_flags":       self.extra_flags_edit.text(),
            "product_name":      self.product_name_edit.text(),
            "product_version":   self.product_version_edit.text(),
            "file_version":      self.file_version_edit.text(),
            "file_description":  self.file_description_edit.text(),
            "copyright":         self.copyright_edit.text(),
            "trademarks":        self.trademarks_edit.text(),
            "included_files":    [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())],
            "included_folders":  [self.folder_list_widget.item(i).text() for i in range(self.folder_list_widget.count())],
            "included_modules":  [self.module_list_widget.item(i).text() for i in range(self.module_list_widget.count())],
        }

    def _apply_data(self, d):
        self.script_edit.setText(d.get("script_path",""))
        self.output_edit.setText(d.get("output_dir",""))
        self.icon_edit.setText(d.get("icon_path",""))
        self.python_exe_edit.setText(d.get("python_exe",""))
        self.onefile_check.setChecked(d.get("onefile",False))
        self.disable_console_check.setChecked(d.get("disable_console",False))
        self.antibloat_check.setChecked(d.get("antibloat",False))
        self.deploy_zip_check.setChecked(d.get("deploy_zip",False))
        self.multimedia_check.setChecked(d.get("multimedia_plugin",False))
        self.shutdown_check.setChecked(d.get("shutdown",False))
        self.follow_imports_check.setChecked(d.get("follow_imports",False))
        self.show_scons_check.setChecked(d.get("show_scons",False))
        self.assume_yes_check.setChecked(d.get("assume_yes",False))
        self.remove_output_check.setChecked(d.get("remove_output",True))
        self.no_pyc_check.setChecked(d.get("no_pyc",False))
        self.output_filename_edit.setText(d.get("output_filename",""))
        self.extra_flags_edit.setText(d.get("extra_flags",""))
        self.product_name_edit.setText(d.get("product_name",""))
        self.product_version_edit.setText(d.get("product_version",""))
        self.file_version_edit.setText(d.get("file_version",""))
        self.file_description_edit.setText(d.get("file_description",""))
        self.copyright_edit.setText(d.get("copyright",""))
        self.trademarks_edit.setText(d.get("trademarks",""))
        def _sc(combo, val):
            for i in range(combo.count()):
                if combo.itemData(i) == val: combo.setCurrentIndex(i); return
        _sc(self.lto_combo, d.get("lto","no"))
        # Handle nilai lama "latest" dari profile yang disimpan versi sebelumnya
        msvc_val = d.get("msvc", "")
        if msvc_val == "latest": msvc_val = ""
        _sc(self.msvc_combo, msvc_val)
        _sc(self.opt_combo, d.get("python_opt",""))
        idx = self.jobs_combo.findText(d.get("jobs","4"))
        if idx >= 0: self.jobs_combo.setCurrentIndex(idx)
        self.file_list_widget.clear(); self.file_list_widget.addItems(d.get("included_files",[]))
        self.folder_list_widget.clear(); self.folder_list_widget.addItems(d.get("included_folders",[]))
        self.module_list_widget.clear(); self.module_list_widget.addItems(d.get("included_modules",[]))

    def load_profile_direct(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._apply_data(data)
            self.current_profile_path = path
            self.setWindowTitle(f"Nuitka Compiler Pro  —  {os.path.basename(path)}")
            self._add_recent(path)
            self._log(f"<font color='{self._t['success']}'> ✔ Loaded: {os.path.basename(path)}</font>")
            return True
        except Exception as e:
            self._log(f"<font color='{self._t['danger']}'> ✖ Load failed: {e}</font>")
            return False

    def save_profile(self):
        if self.current_profile_path: self._do_save(self.current_profile_path)
        else: self.save_profile_as()

    def save_profile_as(self):
        last = self.settings.value("last_profile_dir","")
        path, _ = QFileDialog.getSaveFileName(self,"Save Profile",last,"Nuitka Profile (*.ncp)")
        if path:
            self.settings.setValue("last_profile_dir", os.path.dirname(path))
            self._do_save(path)

    def _do_save(self, path):
        try:
            with open(path,'w',encoding='utf-8') as f:
                json.dump(self._collect(), f, indent=4, ensure_ascii=False)
            self.current_profile_path = path
            self.setWindowTitle(f"Nuitka Compiler Pro  —  {os.path.basename(path)}")
            self._add_recent(path)
            self._log(f"<font color='{self._t['success']}'> ✔ Saved: {os.path.basename(path)}</font>")
        except Exception as e:
            QMessageBox.critical(self,"Save Error",str(e))

    def load_profile(self):
        last = self.settings.value("last_profile_dir","")
        path, _ = QFileDialog.getOpenFileName(self,"Load Profile",last,"Nuitka Profile (*.ncp)")
        if path:
            self.settings.setValue("last_profile_dir", os.path.dirname(path))
            self.load_profile_direct(path)

    # ── Reset ─────────────────────────────────────────────

    def _reset_internal(self):
        for e in [self.script_edit, self.output_edit, self.icon_edit,
                  self.python_exe_edit, self.output_filename_edit, self.extra_flags_edit,
                  self.product_name_edit, self.product_version_edit, self.file_version_edit,
                  self.file_description_edit, self.copyright_edit, self.trademarks_edit]:
            e.clear()
        for cb in [self.onefile_check, self.disable_console_check, self.antibloat_check,
                   self.deploy_zip_check, self.multimedia_check, self.shutdown_check,
                   self.follow_imports_check, self.show_scons_check,
                   self.assume_yes_check, self.no_pyc_check]:
            cb.setChecked(False)
        self.remove_output_check.setChecked(True)
        self.lto_combo.setCurrentIndex(0)
        self.msvc_combo.setCurrentIndex(0)
        self.opt_combo.setCurrentIndex(0)
        idx = self.jobs_combo.findText("4")
        if idx >= 0: self.jobs_combo.setCurrentIndex(idx)
        self.file_list_widget.clear()
        self.folder_list_widget.clear()
        self.module_list_widget.clear()

    def reset_ui(self):
        if QMessageBox.question(
            self,"Reset","Reset all settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self._reset_internal()
            self.clear_log()
            self.current_profile_path = None
            self.setWindowTitle("Nuitka Compiler Pro")
            self._set_status("IDLE", self._t['text4'])

    # ── Misc ──────────────────────────────────────────────

    def _set_status(self, text, color):
        self.status_indicator.setText(f"●  {text}")
        self.status_indicator.setStyleSheet(
            f"color:{color};font-size:10px;font-weight:700;letter-spacing:1px;"
        )

    def _set_btn_state(self, enabled, text=None):
        self.compile_btn.setEnabled(enabled)
        self.compile_btn2.setEnabled(enabled)
        if text:
            self.compile_btn.setText(text)
            self.compile_btn2.setText(text)
        else:
            self.compile_btn.setText("▶  Compile")
            self.compile_btn2.setText("▶  Start Compilation")

    def _log(self, text):
        self.log_output.append(text)
        sb = self.log_output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_log(self):
        self.log_output.clear()

    def _tick_elapsed(self):
        e = int(time.time() - self.compilation_start_time)
        self.elapsed_label.setText(f"{e//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}")

    def preview_command(self):
        cmd = self._build_cmd()
        if cmd:
            self._log(f"<font color='{self._t['accent_light']}'>{'─'*48}</font>")
            self._log(f"<font color='{self._t['text4']}'>{cmd}</font>")
            self._log(f"<font color='{self._t['accent_light']}'>{'─'*48}</font>")

    def clear_nuitka_cache(self):
        if IS_WINDOWS:
            local = os.getenv('LOCALAPPDATA')
            if not local: return
            base = os.path.join(local, 'Nuitka', 'Nuitka', 'Cache')
        else:
            # Linux: XDG cache dir, default ~/.cache
            xdg_cache = os.getenv('XDG_CACHE_HOME') or os.path.expanduser('~/.cache')
            base = os.path.join(xdg_cache, 'Nuitka', 'Nuitka', 'Cache')
        paths = [os.path.join(base,'clcache'), os.path.join(base,'module-cache')]
        if QMessageBox.question(
            self,"Clear Cache","Delete Nuitka compilation cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes: return
        for p in paths:
            if os.path.exists(p):
                try: shutil.rmtree(p); self._log(f"<font color='{self._t['success']}'> ✔ {p}</font>")
                except Exception as ex: self._log(f"<font color='{self._t['danger']}'> ✖ {ex}</font>")

    def reload_application(self):
        if self.is_batch_running:
            QMessageBox.warning(self, "Busy", "Cannot reload during batch."); return
        self._save_settings()
        # When frozen, sys.executable IS our .exe — restart it directly
        QProcess.startDetached(sys.executable, sys.argv)
        self.close()

    # ── Settings ─────────────────────────────────────────

    def _load_settings(self):
        try:
            self.resize(self.settings.value("window/size", QSize(1240, 800)))
            self.move(self.settings.value("window/pos", QPoint(60, 50)))
            geo = self.settings.value("window/geometry")
            if geo: self.restoreGeometry(geo)
            state = self.settings.value("window/state")
            if state: self.restoreState(state)
        except Exception:
            pass

    def _save_settings(self):
        self.settings.setValue("window/size",     self.size())
        self.settings.setValue("window/pos",      self.pos())
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state",    self.saveState())
        self.settings.setValue("app/theme",       self._theme_name)

    def closeEvent(self, event: QCloseEvent):
        if self.is_batch_running:
            r = QMessageBox.question(
                self,"Batch Running","Exit during batch?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if r == QMessageBox.StandardButton.No:
                event.ignore(); return
        self._save_settings()
        super().closeEvent(event)


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")           # Prevent OS theme inheritance
    app.setPalette(QPalette())       # Clear default OS palette
    app.setApplicationName("Nuitka Compiler Pro")
    app.setApplicationVersion("7.1.0")
    app.setOrganizationName("Danx")

    window = NuitkaGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
