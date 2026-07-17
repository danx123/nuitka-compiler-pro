# nuitka_menu.py
import sys
import os
import ctypes
from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import QSettings

if sys.platform == 'win32':
    import winreg


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class MenuHandler:
    """
    Builds the application menu bar using QMainWindow.menuBar().
    No hardcoded stylesheet — inherits from global QSS.
    """

    def __init__(self, main_window):
        self.win = main_window
        self.settings = QSettings("Danx", "NuitkaCompilerPro")
        self._recent_menu = None
        self.MAX_RECENT = 10

        mb = self.win.menuBar()
        self._build_file_menu(mb)
        self._build_tools_menu(mb)
        self._build_view_menu(mb)
        self._build_help_menu(mb)

    # ── File Menu ─────────────────────────────────────────

    def _build_file_menu(self, mb):
        m = mb.addMenu("&File")

        self._act(m, "New / Reset",       "Ctrl+N",       self.win.reset_ui,          "Reset all settings")
        m.addSeparator()
        self._act(m, "Save Profile",      "Ctrl+S",       self.win.save_profile,      "Save configuration to .ncp")
        self._act(m, "Save Profile As…",  "Ctrl+Shift+S", self.win.save_profile_as,   "Save to a new .ncp file")
        self._act(m, "Load Profile…",     "Ctrl+O",       self.win.load_profile,      "Load configuration from .ncp")
        m.addSeparator()
        self._act(m, "Profile Editor (JSON)", "Ctrl+E",   self.win.open_profile_editor, "Raw JSON profile editor")
        m.addSeparator()

        # Recent Files submenu
        self._recent_menu = QMenu("Recent Files", self.win)
        m.addMenu(self._recent_menu)
        self.refresh_recent_menu()

        self._act(m, "Clear Recent Files", "",            self._clear_recent,         "Clear recent files list")
        m.addSeparator()
        self._act(m, "Exit",              "Alt+F4",       self.win.close,             "Exit application")

    # ── Tools Menu ────────────────────────────────────────

    def _build_tools_menu(self, mb):
        m = mb.addMenu("&Tools")

        self._act(m, "Preview Command",       "Ctrl+P", self.win.preview_command,     "Preview Nuitka command")
        self._act(m, "Clear Nuitka Cache",    "",       self.win.clear_nuitka_cache,  "Delete Nuitka cache")
        m.addSeparator()
        self._act(m, "Batch Manager…",        "Ctrl+B", self.win.open_batch_dialog,   "Open batch compilation manager")
        m.addSeparator()
        self._act(m, "Reload Application",    "Ctrl+R", self.win.reload_application,  "Restart the app")

    # ── View Menu ─────────────────────────────────────────

    def _build_view_menu(self, mb):
        m = mb.addMenu("&View")

        # Log dock toggle
        a_log = QAction("Show Log Panel", self.win)
        a_log.setCheckable(True)
        a_log.setChecked(True)
        a_log.setShortcut("Ctrl+L")
        a_log.triggered.connect(lambda checked: self.win._log_dock.setVisible(checked))
        self.win._log_dock.visibilityChanged.connect(a_log.setChecked)
        m.addAction(a_log)

        m.addSeparator()

        # Theme
        a_theme = QAction("Light Theme", self.win)
        a_theme.setCheckable(True)
        a_theme.setChecked(self.win._theme_name == "light")
        a_theme.setShortcut("Ctrl+T")
        a_theme.triggered.connect(self.win._toggle_theme)
        # Keep in sync with toolbar toggle
        self.win._theme_action.toggled.connect(a_theme.setChecked)
        a_theme.toggled.connect(self.win._theme_action.setChecked)
        m.addAction(a_theme)
        self._view_theme_action = a_theme

        m.addSeparator()
        self._act(m, "Reset Layout", "", self._reset_layout, "Restore default dock layout")

    # ── Help Menu ─────────────────────────────────────────

    def _build_help_menu(self, mb):
        m = mb.addMenu("&Help")

        self._act(m, "Help Contents", "F1", self._show_help, "Show help")
        m.addSeparator()
        self._act(m, "Register .ncp File Association", "", self._register_ncp,
                  "Associate .ncp files with this app (Windows)")
        m.addSeparator()
        self._act(m, "About", "", self._show_about, "About Nuitka Compiler Pro")

    # ── Recent Files ──────────────────────────────────────

    def add_recent_file(self, path):
        """Add a file to recent files and refresh the menu."""
        if not path or not os.path.exists(path):
            return
        path = os.path.normpath(path)
        recent = self._get_recent()
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        recent = recent[:self.MAX_RECENT]
        self.settings.setValue("recent_files", recent)
        self.refresh_recent_menu()

    def _get_recent(self):
        r = self.settings.value("recent_files", [])
        if isinstance(r, str):
            r = [r] if r else []
        valid = [f for f in r if os.path.exists(f)]
        if len(valid) != len(r):
            self.settings.setValue("recent_files", valid)
        return valid

    def refresh_recent_menu(self):
        if not self._recent_menu:
            return
        self._recent_menu.clear()
        recent = self._get_recent()
        if not recent:
            a = QAction("(No Recent Files)", self.win)
            a.setEnabled(False)
            self._recent_menu.addAction(a)
            return
        for i, fp in enumerate(recent):
            name = os.path.basename(fp)
            label = f"&{i+1}.  {name}" if i < 9 else name
            a = QAction(label, self.win)
            if i < 9:
                a.setShortcut(QKeySequence(f"Ctrl+{i+1}"))
            a.setStatusTip(fp)
            a.setToolTip(fp)
            a.triggered.connect(lambda chk=False, p=fp: self._load_recent(p))
            self._recent_menu.addAction(a)

    def _load_recent(self, path):
        if os.path.exists(path):
            self.win.load_profile_direct(path)
            self.add_recent_file(path)
        else:
            QMessageBox.warning(self.win, "File Not Found",
                                f"The file no longer exists:\n{path}")
            recent = self._get_recent()
            if path in recent:
                recent.remove(path)
                self.settings.setValue("recent_files", recent)
                self.refresh_recent_menu()

    def _clear_recent(self):
        r = QMessageBox.question(
            self.win, "Clear Recent Files",
            "Clear all recent files from history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if r == QMessageBox.StandardButton.Yes:
            self.settings.setValue("recent_files", [])
            self.refresh_recent_menu()

    # ── View helpers ──────────────────────────────────────

    def _reset_layout(self):
        """Reset dock positions to default."""
        self.win._log_dock.setFloating(False)
        from PySide6.QtCore import Qt
        self.win.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.win._log_dock)
        self.win._log_dock.setVisible(True)

    # ── Help / About / Registry ───────────────────────────

    def _show_help(self):
        html = """
<h3 style='color:#3B82F6;'>Nuitka Compiler Pro — Help</h3>
<p><b>Quick Start:</b></p>
<ol>
  <li>Select your Python script (.py) in <b>Input / Output</b>.</li>
  <li>Configure options in <b>Build Options</b>, <b>Advanced</b>, and <b>Metadata</b> tabs.</li>
  <li>Click <b>Start Compilation</b>.</li>
</ol>
<p><b>Key Shortcuts:</b></p>
<table>
  <tr><td><b>Ctrl+S / O</b></td><td>&nbsp;Save / Load profile</td></tr>
  <tr><td><b>Ctrl+E</b></td><td>&nbsp;Raw JSON editor</td></tr>
  <tr><td><b>Ctrl+B</b></td><td>&nbsp;Batch manager</td></tr>
  <tr><td><b>Ctrl+P</b></td><td>&nbsp;Preview command</td></tr>
  <tr><td><b>Ctrl+T</b></td><td>&nbsp;Toggle light/dark</td></tr>
  <tr><td><b>Ctrl+L</b></td><td>&nbsp;Toggle log panel</td></tr>
  <tr><td><b>Ctrl+1–9</b></td><td>&nbsp;Open recent file</td></tr>
  <tr><td><b>F1</b></td><td>&nbsp;This help screen</td></tr>
</table>
<p><b>Options explained:</b></p>
<ul>
  <li><b>LTO</b>: Link-Time Optimization — smaller binary, slower build.</li>
  <li><b>Anti-Bloat</b>: Strips pytest/setuptools. May break some imports.</li>
  <li><b>Multimedia Plugin</b>: Copies PySide6 DLLs for One-Directory mode.</li>
  <li><b>Deploy .zip</b>: LZMA-compressed archive of build output.</li>
  <li><b>Batch Mode</b>: Sequential compilation of multiple .ncp profiles with cooldown.</li>
</ul>
"""
        QMessageBox.information(self.win, "Help — Nuitka Compiler Pro", html)

    def _show_about(self):
        html = """
<div style='text-align:center;'>
  <h3 style='color:#3B82F6;'>Nuitka Compiler Pro</h3>
  <p style='color:#64748B;'>Version 7.5.0</p>
  <hr>
  <p>Professional GUI frontend for the Nuitka Python compiler.<br>
  Built for production build workflows.</p>
  <p style='color:#64748B;'>Created by <b>Danx — Macan Angkasa</b></p>
</div>
"""
        QMessageBox.about(self.win, "About — Nuitka Compiler Pro", html)

    def _register_ncp(self):
        if sys.platform != 'win32':
            QMessageBox.warning(self.win, "Windows Only",
                                "File association is only available on Windows.")
            return
        ext = ".ncp"
        file_type = "NuitkaCompilerPro.Profile"
        exe = sys.executable
        if not getattr(sys, 'frozen', False):
            cmd = f'"{exe}" "{os.path.abspath(sys.argv[0])}" "%1"'
        else:
            cmd = f'"{exe}" "%1"'
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  f"Software\\Classes\\{ext}") as k:
                winreg.SetValue(k, "", winreg.REG_SZ, file_type)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  f"Software\\Classes\\{file_type}") as k:
                winreg.SetValue(k, "", winreg.REG_SZ, "Nuitka Compiler Profile")
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  f"Software\\Classes\\{file_type}\\DefaultIcon") as k:
                winreg.SetValue(k, "", winreg.REG_SZ, f'"{exe}",0')
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  f"Software\\Classes\\{file_type}\\shell\\open\\command") as k:
                winreg.SetValue(k, "", winreg.REG_SZ, cmd)
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            QMessageBox.information(self.win, "Success",
                                    f"Registered {ext} file association successfully!")
        except Exception as e:
            QMessageBox.critical(self.win, "Registry Error",
                                 f"Failed to register extension:\n{e}")

    # ── Internal helper ───────────────────────────────────

    def _act(self, menu, label, shortcut, fn, tip=""):
        a = QAction(label, self.win)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        if tip:
            a.setStatusTip(tip)
        a.triggered.connect(fn)
        menu.addAction(a)
        return a
