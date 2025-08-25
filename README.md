# Nuitka Compiler Pro

Nuitka Compiler Pro is a modern GUI application based on PyQt6 that simplifies the process of compiling Python scripts into EXE (Windows Executable) format using Nuitka (https://nuitka.net/).

This application is designed with a professional interface and comprehensive features, making it suitable for both Indie Devs and Enterprise Devs who want to easily distribute Python applications.

---

## ✨ Key Features

- 🎛️ **Modern GUI Interface**
- Clean interface, dark console-style log output.
- No need to type the command line manually.

- ⚡ **Fast Compile with Nuitka**
- Supports standalone build options, onefile, and various Nuitka configurations.
- Run the compilation process in a separate thread (doesn't freeze the UI).

- 📝 **Version & Metadata**
- Dedicated dialog for filling in application metadata:
- FileVersion
- ProductName
- CompanyName
- LegalCopyright
- Auto-fill from script name.
- Metadata automatically injected into builds (`--windows-file-version`, `--windows-product-version`, etc.).

- 📂 **File & Directory Management**
- Easily add files/directories to builds.
- Option to include additional resources.

- 🔒 **Stable & Modular**
- Uses PyQt6 `QThread` for build logging.
- Structured & easily customizable builder commands.

---

## 📸 Screenshot
### For PyQt 6:
<img width="601" height="532" alt="pyqt6" src="https://github.com/user-attachments/assets/7ef1271d-3af9-48d9-9337-06c6deeeaaba" />

### For PyQt5:
<img width="603" height="533" alt="pyqt5" src="https://github.com/user-attachments/assets/86a00775-4052-45a1-8e5c-c20cf3777e19" />

---

## 📥 Installation & Running

### 1. Clone Repo
```bash
git clone https://github.com/danx123/nuitka-compiler-pro
cd nuitka-compiler-pro
