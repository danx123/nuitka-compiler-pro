import sys
import os
import subprocess
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QFileDialog, QTextEdit, QCheckBox, QLabel, QGroupBox
)
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# --- Worker Thread untuk menjalankan Nuitka agar GUI tidak freeze ---
class CompilerWorker(QObject):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.progress_update.emit(output.strip())
            
            self.process.wait()
            rc = self.process.poll()
            
            if rc == 0:
                self.finished.emit("\n--- KOMPILASI SUKSES! ---")
            else:
                self.finished.emit(f"\n--- KOMPILASI GAGAL (Error Code: {rc}) ---")

        except Exception as e:
            self.finished.emit(f"\n--- TERJADI ERROR KRITIS ---\n{str(e)}")


# --- Jendela Utama Aplikasi ---
class NuitkaGui(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nuitka GUI Setup Tool')
        self.setGeometry(100, 100, 800, 700) # Perbesar sedikit jendela

        main_layout = QVBoxLayout()

        # --- Bagian Input & Output ---
        io_group = QGroupBox("Input & Output")
        io_layout = QVBoxLayout()
        self.script_path_edit = self.create_file_selector("Pilih Script Python (.py)", self.select_script, "Pilih file Python...")
        io_layout.addLayout(self.script_path_edit)
        self.output_dir_edit = self.create_file_selector("Output Direktori", self.select_output_dir, "Pilih folder output...", is_folder=True)
        io_layout.addLayout(self.output_dir_edit)
        io_group.setLayout(io_layout)
        main_layout.addWidget(io_group)

        # --- Bagian Opsi Kompilasi ---
        options_group = QGroupBox("Opsi Kompilasi")
        options_layout = QVBoxLayout()
        self.onefile_check = QCheckBox("Mode One-File (satu .exe)")
        self.onefile_check.setToolTip("Jika tidak dicentang, akan menghasilkan folder (One-Directory)")
        self.disable_console_check = QCheckBox("Sembunyikan Jendela Konsol")
        options_layout.addWidget(self.onefile_check)
        options_layout.addWidget(self.disable_console_check)
        self.icon_path_edit = self.create_file_selector("Pilih Ikon (.ico)", self.select_icon, "Pilih file ikon...")
        options_layout.addLayout(self.icon_path_edit)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # --- BARU: Bagian Informasi Versi ---
        version_group = QGroupBox("Informasi Versi Aplikasi (dari .txt)")
        version_layout = QVBoxLayout()
        self.version_file_edit = self.create_file_selector("File Versi (.txt)", self.select_version_file, "Pilih file versi...")
        version_layout.addLayout(self.version_file_edit)
        version_group.setLayout(version_layout)
        main_layout.addWidget(version_group)

        # --- Bagian File Tambahan ---
        data_group = QGroupBox("Sertakan File & Folder Tambahan")
        data_layout = QVBoxLayout()
        data_layout.addWidget(QLabel("Sertakan File (pisahkan dengan koma):"))
        self.include_files_edit = QLineEdit()
        self.include_files_edit.setPlaceholderText("contoh: gambar.png,data/config.json")
        data_layout.addWidget(self.include_files_edit)
        data_layout.addWidget(QLabel("Sertakan Folder (pisahkan dengan koma):"))
        self.include_dirs_edit = QLineEdit()
        self.include_dirs_edit.setPlaceholderText("contoh: assets,templates")
        data_layout.addWidget(self.include_dirs_edit)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)
        
        # --- Bagian Log Output ---
        log_group = QGroupBox("Log Kompilasi")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0; font-family: Consolas, monaco, monospace;")
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # --- Bagian Tombol Kontrol ---
        control_layout = QHBoxLayout()
        self.preview_cmd_button = QPushButton("Lihat Perintah")
        self.preview_cmd_button.clicked.connect(self.preview_command)
        self.clear_log_button = QPushButton("Bersihkan Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        self.compile_button = QPushButton("Mulai Kompilasi")
        self.compile_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.compile_button.clicked.connect(self.run_compilation)
        control_layout.addWidget(self.preview_cmd_button)
        control_layout.addWidget(self.clear_log_button)
        control_layout.addStretch()
        control_layout.addWidget(self.compile_button)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def create_file_selector(self, label_text, connect_func, placeholder, is_folder=False):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        button = QPushButton("Browse...")
        button.clicked.connect(lambda: connect_func(line_edit))
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return layout

    def select_script(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih Script Python', '', 'Python Files (*.py *.pyw)')
        if fname:
            line_edit.setText(fname)

    def select_icon(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File Ikon', '', 'Icon Files (*.ico)')
        if fname:
            line_edit.setText(fname)

    def select_output_dir(self, line_edit):
        dname = QFileDialog.getExistingDirectory(self, 'Pilih Direktori Output')
        if dname:
            line_edit.setText(dname)
            
    # --- BARU ---
    def select_version_file(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File Versi', '', 'Text Files (*.txt)')
        if fname:
            line_edit.setText(fname)

    def build_command(self):
        script_path = self.script_path_edit.itemAt(1).widget().text()
        if not script_path:
            self.log_output.append("<font color='red'>ERROR: Script Python belum dipilih!</font>")
            return None

        command = ["python", "-m", "nuitka"]
        command.append(f'"{script_path}"')

        command.append("--standalone")
        if self.onefile_check.isChecked():
            command.append("--onefile")
        
        if self.disable_console_check.isChecked():
            command.append("--windows-disable-console")

        output_dir = self.output_dir_edit.itemAt(1).widget().text()
        if output_dir:
            command.append(f'--output-dir="{output_dir}"')

        icon_path = self.icon_path_edit.itemAt(1).widget().text()
        if icon_path:
            command.append(f'--windows-icon-from-ico="{icon_path}"')
            
        # --- LOGIKA BARU: Proses file versi ---
        version_file_path = self.version_file_edit.itemAt(1).widget().text()
        if version_file_path and os.path.exists(version_file_path):
            try:
                version_map = {
                    "FileVersion": "--windows-file-version",
                    "ProductVersion": "--windows-product-version",
                    "ProductName": "--windows-product-name",
                    "CompanyName": "--windows-company-name",
                    "FileDescription": "--windows-file-description",
                    "InternalName": "--windows-internal-name",
                    "OriginalFilename": "--windows-original-filename",
                    "LegalCopyright": "--windows-legal-copyright",
                }
                with open(version_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key in version_map:
                                command.append(f'{version_map[key]}="{value}"')
            except Exception as e:
                self.log_output.append(f"<font color='orange'>WARNING: Gagal memproses file versi: {e}</font>")
        
        include_files = self.include_files_edit.text().strip()
        if include_files:
            for item in include_files.split(','):
                item = item.strip()
                command.append(f'--include-data-file="{item}={os.path.basename(item)}"')

        include_dirs = self.include_dirs_edit.text().strip()
        if include_dirs:
            for item in include_dirs.split(','):
                item = item.strip()
                command.append(f'--include-data-dir="{item}={item}"')
                
        command.append("--show-progress")
        command.append("--show-memory")
        command.append("--jobs=4")
        command.append("--remove-output")

        return " ".join(command)
        
    def preview_command(self):
        command = self.build_command()
        if command:
            self.log_output.append("\n--- Perintah yang akan dijalankan ---")
            self.log_output.append(command)
            self.log_output.append("-------------------------------------\n")
    
    def clear_log(self):
        self.log_output.clear()

    def run_compilation(self):
        command_str = self.build_command()
        if not command_str:
            return

        self.clear_log()
        self.log_output.append("--- Memulai Proses Kompilasi ---")
        self.log_output.append(f"Perintah: {command_str}\n")
        
        self.compile_button.setEnabled(False)
        self.compile_button.setText("Mengompilasi...")

        self.thread = QThread()
        self.worker = CompilerWorker(command_str)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.compilation_finished)
        self.worker.progress_update.connect(self.update_log)
        self.thread.start()

    def update_log(self, text):
        self.log_output.append(text)

    def compilation_finished(self, message):
        self.log_output.append(f"<font color='lime'>{message}</font>")
        self.compile_button.setEnabled(True)
        self.compile_button.setText("Mulai Kompilasi")
        self.thread.quit()
        self.thread.wait()

def main():
    app = QApplication(sys.argv)
    ex = NuitkaGui()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()