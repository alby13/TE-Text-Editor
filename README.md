# TE (Text Editor)
[![Python version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License: Custom](https://img.shields.io/badge/license-Custom-lightgrey.svg)](#license)

TE is a cross-platform terminal text editor that provides a simple, mouse-driven, and intuitive editing experience without leaving the command line. It leverages the powerful pygments library for syntax highlighting across dozens of languages and the standard curses library for its terminal user interface (TUI).

How does this exist? A programmer named Ken Arnold made a software library in 1978 called Curses.
<br><br>


░▒▓████████▓▒░▒▓██████▓▒░      
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█████▓▒░        
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓██████▓▒░      
                                 
                                 
<br>

#### Current Version: Build #8, Released 6-23-2025

Previous Releases:
- Build #6, Released on 7-10-2024
- Build #7, Released on 6-22-2025
<br>

### 🚀 About The Project

TE is a cross-platform terminal text editor that provides a simple, mouse-driven, and intuitive editing experience without leaving the command line. It leverages the powerful pygments library for syntax highlighting across dozens of languages and the standard curses library for its terminal user interface (TUI).

This project was created as a demonstration of programming capabilities, showing how to handle complex state management, user input (both keyboard and mouse), and third-party library integration in a significant console application.

## What's New? Verison 8
- Copy and Paste feature, along with Cut.
- Undo/Redo
<br>

### ✨ Features

| Feature                  | Description |
|--------------------------|-------------|
| **Syntax Highlighting**  | Auto-detect languages; powered by Pygments. |
| **Full Mouse Support**   | Click to move, drag-select, scroll, and interact with UI menus. |
| **File Browser**         | Navigate filesystem to open files and directories. |
| **Dynamic Themes**       | Cycle through Pygments color schemes instantly. |
| **File Operations**      | New, Open, Save, Save As — all built-in. |
| **Robust Handling**      | Graceful handling of legacy encodings and files. |
| **Toggleable Line Numbers** | Show or hide line numbers with a keypress. |
| **Status Bar**           | Shows file name, cursor position, theme, and mode. |
| **Fun Extras**           | Imaginary printer and coffee break simulator! ☕ |

#### WIP
Working on you being able to get it by one command. I haven't done anything to make this happen... yet.

<br><br>
### ⚙️ Getting Started

To get a local copy up and running, follow these simple steps.
Prerequisites

- Python **3.6+**
- Pygments:
  ```bash
  pip install pygments
  
<br><br>
### 🖥️ Running the Editor
Clone the repo:

  ```bash
git clone https://github.com/alby13/TE-Text-Editor.git
cd TE-Text-Editor

```

Run the editor:

  ```bash
python te.py
If your main file is named differently (e.g. te_editor.py), update accordingly.

```

<br><br>
### ⌨ Usage & Controls

TE is designed to be intuitive, especially for users familiar with graphical text editors.
| Key      | Action                           |
| -------- | -------------------------------- |
| `F1`     | Open file browser                |
| `F2`     | Save current file                |
| `F3`     | New file                         |
| `F4`     | Cycle color theme                |
| `F5`     | Toggle line numbers              |
| `F9`     | Switch between Edit & Menu Modes |
| `Esc` ×3 | Exit the editor immediately      |

<br>
🖊️ Edit Mode (Default)
- Arrow keys: Move the cursor

- Page Up / Down: Scroll by screen

- Typing: Insert characters

- Enter: New line

- Backspace / Delete: Remove characters

- Shift + Arrows: Select text
<br>

### 🧭 Menu Mode

Activated via F9 or clicking the menu bar.

- Left/Right Arrows: Switch top-level menus

- Up/Down Arrows: Navigate submenu

- Enter: Select menu item

- Esc: Exit submenu or Menu Mode
<br>

### 🖱️Mouse Controls

- Click in text area: Move cursor

- Right Click: Access Submenu

- Click and drag: Select text

- Scroll wheel: Scroll document

- Click menu bar: Activate Menu Mode

- Click submenu item: Execute action<br>(Undo, Redo, Copy, Paste, Cut)
<br>

### 📜 License

This project is provided for demonstration purposes only. Do not copy, modify, or distribute without express written permission.

<b>COPYRIGHT NOTICE</b>

Copyright © 2024-2025 alby13. All Rights Reserved.

This program, TE (Text Editor), is copyrighted material and may not be used, copied,
distributed, or modified for any purpose without the express written permission of
alby13.

Disclaimer regarding Third-Party Libraries:

This program utilizes the Python `curses` library (covered by the Python Software Foundation License - PSF License)
and the `pyperclip` library (covered by the 3-Clause BSD License).
Copies of their respective licenses can be found in the files `LICENSE_PSF.txt` and `LICENSE_BSD.txt`
accompanying this program. The terms of these licenses apply only to those specific libraries
and other components they cover, not to this program's original code.

### 🙏 Acknowledgments

- The curses library for providing the foundation of the terminal interface.
- The Pygments library is used for syntax highlighting.
- The pyperclip for copy and paste functionality.
