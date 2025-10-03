# Nuitka Compiler Pro

Nuitka Compiler Pro is a modern GUI application based on PySide6 that simplifies the process of compiling Python scripts into EXE (Windows Executable) format using Nuitka (https://nuitka.net/).

This application is designed with a professional interface and comprehensive features, making it suitable for both Indie Devs and Enterprise Devs who want to easily distribute Python applications.

---

## ✨ Key Features

- 🎛️ **Modern GUI Interface**
- Clean interface, dark console-style log output.
- No need to type the command line manually.

- ⚡ **Fast Compile with Nuitka**
- Supports standalone build options, onefile, and various Nuitka configurations.
- Run the compilation process in a separate thread (doesn't freeze the UI).

- 📂 **File & Directory Management**
- Easily add files/directories to builds.
- Option to include additional resources.

- 🔒 **Stable & Modular**
- Uses PySide6 `QThread` for build logging.
- Structured & easily customizable builder commands.

---

## 📸 Screenshot
### For PyQt6, PyQt5, PySide6, PySide2

<img width="703" height="683" alt="Capture" src="https://github.com/user-attachments/assets/2b92e574-2354-4246-a2ee-a1e277474d37" />



---

## 📝 Changelog v3.5.0
- Update Framework
- Added .ncp (Nuitka Compiler Profile) — save/load build configurations.
- Added Elapsed Time display in compilation log header.
- Added Reload UI action to apply preference changes without restart.
- Minor UX improvements: clearer log, improved cache management button, preview command fixes.

## 📥 Installation & Running

### 1. Clone Repo
```bash
git clone https://github.com/danx123/nuitka-compiler-pro
cd nuitka-compiler-pro
