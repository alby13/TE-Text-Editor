# TE (Text Editor)
[![Python version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License: Custom](https://img.shields.io/badge/license-Custom-lightgrey.svg)](#license)

TE is a cross-platform terminal text editor that provides a simple, mouse-driven, and intuitive editing experience without leaving the command line. It leverages the powerful pygments library for syntax highlighting across dozens of languages and the standard curses library for its terminal user interface (TUI).

How does this exist? A programmer named Ken Arnold made a software library in 1978 called Curses.
<br><br>


░▒▓████████▓▒░▒▓████████▓▒░      
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓██████▓▒░        
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓█▓▒░             
____░▒▓█▓▒░______░▒▓████████▓▒░      
                                 
                                 
- Current Version: Build #7, Released 6-22-2025

- Previous: Build #6, Released on 7-10-2024
<br>

### 🚀 About The Project

TE is a cross-platform terminal text editor that provides a simple, mouse-driven, and intuitive editing experience without leaving the command line. It leverages the powerful pygments library for syntax highlighting across dozens of languages and the standard curses library for its terminal user interface (TUI).

This project was created as a demonstration of programming capabilities, showing how to handle complex state management, user input (both keyboard and mouse), and third-party library integration in a significant console application.

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
General Controls
Key	Action
F1	Open the file browser to open a file.
F2	Save the current file.
F3	Create a new, empty file.
F4	Cycle to the next color theme.
F5	Toggle line numbers on or off.
F9	Toggle focus between Edit Mode & Menu Mode.
Esc (x 3)	Quit the editor immediately.
Edit Mode

This is the default mode for typing and editing text.

    Arrow Keys: Move the cursor.

    Page Up / Page Down: Scroll through the document by a full screen.

    Typing: Inserts characters at the cursor position.

    Enter: Inserts a new line.

    Backspace: Deletes the character to the left of the cursor.

    Delete: Deletes the character at the cursor's position.

    Shift + Arrow Keys: Select text character by character or line by line.

<br><br>
### Menu Mode

Activate by pressing F9 or clicking on the menu bar.

    Left / Right Arrow Keys: Switch between top-level menus (File, Edit, etc.).

    Up / Down Arrow Keys: Navigate items within an open submenu.

    Enter: Select the highlighted menu or submenu item.

    Esc: Close the current submenu or exit menu mode entirely.

Mouse Controls

    Click in Text Area: Moves the cursor to the clicked location. If in Menu Mode, this will switch you back to Edit Mode.

    Click and Drag: Selects a region of text.

    Scroll Wheel: Scrolls the document up or down.

    Click on Menu Bar: Activates Menu Mode and opens the corresponding submenu.

    Click on Submenu Item: Executes the menu action (e.g., opens the "Save As" prompt).

<br><br>
### 📜 License

This project is provided for demonstration purposes only. Do not copy, modify, or distribute without express written permission.

<b>COPYRIGHT NOTICE</b>

Copyright © 2024-2025 alby13. All Rights Reserved.

This program, TE (Text Editor), is copyrighted material and may not be used, copied,
distributed, or modified for any purpose without the express written permission of
alby13.

Disclaimer regarding Third-Party Libraries:

This program utilizes the Python curses library, which is part of the Python
Standard Library and is distributed under the Python Software Foundation License (PSF License).
A copy of the PSF License can be found in the file LICENSE_PSF.txt accompanying this program.
(Note: You should create a file named LICENSE_PSF.txt and include the appropriate license text.)
The terms of the PSF License apply only to the Python curses library and other
Python components, not to this program's original code.

### 🙏 Acknowledgments

- The incredible Pygments library is used for syntax highlighting.
- This project would not be possible without the curses library for providing the foundation of the terminal interface.
