# nuitka_quickqueue.py
# Hot-plug panel — dibuka/ditutup dengan tombol tilde "~" dari jendela utama.
# Bisa dipakai SAAT batch sedang berjalan: tambah / hapus / urutkan antrean,
# ubah waktu tunggu (cooldown), dan nyalakan/matikan shutdown secara live.
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QFileDialog, QMessageBox, QAbstractItemView,
    QCheckBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, QTimer

from nuitka_batch import ENTERPRISE_STYLE

_LABEL_SS = ("color: #475569; font-size: 9px; font-weight: 700; "
             "letter-spacing: 2px; font-family: 'Segoe UI', sans-serif;")


class QuickQueueDialog(QDialog):
    """Panel non-modal untuk mengelola antrean batch secara live."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self._was_running = False

        self.setWindowTitle("Quick Queue — Nuitka Compiler Pro")
        self.setStyleSheet(ENTERPRISE_STYLE)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setModal(False)
        self.resize(540, 520)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(0)

        # ── Header ──
        head = QHBoxLayout()
        badge = QLabel("LIVE")
        badge.setStyleSheet(
            "background: #047857; color: #A7F3D0; font-size: 9px; font-weight: 700; "
            "letter-spacing: 1.5px; padding: 3px 8px; border-radius: 3px; "
            "font-family: 'Segoe UI', sans-serif;"
        )
        title = QLabel("Quick Queue")
        title.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #F1F5F9; "
            "font-family: 'Segoe UI', sans-serif; margin-left: 10px;"
        )
        hint = QLabel("press ~ to open / close")
        hint.setStyleSheet("color: #475569; font-size: 10px;")
        head.addWidget(badge)
        head.addWidget(title)
        head.addStretch()
        head.addWidget(hint)
        lay.addLayout(head)

        lay.addSpacing(6)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #64748B; font-size: 11px;")
        lay.addWidget(self.status_label)

        lay.addSpacing(14)
        lay.addWidget(self._sep())
        lay.addSpacing(14)

        # ── Queue ──
        q_label = QLabel("QUEUE")
        q_label.setStyleSheet(_LABEL_SS)
        lay.addWidget(q_label)
        lay.addSpacing(8)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list.setMinimumHeight(170)
        lay.addWidget(self.list, 1)
        lay.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(8)
        add_btn = QPushButton("＋  Add Profiles")
        add_btn.setProperty("class", "primary")
        add_btn.clicked.connect(self._add_files)
        del_btn = QPushButton("✕  Remove")
        del_btn.clicked.connect(self._remove_selected)
        up_btn = QPushButton("↑")
        up_btn.setFixedWidth(36)
        up_btn.clicked.connect(lambda: self._move(-1))
        dn_btn = QPushButton("↓")
        dn_btn.setFixedWidth(36)
        dn_btn.clicked.connect(lambda: self._move(+1))
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #475569; font-size: 11px;")
        for w in (add_btn, del_btn, up_btn, dn_btn):
            row.addWidget(w)
        row.addStretch()
        row.addWidget(self.count_label)
        lay.addLayout(row)

        lay.addSpacing(16)
        lay.addWidget(self._sep())
        lay.addSpacing(14)

        # ── Cooldown ──
        c_label = QLabel("COOLDOWN BETWEEN TASKS")
        c_label.setStyleSheet(_LABEL_SS)
        lay.addWidget(c_label)
        lay.addSpacing(8)

        crow = QHBoxLayout()
        self.cool_spin = QSpinBox()
        self.cool_spin.setRange(0, 180)
        self.cool_spin.setValue(5)
        self.cool_spin.setSuffix(" min")
        self.cool_spin.setSpecialValueText("No delay")
        self.cool_spin.setMinimumHeight(34)
        self.cool_spin.setMinimumWidth(130)
        self.cool_spin.setToolTip("Wait time between compilations. Applies to the subsequent interval "
                                  "(the ongoing pause remains unchanged).")
        self.cool_spin.valueChanged.connect(self._cooldown_changed)
        crow.addWidget(self.cool_spin)
        crow.addStretch()
        lay.addLayout(crow)

        lay.addSpacing(14)

        self.shutdown_check = QCheckBox("  Shut down PC after all queues are complete")
        self.shutdown_check.setStyleSheet(
            "color: #FCA5A5; font-weight: 600; font-family: 'Segoe UI', sans-serif;"
        )
        self.shutdown_check.toggled.connect(self._shutdown_toggled)
        lay.addWidget(self.shutdown_check)

        lay.addSpacing(18)

        # ── Actions ──
        act = QHBoxLayout()
        act.setSpacing(10)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        self.start_btn = QPushButton("▶  Start Batch")
        self.start_btn.setFixedHeight(38)
        self.start_btn.setStyleSheet(
            "background-color: #1D4ED8; border: 1px solid #2563EB; color: white; "
            "font-size: 13px; font-weight: 700; border-radius: 6px; padding: 0 20px;"
        )
        self.start_btn.clicked.connect(self._start_batch)
        act.addStretch()
        act.addWidget(close_btn)
        act.addWidget(self.start_btn)
        lay.addLayout(act)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._render)

    # ── helpers ───────────────────────────────────────────

    @staticmethod
    def _sep():
        s = QFrame()
        s.setFrameShape(QFrame.Shape.HLine)
        s.setStyleSheet("background: #1A2540; max-height:1px;")
        return s

    def _running(self):
        return bool(self.win.is_batch_running)

    def _locked(self):
        """Jumlah item di depan yang sudah jalan / selesai (tidak boleh diubah)."""
        return self.win.batch_current_index if self._running() else 0

    def _paths(self):
        if self._running():
            return list(self.win.batch_queue)
        return [self.list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.list.count())]

    def _set_paths(self, paths):
        if self._running():
            self.win.batch_queue[:] = paths      # in-place → langsung dipakai _next_batch
        self._rebuild(paths)

    def _rebuild(self, paths):
        sel = self.list.currentRow()
        self.list.blockSignals(True)
        self.list.clear()
        for p in paths:
            it = QListWidgetItem(os.path.basename(p))
            it.setData(Qt.ItemDataRole.UserRole, p)
            it.setToolTip(p)
            self.list.addItem(it)
        self.list.blockSignals(False)
        if 0 <= sel < self.list.count():
            self.list.setCurrentRow(sel)
        self._decorate()

    def _decorate(self):
        """Beri penanda status per item tanpa membangun ulang list."""
        running = self._running()
        w = self.win
        for i in range(self.list.count()):
            it = self.list.item(i)
            name = os.path.basename(it.data(Qt.ItemDataRole.UserRole))
            if not running:
                it.setText(f"{i + 1}.  {name}")
                it.setFlags(it.flags() | Qt.ItemFlag.ItemIsSelectable)
                continue
            cur = w.batch_current_index - 1
            if i < cur or (i == cur and getattr(w, "batch_in_cooldown", False)):
                mark, locked = "✔", True
            elif i == cur:
                mark, locked = "▶", True
            else:
                mark, locked = "⏳", False
            it.setText(f"{mark}  {i + 1}.  {name}")
            if locked:
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            else:
                it.setFlags(it.flags() | Qt.ItemFlag.ItemIsSelectable)

    def _sync_controls_from_win(self):
        self.cool_spin.blockSignals(True)
        self.shutdown_check.blockSignals(True)
        self.cool_spin.setValue(int(self.win.batch_cooldown_time // 60))
        self.shutdown_check.setChecked(bool(self.win.batch_shutdown_mode))
        self.cool_spin.blockSignals(False)
        self.shutdown_check.blockSignals(False)

    # ── lifecycle ─────────────────────────────────────────

    def showEvent(self, e):
        super().showEvent(e)
        if self._running():
            self._sync_controls_from_win()
        self._was_running = self._running()
        self._render(force=True)
        self._timer.start()

    def hideEvent(self, e):
        self._timer.stop()
        super().hideEvent(e)

    def _render(self, force=False):
        w = self.win
        running = self._running()

        if running and not self._was_running:
            self._sync_controls_from_win()
        if not running and self._was_running:
            self.list.clear()           # batch selesai → mulai staging baru
        self._was_running = running

        if running:
            if self._paths() != [self.list.item(i).data(Qt.ItemDataRole.UserRole)
                                 for i in range(self.list.count())]:
                self._rebuild(list(w.batch_queue))
            else:
                self._decorate()
            done = max(0, min(w.batch_current_index, len(w.batch_queue)))
            state = "cooldown" if getattr(w, "batch_in_cooldown", False) else "compiling"
            self.status_label.setText(
                f"Batch RUNNING ({state}) — step {done}/{len(w.batch_queue)}. "
                f"Changes take effect immediately."
            )
            self.status_label.setStyleSheet("color: #10B981; font-size: 11px;")
            self.start_btn.setVisible(False)
        else:
            self._decorate()
            self.status_label.setText("Idle — Set up the queue, then press Start Batch..")
            self.status_label.setStyleSheet("color: #64748B; font-size: 11px;")
            self.start_btn.setVisible(True)

        pending = max(0, self.list.count() - self._locked())
        self.count_label.setText(f"{pending} pending / {self.list.count()} total")

    # ── actions ───────────────────────────────────────────

    def _add_files(self):
        last = self.win.settings.value("last_profile_dir", "")
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Nuitka Profiles", last, "Nuitka Profiles (*.ncp)"
        )
        if not files:
            return
        self.win.settings.setValue("last_profile_dir", os.path.dirname(files[0]))
        paths = self._paths()
        pending = set(paths[self._locked():])
        for f in files:
            f = os.path.normpath(f)
            if f not in pending:
                paths.append(f)
                pending.add(f)
        self._set_paths(paths)
        self._render()

    def _remove_selected(self):
        locked = self._locked()
        rows = sorted({self.list.row(i) for i in self.list.selectedItems()}, reverse=True)
        rows = [r for r in rows if r >= locked]
        if not rows:
            return
        paths = self._paths()
        for r in rows:
            paths.pop(r)
        self._set_paths(paths)
        self._render()

    def _move(self, delta):
        row = self.list.currentRow()
        tgt = row + delta
        locked = self._locked()
        if row < locked or tgt < locked or tgt >= self.list.count():
            return
        paths = self._paths()
        paths[row], paths[tgt] = paths[tgt], paths[row]
        self._set_paths(paths)
        self.list.setCurrentRow(tgt)

    def _cooldown_changed(self, minutes):
        if self._running():
            self.win.batch_cooldown_time = int(minutes) * 60
            self.win._log(f"<font color='{self.win._t['warning']}'> Quick Queue: cooldown → "
                          f"{minutes} min</font>")

    def _shutdown_toggled(self, on):
        if self._running():
            self.win.batch_shutdown_mode = bool(on)
            self.win._log(f"<font color='{self.win._t['danger']}'> Quick Queue: shutdown after "
                          f"batch → {'ON' if on else 'OFF'}</font>")

    def _start_batch(self):
        w = self.win
        paths = self._paths()
        if not paths:
            QMessageBox.warning(self, "Empty Queue", "Add at least one profile .ncp.")
            return
        if w.compiler_thread and w.compiler_thread.isRunning():
            QMessageBox.warning(self, "Busy", "Compilation is already running.")
            return
        w._start_batch(paths, int(self.cool_spin.value()) * 60,
                       self.shutdown_check.isChecked())
        self._render()
