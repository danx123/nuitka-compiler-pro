# nuitka_editor.py
import json
import os
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QMessageBox,
    QFrame, QStatusBar, QWidget
)
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PySide6.QtCore import Qt, QRegularExpression, QTimer


EDITOR_STYLE = """
QDialog {
    background-color: #0F1117;
    color: #E2E8F0;
}
QLabel {
    color: #94A3B8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
}
QLabel[class="filename"] {
    color: #60A5FA;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}
QPushButton {
    background-color: #1E2433;
    border: 1px solid #2D3748;
    border-radius: 5px;
    color: #CBD5E1;
    padding: 7px 14px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
    font-weight: 600;
    min-height: 30px;
}
QPushButton:hover {
    background-color: #252F45;
    border-color: #3B5078;
    color: #F1F5F9;
}
QPushButton[class="primary"] {
    background-color: #1D4ED8;
    border-color: #2563EB;
    color: white;
}
QPushButton[class="primary"]:hover {
    background-color: #2563EB;
}
QPushButton[class="success"] {
    background-color: #166534;
    border-color: #16A34A;
    color: #BBF7D0;
}
QPushButton[class="success"]:hover {
    background-color: #15803D;
}
QTextEdit {
    background-color: #0D1117;
    color: #E2E8F0;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    border: 1px solid #1E2D4A;
    border-radius: 6px;
    padding: 10px;
    selection-background-color: #1E3A6E;
    line-height: 1.5;
}
QStatusBar {
    background-color: #1D4ED8;
    color: white;
    font-size: 11px;
    font-family: 'Segoe UI', sans-serif;
}
"""


class JsonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter dengan tema VS Code Dark+ style untuk JSON."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # Keys (strings before colon)
        key_fmt = QTextCharFormat()
        key_fmt.setForeground(QColor("#9CDCFE"))
        self._rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"\s*:'), key_fmt))

        # String values (strings after colon)
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#CE9178"))
        self._rules.append((QRegularExpression(r':\s*"[^"\\]*(?:\\.[^"\\]*)*"'), str_fmt))

        # Boolean / null
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#569CD6"))
        kw_fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((QRegularExpression(r'\b(true|false|null)\b'), kw_fmt))

        # Numbers
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#B5CEA8"))
        self._rules.append((QRegularExpression(r'(?<!["\w])-?\b\d+(?:\.\d+)?\b'), num_fmt))

        # Brackets & punctuation
        punc_fmt = QTextCharFormat()
        punc_fmt.setForeground(QColor("#FFD700"))
        self._rules.append((QRegularExpression(r'[\[\]{},]'), punc_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class NuitkaProfileEditor(QDialog):
    """Enterprise JSON editor untuk file .ncp dengan syntax highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profile Editor — Nuitka Compiler Pro")
        self.resize(700, 560)
        self.setStyleSheet(EDITOR_STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMaximizeButtonHint)

        self.current_file = None
        self._is_modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Toolbar ---
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #161B27; border-bottom: 1px solid #1E2D3D;")
        toolbar.setFixedHeight(52)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 8, 16, 8)
        toolbar_layout.setSpacing(8)

        badge = QLabel("JSON")
        badge.setStyleSheet(
            "background: #0D3B7F; color: #60A5FA; font-size: 9px; font-weight: 700; "
            "letter-spacing: 1px; padding: 3px 7px; border-radius: 3px; font-family: 'Segoe UI', sans-serif;"
        )
        toolbar_layout.addWidget(badge)

        self.file_label = QLabel("No file loaded  —  open a .ncp profile to begin editing")
        self.file_label.setStyleSheet("color: #475569; font-family: 'Segoe UI', sans-serif; font-size: 12px; margin-left: 8px;")
        toolbar_layout.addWidget(self.file_label)

        self.modified_dot = QLabel("●")
        self.modified_dot.setStyleSheet("color: #F59E0B; font-size: 10px;")
        self.modified_dot.setVisible(False)
        toolbar_layout.addWidget(self.modified_dot)

        toolbar_layout.addStretch()

        format_btn = QPushButton("{ } Format")
        format_btn.setToolTip("Auto-format and pretty-print the JSON")
        format_btn.clicked.connect(self._format_json)
        toolbar_layout.addWidget(format_btn)

        load_btn = QPushButton("📂  Open")
        load_btn.setProperty("class", "primary")
        load_btn.clicked.connect(self.load_file)
        toolbar_layout.addWidget(load_btn)

        save_btn = QPushButton("💾  Save")
        save_btn.setProperty("class", "success")
        save_btn.setStyleSheet(
            "background-color: #166534; border: 1px solid #16A34A; "
            "color: #BBF7D0; padding: 7px 14px; border-radius: 5px; "
            "font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: 600;"
        )
        save_btn.clicked.connect(self.save_file)
        toolbar_layout.addWidget(save_btn)

        layout.addWidget(toolbar)

        # --- Editor Area ---
        editor_container = QWidget()
        editor_container.setStyleSheet("background-color: #0D1117;")
        ec_layout = QVBoxLayout(editor_container)
        ec_layout.setContentsMargins(16, 12, 16, 0)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText('Open a .ncp file to edit its configuration...\n\nJSON keys available:\n  script_path, output_dir, icon_path, onefile, disable_console,\n  antibloat, lto, jobs, deploy_zip, multimedia_plugin, shutdown,\n  product_name, product_version, file_version, file_description, copyright,\n  included_files, included_folders, included_modules, ...')
        self.highlighter = JsonHighlighter(self.editor.document())
        self.editor.textChanged.connect(self._on_text_changed)
        ec_layout.addWidget(self.editor)

        layout.addWidget(editor_container, 1)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            "background-color: #0E1829; color: #475569; border-top: 1px solid #1E2D3D; "
            "font-family: 'Consolas', monospace; font-size: 11px;"
        )
        self.status_bar.showMessage("Ready  —  Open a .ncp file to start editing")
        layout.addWidget(self.status_bar)

        # Cursor position tracking
        self.editor.cursorPositionChanged.connect(self._update_cursor_pos)

    def _on_text_changed(self):
        self._is_modified = True
        self.modified_dot.setVisible(True)
        self._update_cursor_pos()

    def _update_cursor_pos(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        chars = len(self.editor.toPlainText())
        self.status_bar.showMessage(
            f"  Ln {line}, Col {col}     {chars} characters"
        )

    def _format_json(self):
        try:
            raw = self.editor.toPlainText()
            if not raw.strip():
                return
            parsed = json.loads(raw)
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
            self.editor.setText(formatted)
            self.status_bar.showMessage("  ✔  JSON formatted successfully")
        except json.JSONDecodeError as e:
            self.status_bar.showMessage(f"  ✖  JSON syntax error: {e}")

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Profile", "", "Nuitka Profiles (*.ncp)"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.editor.setText(json.dumps(data, indent=4, ensure_ascii=False))
            self.current_file = file_path
            fname = os.path.basename(file_path)
            self.file_label.setText(f"{fname}  ·  {file_path}")
            self.file_label.setStyleSheet("color: #60A5FA; font-family: 'Consolas', monospace; font-size: 12px;")
            self._is_modified = False
            self.modified_dot.setVisible(False)
            self.status_bar.showMessage(f"  Loaded: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load file:\n{e}")

    def save_file(self):
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Profile As", "", "Nuitka Profiles (*.ncp)"
            )
            if not file_path:
                return
            self.current_file = file_path

        try:
            raw = self.editor.toPlainText()
            parsed = json.loads(raw)

            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, indent=4, ensure_ascii=False)

            fname = os.path.basename(self.current_file)
            self.file_label.setText(f"{fname}  ·  {self.current_file}")
            self._is_modified = False
            self.modified_dot.setVisible(False)
            self.status_bar.showMessage(f"  ✔  Saved: {self.current_file}")
            QTimer.singleShot(3000, lambda: self.status_bar.showMessage("  Ready"))

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"Cannot save — syntax error in JSON:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")

    def closeEvent(self, event):
        if self._is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        super().closeEvent(event)
