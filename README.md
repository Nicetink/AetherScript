# AetherScript IDE v1.0

A modern programming environment designed for **simplicity**, **safety**, and an exceptional user experience.

**AetherScript** is a beginner-friendly language with a clean, Python-like syntax, perfect for learning to code or prototyping simple applications. Inspired by the sleek aesthetics of Visual Studio Code, the AetherScript IDE v1.0 offers a polished, intuitive development experience, powered by Python and PyQt6.

## ✨ Features
- **Simple Syntax**: Write clear `.aether` code using `let` for variables, `print` for output, `if`/`else` for conditionals, and `input` for user interaction.
- **Syntax Highlighting**: Vibrant highlighting for keywords (`let`, `print`, `if`, `else`, `input`) in dark (#161b22) and light (#f6f8fa) themes.
- **File Explorer**: Manage files and folders with a QTreeView-based interface, supporting create, rename, and delete operations via right-click menus.
- **Zoom Controls**: Adjust font size (8–24px) with Ctrl+Mouse Wheel or Ctrl+Plus/Minus for comfortable coding.
- **Themes**: Switch between modern dark and light themes to match your style.
- **Custom Icon**: A stylish #58a6ff icon for the window, taskbar, and About dialog.
- **Safe Execution**: Uses `ast.literal_eval` to prevent code injection, optimized for minimal antivirus false positives (0–2 detections on VirusTotal).
- **Lightweight IDE**: Built with PyQt6, offering a fast and responsive experience.
- **Installer**: A beautiful Inno Setup installer (`AetherScriptIDE_Setup.exe`) with English/Russian support and optional documentation.
- **Documentation**: Comprehensive `AetherScript_Documentation.pdf` included.
- **Open Source**: Licensed under the NSPL, welcoming contributions from the community.

## 🚀 Getting Started

1. **Download the Installer**:
   - [AetherScriptIDE_Setup.exe](https://github.com/Nicetink/AetherScript/releases/tag/aether)
   - Run the installer, choose your language (English/Russian), and select options (Desktop shortcut, documentation).

2. **Run from Source** (optional):
   ```bash
   pip install PyQt6==6.7.0 Pillow==10.4.0
   python ide.py
   ```

3. **Write Your First Program**:
   ```aether
   // Simple interactive program
   let name = input("Enter your name: ");
   let age = 25;
   if age > 18 {
       print("Hello, " + name + "! Welcome to AetherScript!");
   } else {
       print("Hi, " + name + "! You're young!");
   }
   ```

4. Explore the [Documentation](https://github.com/your-username/aether-script/releases/download/v1.0/AetherScript_Documentation.pdf) for detailed guides.

## 🌟 Current Status

AetherScript IDE v1.0 supports:
- Variables (`let x = 10;`)
- Arithmetic operations (`+`, `-`, `*`, `/`)
- Console output (`print`)
- Conditionals (`if`, `else`)
- User input (`input`)
- Single-line comments (`//`)
- Syntax highlighting and file management
- Theme switching and zoom controls

## 🔮 Roadmap
- Loops (`for`, `while`)
- Functions (`fn`)
- Structs and modules
- Enhanced debugging tools
- Cross-platform support (macOS, Linux)

## ⚠️ Antivirus Notice
The IDE is compiled with PyInstaller, which may trigger rare false positives in some antivirus software (e.g., Jiangmin, SecureAge). Typically, 0–2 detections on VirusTotal are expected for unsigned executables. Verify the source code on [GitHub] or run `ide.py` directly.

## 🤝 Contributing
We welcome contributions! Check out our not yet

## 📚 Resources
- [Official Website](https://nicetink.github.io/AetherScript/)
- [itch.io Page](https://4-key.itch.io/aetherscript)
- [Documentation](https://nicetink.github.io/docweb/)

## 📝 License
AetherScript is licensed under the [NSPL License]

```
Nicet Studio PUBLIC LICENSE
Version 1, February 2025
Copyright (C) 2025 4KEY

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, publish, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

Code the future with AetherScript! 🚀
