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
### For PySide6
<img width="1365" height="767" alt="Cuplikan layar 2026-01-12 151937" src="https://github.com/user-attachments/assets/7027af39-3c93-4a3c-9b3b-ab61aad726a9" />
<img width="1366" height="768" alt="nuitka_sc" src="https://github.com/user-attachments/assets/3347d249-b708-448a-9df0-dbfc32dbb481" />



---

## 📝 Changelog v4.8.0
Workspace Persistence & UX Refinement

### 🚀 Summary
This update focuses on streamlining the user workflow by implementing a robust profile management system and adding "memory" to file navigation, ensuring a more seamless professional experience.

### 🛠 Features & Improvements
- Smart Save Logic:
  - Introduced a distinction between Save and Save As. The application now intelligently updates the currently active profile (Overwrite) instead of prompting for a new file every time.
  - Dynamic Window Titles: The application title bar now displays the name of the active profile for better workspace orientation.
- Directory Persistence (Last Known Location):
The application now remembers your last accessed directory. Open and Save As dialogs will automatically point to the last used folder, eliminating repetitive navigation.
- Enhanced File Menu:
Added "Save Profile As..." (Ctrl+Shift+S) to the File menu, allowing users to easily branch off or duplicate existing configurations.
- Session State Tracking:
Added internal current_path tracking to ensure the UI state remains synchronized with the physical file on the disk.

### 🐞 Bug Fixes
- Resolved Profile Overwrite Bug: Fixed an issue where clicking "Save" would always trigger a new file dialog, even when a profile was already loaded.
- UI Reset Synchronization: Updated the "New/Reset" function to clear the active file session, preventing accidental saves to previous profiles after a reset.
- Path Validation: Improved handling of directory paths to ensure consistent behavior across different system environments.
---


## 📥 Installation & Running

### 1. Clone Repo
```bash
git clone https://github.com/danx123/nuitka-compiler-pro
cd nuitka-compiler-pro
