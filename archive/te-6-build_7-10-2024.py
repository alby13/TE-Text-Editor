# TE (Text Editor) - Build 6, 7-10-2024 - Copyright 2024, All Rights Reserved.
# Created by alby13 - Offered with no warranty, not responsible for anything.

import curses
import os
import sys
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_all_styles

class Menu:
    def __init__(self, items):
        self.items = items
        self.current_item = 0
        self.open = False
        self.submenus = {
            "File": [" New ", " Open ", " Save ", " Adios "],
            "Edit": ["Cut", "Copy", "Paste"],
            "Menu": ["Toggle Line Numbers", " Change Theme"],
            "Help": ["About"],
            "Fun": ["Print to Imaginary Printer", "Play DOOM", "Bug Introducer", "Coffee Break Simulator", "Report a good feature", "Procrastination NOW!", "Write it for me"]
        }

    def display(self, stdscr, start_y, start_x):
        for idx, item in enumerate(self.items):
            if idx == self.current_item:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(start_y, start_x + idx * 10, f" {item} ")
            if idx == self.current_item:
                stdscr.attroff(curses.A_REVERSE)
        
        if self.open:
            self.display_submenu(stdscr, start_y + 1, start_x + self.current_item * 10)

    def display_submenu(self, stdscr, start_y, start_x):
        submenu_items = self.submenus[self.items[self.current_item]]
        for idx, item in enumerate(submenu_items):
            stdscr.addstr(start_y + idx, start_x, f" {item} ")

    def handle_mouse(self, mx, my):
        if my == 0:  # Menu bar clicked
            selected_item = min(mx // 10, len(self.items) - 1)
            if self.open and self.current_item == selected_item:
                self.open = False  # Deselect the menu if the same item is clicked again
            else:
                self.current_item = selected_item
                self.open = True  # Show the submenu
        elif self.open:
            submenu_items = self.submenus[self.items[self.current_item]]
            if 0 <= my - 1 < len(submenu_items):
                return f"{self.items[self.current_item]}:{submenu_items[my - 1]}"
        return None

    def handle_key(self, key):
        if key == ord('\n'):
            if self.open:
                submenu_items = self.submenus[self.items[self.current_item]]
                return f"{self.items[self.current_item]}:{submenu_items[0]}"
            else:
                self.open = True
        elif key == curses.KEY_LEFT:
            self.current_item = (self.current_item - 1) % len(self.items)
        elif key == curses.KEY_RIGHT:
            self.current_item = (self.current_item + 1) % len(self.items)
        return None

class TextEditor:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.content = ['']
        self.cursor_y = 0
        self.cursor_x = 0
        self.top_line = 0
        self.current_file = None
        self.message = ""
        self.color_theme = "default"
        self.menu = Menu(["File", "Edit", "Menu", "Help", "Fun"])
        self.show_line_numbers = False
        self.menu_focus = True

    def run(self):
        curses.curs_set(1)
        curses.start_color()
        curses.use_default_colors()
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        self.stdscr.nodelay(1)

        while True:
            self.draw_interface()
            self.handle_input()

    def draw_interface(self):
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()

        # Draw menu
        self.menu.display(self.stdscr, 0, 0)

        # Draw content
        content_height = height - 4
        for i in range(content_height):
            line_num = self.top_line + i
            if line_num < len(self.content):
                line = self.content[line_num]
                if self.show_line_numbers:
                    self.stdscr.addstr(i + 1, 0, f"{line_num + 1:4d} ")
                self.stdscr.addstr(i + 1, 5 if self.show_line_numbers else 0, line)

        # Draw status bar
        self.stdscr.addstr(height - 3, 0, f"File: {self.current_file or 'Untitled'} | Cursor: ({self.cursor_y}, {self.cursor_x})")
        # Draw message bar
        self.stdscr.addstr(height - 2, 0, self.message)
        # Draw help bar
        self.stdscr.addstr(height - 1, 0, "F1: Open  F2: Save  F3: New  F4: Theme  F5: Line Numbers  F9: Menu Access  - Escape Key 3x To Quit")

        # Add mode indicator
        mode = "MENU" if self.menu_focus else "TEXT"
        self.stdscr.addstr(height - 3, width - 10, f"Mode: {mode}")

        # Display the cursor
        try:
            self.stdscr.move(self.cursor_y - self.top_line + 1, self.cursor_x + (5 if self.show_line_numbers else 0))
        except curses.error:
            pass

    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_F9:
            self.menu_focus = not self.menu_focus
            self.message = "" if self.menu_focus else "Menu Control Activated!"
        elif self.menu_focus:
            if key in [curses.KEY_LEFT, curses.KEY_RIGHT]:
                action = self.menu.handle_key(key)
                if action:
                    self.handle_menu_action(action)
            elif key == ord('\n'):
                self.menu.open = not self.menu.open
        else:
            if key == ord('\n'):  # Add this condition
                self.insert_newline()
            elif key == curses.KEY_MOUSE:
                _, mx, my, _, _ = curses.getmouse()
                if my == 0 or (self.menu.open and my <= len(self.menu.submenus[self.menu.items[self.menu.current_item]])):
                    action = self.menu.handle_mouse(mx, my)
                    if action:
                        self.handle_menu_action(action)
                else:
                    self.cursor_y = min(self.top_line + my - 1, len(self.content) - 1)
                    self.cursor_x = max(0, min(mx - 5 if self.show_line_numbers else mx, len(self.content[self.cursor_y])))
            elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, ord('\n')]:
                action = self.menu.handle_key(key)
                if action:
                    self.handle_menu_action(action)
                else:
                    self.cursor_y = min(self.top_line + my - 1, len(self.content) - 1)
                    self.cursor_x = max(0, min(mx - 5 if self.show_line_numbers else mx, len(self.content[self.cursor_y])))
            elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, ord('\n')]:
                action = self.menu.handle_key(key)
                if action:
                    self.handle_menu_action(action)
            elif key == curses.KEY_UP:
                self.move_cursor(-1, 0)
            elif key == curses.KEY_DOWN:
                self.move_cursor(1, 0)
            #elif key == ord('\n') and not self.menu_focus:
            elif key == ord('\n'):
                self.insert_newline()
            elif key == curses.KEY_BACKSPACE or key == 127:
                self.delete_char()
            elif key == curses.KEY_F1:
                self.open_file()
            elif key == curses.KEY_F2:
                self.save_file()
            elif key == curses.KEY_F3:
                self.new_file()
            elif key == curses.KEY_F4:
                self.change_theme()
            elif key == curses.KEY_F5:
                self.show_line_numbers = not self.show_line_numbers
            else:
                if key == 27:
                    if self.prev_key == 27:
                        sys.exit(0)
                    self.prev_key = key
                else:
                    self.prev_key = None
                    if 32 <= key <= 126:
                        self.insert_char(chr(key))

    def handle_menu_action(self, action):
        menu, item = action.split(':')
        if menu == "File":
            if item == "New":
                self.new_file()
            elif item == "Open":
                self.open_file()
            elif item == "Save":
                self.save_file()
            elif item == "Exit":
                sys.exit(0)
        elif menu == "Edit":
            self.message = f"Edit:{item} not implemented yet"
        elif menu == "View":
            if item == "Toggle Line Numbers":
                self.show_line_numbers = not self.show_line_numbers
            elif item == "Change Theme":
                self.change_theme()
        elif menu == "Help":
            self.message = "ABOUT: TE (Text Editor) - A buggy and incomplete text editor created by alby13. <alby13> It's mine! My own, my precious."

        # Hide the menu after an action is performed
        self.menu.open = False
        self.menu_focus = False

    def move_cursor(self, dy, dx):
        new_y = max(0, min(self.cursor_y + dy, len(self.content) - 1))
        new_x = max(0, min(self.cursor_x + dx, len(self.content[new_y])))
        
        if new_y != self.cursor_y:
            self.cursor_y = new_y
            self.cursor_x = new_x
        else:
            self.cursor_x = new_x

        # Adjust view if cursor is out of visible area
        height, _ = self.stdscr.getmaxyx()
        if self.cursor_y < self.top_line:
            self.top_line = self.cursor_y
        elif self.cursor_y >= self.top_line + height - 4:
            self.top_line = max(0, self.cursor_y - height + 5)

    def insert_char(self, char):
        line = self.content[self.cursor_y]
        self.content[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
        self.cursor_x += 1

    def insert_newline(self):
        line = self.content[self.cursor_y]
        self.content[self.cursor_y] = line[:self.cursor_x]
        self.content.insert(self.cursor_y + 1, line[self.cursor_x:])
        self.cursor_y += 1
        self.cursor_x = 0
        self.move_cursor(0, 0)  # This will adjust the view if necessary

    def delete_char(self):
        if self.cursor_x == 0 and self.cursor_y > 0:
            self.cursor_x = len(self.content[self.cursor_y - 1])
            self.content[self.cursor_y - 1] += self.content.pop(self.cursor_y)
            self.cursor_y -= 1
        elif self.cursor_x > 0:
            line = self.content[self.cursor_y]
            self.content[self.cursor_y] = line[:self.cursor_x - 1] + line[self.cursor_x:]
            self.cursor_x -= 1

    def save_file(self):
        if not self.current_file:
            self.current_file = self.get_user_input("Enter filename to save: ")
        with open(self.current_file, 'w') as f:
            f.write('\n'.join(self.content))
        self.message = f"Saved to {self.current_file}"

    def open_file(self):
        filename = self.get_user_input("Enter filename to open: ")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.content = f.read().splitlines() or ['']
            self.current_file = filename
            self.cursor_y = 0
            self.cursor_x = 0
            self.top_line = 0
            self.message = f"Opened {filename}"
        else:
            self.message = f"File {filename} not found"

    def new_file(self):
        self.content = ['']
        self.current_file = None
        self.cursor_y = 0
        self.cursor_x = 0
        self.top_line = 0
        self.message = "New file created"

    def change_theme(self):
        themes = list(get_all_styles())
        current_index = themes.index(self.color_theme)
        next_index = (current_index + 1) % len(themes)
        self.color_theme = themes[next_index]
        self.message = f"Theme changed to {self.color_theme}"

    def get_user_input(self, prompt):
        curses.echo()
        self.stdscr.addstr(curses.LINES - 1, 0, prompt)
        self.stdscr.refresh()
        input = self.stdscr.getstr(curses.LINES - 1, len(prompt))
        curses.noecho()
        return input.decode('utf-8')

def main(stdscr):
    editor = TextEditor(stdscr)
    editor.run()

if __name__ == "__main__":
    curses.wrapper(main)
