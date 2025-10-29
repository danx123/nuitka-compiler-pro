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
![untitled](https://github.com/user-attachments/assets/ba2f6841-b9c3-4f10-9b71-8fb5b0d6515d)

---

## 📝 Changelog v3.8.0
- 🐛 Fixed (Improvement)
Critical UI Freeze: Fixed a bug where the application would hang (Not Responding) or crash after compilation completed, specifically when the "Multimedia Plugin" or "Deploy (.zip)" checkboxes were enabled.
Cause: Heavy I/O operations (file copying and LZMA compression) were previously running on the main thread (GUI thread), completely blocking the application's event loop.
Crashes during Chained Tasks: Fixed a race condition that caused a forced close due to attempts to reuse a QThread handle that hadn't been fully closed by a previous process.

- ⚙️ Changed (Changes)
Asynchronous I/O Processes:
Introducing the new AssetCopyWorker and ZipWorker. These workers now move the file copy and .zip compression logic to separate threads.
Compilation, asset copying, and zipping now run asynchronously and sequentially (chained) without ever blocking the UI.
Safe Thread Management:
Each worker (compile, copy, zip) now uses its own QThread variables (compiler_thread, asset_thread, zip_thread).
Implemented an auto-cleanup mechanism using .deleteLater() on threads and workers to ensure they are safely closed and removed from memory after the task completes. This is a major fix for previous crashes.
UI State Logic:
The "Start Compilation" button will now remain disabled throughout the entire chain (compile -> copy -> zip).
The button will only become active again after all selected tasks have completed, or if one of the steps fails midway.


## 📥 Installation & Running

### 1. Clone Repo
```bash
git clone https://github.com/danx123/nuitka-compiler-pro
cd nuitka-compiler-pro
