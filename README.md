# TE / TEdit (Text Editor), Known as TEdit on PyPi
[![Python version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License: Custom](https://img.shields.io/badge/license-Custom-lightgrey.svg)](#license)

TE is a Windows-optimized terminal text editor that provides a simple, mouse-driven, and intuitive editing experience without leaving the command line. It features full color theme changing and leverages the powerful pygments library for syntax highlighting across dozens of coding languages; it utilizes the curses library for its terminal user interface (TUI).

How does this exist? A programmer named Ken Arnold made a software library in 1978 called Curses.
<br><br>


░▒▓████████▓▒░▒▓█████▓▒░      
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓████▓▒░        
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█████▓▒░      
                                 
                                 
<br>

#### Current Version: Version 2.7 — Released 2026-05-24

Previous Releases:
- Version 1.6, Released on 7-10-2024
- Version 1.7, Released on 6-22-2025
- Version 1.8, Released on 6-23-2025
- Version 1.9 (PyPi as v0.9.1) — 2025-09-29
<br>

### 🚀 About The Project

TE was created as a demonstration of programming capabilities, showing how to handle complex state management, user input (both keyboard and mouse), and third-party library integration in a significant console application.

## What's New? From Verison 2.7
- Bug Fixes and Refinements
- Limited Horizontal Support (WIP)
- Bug fixes for line movement and horizontal scrolling
- Color Themes added for normal text files
- Improvements and fixes for Color Displays
- Find and Find Next Feature
- Improvements to Open File GUI
- Proper TAB text area support
<br>

## What's New? From Verison 1.9
- Tab button supported
- Canceling Save during text entry
- Bug fixes for line movement, horizontal scrolling functionality
<br>

### ✨ Features

| Feature                  | Description |
|--------------------------|-------------|
| **Syntax Highlighting**  | Auto-detect languages; powered by Pygments. |
| **Full Mouse Support**   | Click to move, drag-select, scroll, and interact with UI menus. |
| **File Browser**         | Navigate filesystem to open files and directories. |
| **Color Themes**	       | Select a Background Color and Text Color for any file |
| **Code Themes**          | Cycle through Pygments color schemes instantly |
| **File Operations**      | New, Open, Save, Save As — all built-in. |
| **Robust Handling**      | Graceful handling of legacy encodings and files. |
| **Toggle Line Numbers**  | Show or hide line numbers with a keypress. |
| ** Text	Search**         | Search forward from your cursor for text
| **Status Bar**           | Shows file name, cursor position, theme, and mode. |

<br><br>
### ⚙️ Getting Started

To download and run, follow these simple steps.
Prerequisites

- Python **3.8+**
- Pygments (installed automatically with tedit)

  ```bash
  pip install pygments
  
<br><br>
### 🖥️ Running the Editor
Download with the PIP command:

  ```bash
Open your Command Prompt or Linux Terminal Window and type in:

pip install tedit

```

Run the editor:
Once you install via pip, you should be able to launch the editor with either of these:

  ```bash
TE

or:

TEdit

```

Launch command is not case sensitive, so use either capitals TE/TEdit or te/tedit.

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

### 📜 License (Wording improved 5-24-2026, Last Updated 9-29-2025)

You may download and use TE by using the pip command, provided through the PyPI network. This is the intended way to use the program.

The source code on GitHub is provided for demonstration purposes only. You may NOT download, use, modify, copy, or distribute the code without express written permission.

<b>COPYRIGHT NOTICE</b>

Copyright © 2024-2026 alby13. All Rights Reserved.

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
