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
<img width="1365" height="718" alt="Screenshot 2025-11-24 082652" src="https://github.com/user-attachments/assets/a07752d8-f77b-42fe-9bd9-79ec81ed5125" />


---

## 📝 Changelog v4.5.0
### Added
System Monitor Status Bar: Implemented a real-time system monitoring bar at the bottom of the application window.
Displays current CPU and RAM usage with visual progress bars.
Added dynamic color indicators (bars turn red when usage exceeds 85%).
Displays current Operating System information (OS Name, Release, and Architecture).
Application Menu Bar: Introduced a standard top menu bar for better navigation and usability.
File Menu: Includes options for New/Reset, Save Profile, Load Profile, and Exit.
Help Menu: Includes Help Content, Register Format, and About dialogs.
Keyboard Shortcuts: Added standard keyboard shortcuts for improved productivity:
Ctrl+N: Reset UI / New Project.
Ctrl+S: Save Configuration Profile (.ncp).
Ctrl+O: Load Configuration Profile.
File Association (Windows Registry): Added a feature to register .ncp (Nuitka Compiler Profile) extension in the Windows Registry. Users can now double-click .ncp files to open them directly in the application.
### Changed
Modular Architecture: Refactored the codebase to separate UI components. The Menu Bar and System Monitor logic are now handled in a dedicated module (nuitka_menu.py) to improve code maintainability.
UI Layout: Restructured the main window layout to seamlessly integrate the new Menu Bar and Status Bar without disrupting the existing split-pane design.
Visual Improvements: Optimized label colors and contrast in the Status Bar for better readability on light-themed environments.
### Fixed
Dependency Issue: Removed dependency on shlobj and replaced it with ctypes for Windows Shell notifications, resolving import errors on standard Python installations.


## 📥 Installation & Running

### 1. Clone Repo
```bash
git clone https://github.com/danx123/nuitka-compiler-pro
cd nuitka-compiler-pro
