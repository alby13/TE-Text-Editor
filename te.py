# TE (Text Editor) - Build 9, 9-29-2025 - Copyright 2024-2025, All Rights Reserved.
# Created by alby13 - https://github.com/alby13/TE-Text-Editor
# Offered with no warranty, creator not responsible for anything.

import curses
import os
import sys
import copy
import pyperclip
from pygments import highlight, lex
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.formatter import Formatter
from pygments.token import Token
from pygments.styles import get_all_styles, get_style_by_name

# This custom formatter translates Pygments's style into curses color pairs.
class CursesFormatter(Formatter):
    def __init__(self, **options):
        Formatter.__init__(self, **options)
        self.color_map = {}
        self.next_color_pair = 1
        self.style = get_style_by_name(options.get('style', 'default'))

        bg_hex = self.style.background_color
        self.background_color_index = self.hex_to_curses_color(bg_hex)
        
    def setup_colors(self):
        """Initialize color pairs - must be called after curses.start_color()"""
        # Reset color mapping when setting up
        self.color_map = {}
        self.next_color_pair = 1
        
        # Map pygments styles to curses colors
        for token, s in self.style:
            # Create a unique key for the style attributes
            style_key = (s['color'], s['bold'], s['italic'], s['underline'])
            if style_key not in self.color_map and self.next_color_pair < 64:  # Curses color pair limit
                try:
                    fg_color = self.hex_to_curses_color(s['color'])
                    # Use the stored background color
                    curses.init_pair(self.next_color_pair, 
                                    fg_color if fg_color != -1 else curses.COLOR_WHITE,  # Fallback to white
                                    self.background_color_index)
                    self.color_map[style_key] = self.next_color_pair
                    self.next_color_pair += 1
                except curses.error:
                    # If we can't initialize more color pairs, stop trying
                    break

    def hex_to_curses_color(self, hex_color):
        # A simple mapping from hex to the 8 standard curses colors.
        # This is a simplification; a full 256-color implementation is more complex.
        if not hex_color or len(hex_color) < 6:
            return -1 # Default terminal text color
        
        try:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        except ValueError:
            return -1
            
        # Simplified brightness check
        brightness = (r + g + b) / 3
        
        if brightness < 64: return curses.COLOR_BLACK
        if r > 128 and g < 128 and b < 128: return curses.COLOR_RED
        if r < 128 and g > 128 and b < 128: return curses.COLOR_GREEN
        if r > 128 and g > 128 and b < 128: return curses.COLOR_YELLOW
        if r < 128 and g < 128 and b > 128: return curses.COLOR_BLUE
        if r > 128 and g < 128 and b > 128: return curses.COLOR_MAGENTA
        if r < 128 and g > 128 and b > 128: return curses.COLOR_CYAN
        if brightness > 192: return curses.COLOR_WHITE
        return -1 # Default

    def format(self, tokensource, outfile):
        """Returns a list of (text, attribute) tuples"""
        result = []
        for ttype, value in tokensource:
            style_info = self.style.style_for_token(ttype)
            style_key = (style_info['color'], style_info['bold'], style_info['italic'], style_info['underline'])
            
            attr = 0  # Default attribute
            if style_key in self.color_map:
                pair_number = self.color_map[style_key]
                attr = curses.color_pair(pair_number)
                if style_info['bold']: attr |= curses.A_BOLD
                if style_info['italic']: attr |= curses.A_ITALIC # Note: May not be supported in all terminals
                if style_info['underline']: attr |= curses.A_UNDERLINE
            
            result.append((value, attr))
        
        return result

class FileBrowser:
    def __init__(self, stdscr, start_dir=None):
        self.stdscr = stdscr
        self.current_dir = start_dir or os.getcwd()
        self.selected_item = 0
        self.top_item = 0
        self.items = []
        self.refresh_items()
        
    def refresh_items(self):
        """Refresh the list of files and directories"""
        try:
            # Get list of items in current directory
            all_items = os.listdir(self.current_dir)
            
            # Separate directories and files
            dirs = []
            files = []
            
            for item in all_items:
                full_path = os.path.join(self.current_dir, item)
                if os.path.isdir(full_path):
                    dirs.append(f"[{item}]")  # Mark directories with brackets
                else:
                    files.append(item)
            
            # Sort directories and files separately
            dirs.sort()
            files.sort()
            
            # Add parent directory option if not at root
            self.items = []
            if self.current_dir != "/" and self.current_dir != os.path.dirname(self.current_dir):
                self.items.append("[..]")  # Parent directory
            
            # Combine directories and files
            self.items.extend(dirs)
            self.items.extend(files)
            
            # Reset selection if out of bounds
            if self.selected_item >= len(self.items):
                self.selected_item = max(0, len(self.items) - 1)
                
        except PermissionError:
            self.items = ["[Permission Denied]"]
        except Exception as e:
            self.items = [f"[Error: {str(e)}]"]
    
    def draw(self):
        """Draw the file browser window"""
        height, width = self.stdscr.getmaxyx()
        
        # Calculate browser window dimensions (leave space for borders and status)
        browser_height = height - 8
        browser_width = width - 4
        start_y = 3
        start_x = 2
        
        if browser_height < 3 or browser_width < 10:
            return False  # Terminal too small
        
        # Clear the area
        for y in range(start_y, start_y + browser_height + 2):
            try:
                self.stdscr.move(y, start_x)
                self.stdscr.clrtoeol()
            except curses.error:
                pass
        
        # Draw border
        try:
            # Top border
            self.stdscr.addstr(start_y - 1, start_x, "┌" + "─" * (browser_width - 2) + "┐")
            # Bottom border
            self.stdscr.addstr(start_y + browser_height, start_x, "└" + "─" * (browser_width - 2) + "┘")
            # Side borders
            for y in range(start_y, start_y + browser_height):
                self.stdscr.addstr(y, start_x, "│")
                self.stdscr.addstr(y, start_x + browser_width - 1, "│")
        except curses.error:
            pass
        
        # Draw title
        title = f" File Browser: {os.path.basename(self.current_dir) or self.current_dir} "
        title_x = start_x + (browser_width - len(title)) // 2
        try:
            self.stdscr.addstr(start_y - 1, title_x, title, curses.A_BOLD)
        except curses.error:
            pass
        
        # Draw current path
        path_display = self.current_dir
        if len(path_display) > browser_width - 6:
            path_display = "..." + path_display[-(browser_width - 9):]
        try:
            self.stdscr.addstr(start_y, start_x + 1, f" {path_display} ", curses.A_DIM)
        except curses.error:
            pass
        
        # Draw file list
        content_height = browser_height - 2  # Leave space for path and instructions
        visible_items = min(len(self.items), content_height)
        
        # Adjust top_item to keep selected item visible
        if self.selected_item < self.top_item:
            self.top_item = self.selected_item
        elif self.selected_item >= self.top_item + visible_items:
            self.top_item = self.selected_item - visible_items + 1
        
        # Draw items
        for i in range(visible_items):
            item_index = self.top_item + i
            if item_index >= len(self.items):
                break
                
            item = self.items[item_index]
            y = start_y + 1 + i
            
            # Truncate item name if too long
            display_item = item
            max_item_width = browser_width - 4
            if len(display_item) > max_item_width:
                display_item = display_item[:max_item_width - 3] + "..."
            
            # Highlight selected item
            attr = curses.A_REVERSE if item_index == self.selected_item else 0
            
            # Add different colors for directories and files
            if item.startswith("[") and item.endswith("]"):
                if item == "[..]":
                    attr |= curses.A_DIM
                else:
                    attr |= curses.A_BOLD
            
            try:
                self.stdscr.addstr(y, start_x + 1, f" {display_item.ljust(max_item_width)} ", attr)
            except curses.error:
                pass
        
        # Draw instructions
        instructions = "↑↓: Navigate | Enter: Select/Open | Esc: Cancel | Backspace: Parent Dir"
        try:
            self.stdscr.addstr(start_y + browser_height + 1, start_x, 
                             instructions[:browser_width], curses.A_DIM)
        except curses.error:
            pass
        
        return True
    
    def handle_key(self, key):
        """Handle keyboard input for file browser"""
        if key == curses.KEY_UP:
            if self.selected_item > 0:
                self.selected_item -= 1
        elif key == curses.KEY_DOWN:
            if self.selected_item < len(self.items) - 1:
                self.selected_item += 1
        elif key == curses.KEY_BACKSPACE or key == 127:
            # Go to parent directory
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir != self.current_dir:  # Prevent infinite loop at root
                self.current_dir = parent_dir
                self.refresh_items()
                self.selected_item = 0
                self.top_item = 0
        elif key in [ord('\n'), curses.KEY_ENTER]:  # Enter key
            if self.items and self.selected_item < len(self.items):
                selected = self.items[self.selected_item]
                
                if selected == "[..]":
                    # Go to parent directory
                    parent_dir = os.path.dirname(self.current_dir)
                    if parent_dir != self.current_dir:
                        self.current_dir = parent_dir
                        self.refresh_items()
                        self.selected_item = 0
                        self.top_item = 0
                elif selected.startswith("[") and selected.endswith("]"):
                    # Directory selected
                    dir_name = selected[1:-1]  # Remove brackets
                    new_path = os.path.join(self.current_dir, dir_name)
                    if os.path.isdir(new_path):
                        self.current_dir = new_path
                        self.refresh_items()
                        self.selected_item = 0
                        self.top_item = 0
                else:
                    # File selected - return the full path
                    return os.path.join(self.current_dir, selected)
        elif key == 27:  # Escape key
            return "CANCEL"
        
        return None
    
    def handle_mouse(self, mx, my):
        """Handle mouse input for file browser"""
        height, width = self.stdscr.getmaxyx()
        start_y = 3
        start_x = 2
        browser_height = height - 8
        
        # Check if click is within browser window
        if (start_y + 1 <= my < start_y + browser_height - 1 and 
            start_x + 1 <= mx < start_x + width - 6):
            
            # Calculate which item was clicked
            clicked_item = self.top_item + (my - start_y - 1)
            if 0 <= clicked_item < len(self.items):
                if clicked_item == self.selected_item:
                    # Double-click effect - select the item
                    return self.handle_key(ord('\n'))
                else:
                    # Single click - just select
                    self.selected_item = clicked_item
        
        return None

class Menu:
    def __init__(self, items):
        self.items = items
        self.current_item = 0
        self.current_submenu_item = 0
        self.open = False
        self.submenus = {
            "File": ["New", "Open", "Save", "Save as", "Exit"],            
            "Edit": ["Undo", "Redo", "Cut", "Copy", "Paste"],
            "Menu": ["Toggle Line Numbers", "Change Theme"],
            "Help": ["User Manual", "About"]
        }

    def display(self, stdscr, start_y, start_x):
        height, width = stdscr.getmaxyx()
        for idx, item in enumerate(self.items):
            # Display with padding for visual separation
            display_item = f" {item} "
            x_pos = start_x + idx * 10
            
            # Check boundaries before drawing
            if start_y < height and x_pos + len(display_item) < width:
                if idx == self.current_item:
                    stdscr.attron(curses.A_REVERSE)
                try:
                    stdscr.addstr(start_y, x_pos, display_item)
                except curses.error:
                    pass  # Skip if can't draw
                if idx == self.current_item:
                    stdscr.attroff(curses.A_REVERSE)
        
        if self.open:
            self.display_submenu(stdscr, start_y + 1, start_x + self.current_item * 10)

    def display_submenu(self, stdscr, start_y, start_x):
        height, width = stdscr.getmaxyx()
        submenu_items = self.submenus[self.items[self.current_item]]
        max_len = max(len(s) for s in submenu_items) + 2 # For padding
        
        for idx, item in enumerate(submenu_items):
            y_pos = start_y + idx
            # Check boundaries before drawing submenu
            if y_pos < height - 3:  # Leave room for status bars
                # Add padding to create a clean dropdown box
                display_item = f" {item.ljust(max_len - 2)} "
                # Truncate if it would exceed screen width
                if start_x + len(display_item) >= width:
                    display_item = display_item[:width - start_x - 1]
                
                # NEW: Highlight current submenu item
                if idx == self.current_submenu_item:
                    stdscr.attron(curses.A_REVERSE)
                
                try:
                    stdscr.addstr(y_pos, start_x, display_item)
                except curses.error:
                    pass  # Skip if can't draw
                
                if idx == self.current_submenu_item:
                    stdscr.attroff(curses.A_REVERSE)

    def handle_mouse(self, mx, my):
        if my == 0:  # Menu bar clicked
            selected_item_idx = mx // 10
            if selected_item_idx < len(self.items):
                if self.open and self.current_item == selected_item_idx:
                    self.open = False
                else:
                    self.current_item = selected_item_idx
                    self.current_submenu_item = 0  # NEW: Reset submenu selection
                    self.open = True
            else:
                self.open = False
        elif self.open: # Submenu clicked
            submenu_items = self.submenus[self.items[self.current_item]]
            clicked_item_idx = my - 1
            if 0 <= clicked_item_idx < len(submenu_items):
                self.current_submenu_item = clicked_item_idx  # NEW: Update submenu selection
                # We return the clean item name now, without spaces
                return f"{self.items[self.current_item]}:{submenu_items[clicked_item_idx]}"
        return None

    def handle_key(self, key):
        # Keyboard navigation
        if key == ord('\n'):
            if self.open:
                submenu_items = self.submenus[self.items[self.current_item]]
                # Return the currently selected submenu item
                return f"{self.items[self.current_item]}:{submenu_items[self.current_submenu_item]}"
            else:
                self.open = True
                self.current_submenu_item = 0  # Reset submenu selection when opening
        elif key == curses.KEY_LEFT:
            if self.open:
                # Navigate to previous menu item and reset submenu selection
                self.current_item = (self.current_item - 1) % len(self.items)
                self.current_submenu_item = 0
            else:
                self.current_item = (self.current_item - 1) % len(self.items)
        elif key == curses.KEY_RIGHT:
            if self.open:
                # Navigate to next menu item and reset submenu selection
                self.current_item = (self.current_item + 1) % len(self.items)
                self.current_submenu_item = 0
            else:
                self.current_item = (self.current_item + 1) % len(self.items)
        elif key == curses.KEY_UP and self.open:
            # Navigate up in submenu
            submenu_items = self.submenus[self.items[self.current_item]]
            self.current_submenu_item = (self.current_submenu_item - 1) % len(submenu_items)
        elif key == curses.KEY_DOWN and self.open:
            # Navigate down in submenu
            submenu_items = self.submenus[self.items[self.current_item]]
            self.current_submenu_item = (self.current_submenu_item + 1) % len(submenu_items)
        elif key == 27:  # ESC key - close menu
            self.open = False
            return "CLOSE_MENU"  # Special signal to close menu
        
        return None

class TextEditor:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.content = ['']
        self.cursor_y = 0
        self.cursor_x = 0
        self.top_line = 0
        self.left_col = 0 # Horizontal scrolling
        self.current_file = None
        self.message = ""
        self.color_theme = "default"
        self.menu = Menu(["File", "Edit", "Menu", "Help"])
        self.show_line_numbers = False
        self.menu_focus = False
        self.formatter = None
        self.file_browser = None
        self.browser_mode = False
        self.selection_start = None
        self.selection_end = None
        
        #Initialize prev_key and a counter for the escape sequence
        self.escape_counter = 0

        # Copy and Paste, Cut
        self.context_menu_active = False
        self.context_menu_pos = (0, 0)
        self.context_menu_items = ["Undo", "Redo", "Cut", "Copy", "Paste"]
        self.selected_context_menu_item = 0

        # State for Undo/Redo functionality
        self.history = []
        self.redo_stack = []

        self.read_only = False
        self._save_state() # Save the initial empty state

    def setup_colors(self):
        """Sets up colors for syntax highlighting"""
        curses.start_color()
        curses.use_default_colors()
        self.formatter = CursesFormatter(style=self.color_theme)
        self.formatter.setup_colors()

        # --- Set the window's background color ---
        try:
            # Pygments styles have a default foreground for plain text
            default_fg = self.formatter.hex_to_curses_color(self.formatter.style.style_for_token(Token)['color'])
            curses.init_pair(255, default_fg, self.formatter.background_color_index)
            self.stdscr.bkgd(' ', curses.color_pair(255))
        except:
            # Fallback if the style is unusual
            self.stdscr.bkgd(' ', curses.A_NORMAL)

    def run(self):
        # Initial setup
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        self.stdscr.nodelay(1)

        # Enable raw mode to capture Ctrl+C
        curses.raw()

        self.setup_colors()

        while True:
            # Hide cursor if in menu or browser mode, otherwise show it.
            if self.menu_focus or self.browser_mode or self.context_menu_active:
                curses.curs_set(0)
            else:
                curses.curs_set(1)

            # Main draw loop
            if self.browser_mode:
                self.draw_browser_interface()
            else:
                self.draw_interface()

            # Refresh screen before handling input
            self.stdscr.refresh()

            # Handle user input
            self.handle_input()
            curses.napms(10)

    def draw_browser_interface(self):
        """Draw the file browser interface"""
        self.stdscr.erase()
        
        if self.file_browser and self.file_browser.draw():
            pass  # Browser drew successfully
        else:
            # Browser couldn't draw (terminal too small), show error and exit browser
            try:
                self.stdscr.addstr(1, 1, "Terminal too small for file browser.")
                self.stdscr.addstr(2, 1, "Press any key to return to editor.")
            except curses.error:
                pass
        
        self.stdscr.refresh()

    def draw_interface(self):
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        
        # Ensure minimum terminal size
        if height < 6 or width < 20:
            try:
                self.stdscr.addstr(0, 0, "Terminal too small.")
                self.stdscr.refresh()
            except curses.error:
                pass
            return
            
        line_num_width = 5 if self.show_line_numbers else 0

        # Draw content with syntax highlighting
        self.draw_content(height, width, line_num_width)
        
        # Draw menu over the content
        self.menu.display(self.stdscr, 0, 0)


        # Draw the context menu if it is active
        if self.context_menu_active:
            self.draw_context_menu()

        # Draw status bars
        status = f"File: {self.current_file or 'Untitled'} | Ln {self.cursor_y + 1}, Col {self.cursor_x + 1} | Theme: {self.color_theme}"

        if self.menu_focus:
            help_text = "MENU MODE: ←→ Select Menu | ↑↓ Navigate Items | Enter: Select | Esc: Close | F9: Edit Mode | Click text to edit"
        else:
            help_text = "F1: Open | F2: Save | F3: New | F4: Theme | F5: Line Num | F9: Menu | Esc x3: Quit"
        
        try:
            self.stdscr.attron(curses.A_REVERSE)

            # Ensure status strings fit within screen boundaries
            if width > 1:
                # Truncate strings if they're too long for the screen
                status_line = (status[:width-1] if len(status) >= width else status).ljust(width - 1)
                message_line = (self.message[:width-1] if len(self.message) >= width else self.message).ljust(width - 1)
                help_line = (help_text[:width-1] if len(help_text) >= width else help_text).ljust(width - 1)

                # Only draw if we have enough vertical space
                if height >= 4:
                    self.stdscr.addstr(height - 3, 0, status_line)
                if height >= 3:
                    self.stdscr.addstr(height - 2, 0, message_line)
                if height >= 2:
                    self.stdscr.addstr(height - 1, 0, help_line)

            self.stdscr.attroff(curses.A_REVERSE)

            # Add mode indicator (also check width and height)
            #if width > 10 and height >= 4: # No need to check for width
            if height >= 4:
                mode = "Mode: MENU" if self.menu_focus else "Mode: EDIT"
                mode_text = f" {mode} "
                # Only draw the mode text if there is enough horizontal space for it.
                if width > len(mode_text):
                    self.stdscr.addstr(height - 3, width - len(mode_text), mode_text)
                    
        except curses.error:
            # If we can't draw status bars, continue anyway
            pass

        # Call the position of the cursor
        self.position_cursor(height, width, line_num_width)

    def draw_context_menu(self):
        y, x = self.context_menu_pos
        max_len = max(len(s) for s in self.context_menu_items) + 2
        
        for i, item in enumerate(self.context_menu_items):
            try:
                self.stdscr.addstr(y + i, x, f" {item.ljust(max_len - 2)} ", curses.A_REVERSE)
            except curses.error:
                pass # Don't draw if it goes off-screen

    def position_cursor(self, height, width, line_num_width):
        """Comprehensive bounds checking"""
        try:
            # Calculate cursor screen position
            screen_y = self.cursor_y - self.top_line + 1
            screen_x = (self.cursor_x - self.left_col) + line_num_width  # Adjust for horizontal offset
            
            # Ensure cursor is within valid screen boundaries
            if (screen_y >= 1 and screen_y < height - 3 and  # Leave room for status bars
                screen_x >= line_num_width and screen_x < width):
                self.stdscr.move(screen_y, screen_x)
            else:
                # If cursor would be off-screen, place it at a safe position
                safe_y = min(max(1, screen_y), height - 4)
                safe_x = min(max(line_num_width, screen_x), width - 1)
                self.stdscr.move(safe_y, safe_x)
        except curses.error:
            # Last resort: try to place cursor at top-left of content area
            try:
                self.stdscr.move(1, line_num_width)
            except curses.error:
                pass  # Give up on cursor positioning

    def _ensure_cursor_visible(self):
        """Adjusts self.top_line to make sure the cursor is on screen."""
        height, width = self.stdscr.getmaxyx()
        # The content area is the screen height minus the menu bar (1) and three status bars (3).
        content_height = height - 4
        
        # Ensure content_height is at least 1
        if content_height < 1:
            content_height = 1
        
        # Vertical scrolling
        if self.cursor_y < self.top_line:
            self.top_line = self.cursor_y
        elif self.cursor_y >= self.top_line + content_height:
            self.top_line = self.cursor_y - content_height + 1
        
        # Horizontal scrolling
        line_num_width = 5 if self.show_line_numbers else 0
        available_width = width - line_num_width - 1  # Leave 1 for safety
        
        if available_width > 0:
            # Scroll left if cursor is before visible area
            if self.cursor_x < self.left_col:
                self.left_col = self.cursor_x
            # Scroll right if cursor is after visible area
            elif self.cursor_x >= self.left_col + available_width:
                self.left_col = self.cursor_x - available_width + 1

    def draw_content(self, height, width, line_num_width):
        """Handles drawing text with syntax highlighting and selection."""
        content_height = height - 4
        
        if content_height <= 0 or width <= line_num_width:
            return
        
        try:
            lexer = guess_lexer_for_filename(self.current_file or 'text.txt', "".join(self.content))
        except:
            lexer = get_lexer_by_name("text")

        for i in range(content_height):
            line_idx = self.top_line + i
            screen_y = i + 1
            
            if screen_y >= height - 3:  # Stop drawing before status bars
                break
                
            if line_idx < len(self.content):
                try:
                    if self.show_line_numbers and line_num_width <= width:
                        self.stdscr.addstr(screen_y, 0, f"{line_idx + 1:4d} ", curses.A_DIM)
                    
                    line = self.content[line_idx]
                    available_width = width - line_num_width - 1
                    if available_width <= 0: 
                        continue

                    # Apply horizontal offset to the line
                    visible_line = line[self.left_col:self.left_col + available_width + 100]

                    # 1. Get a list of (text, attribute) tokens for visible items
                    if self.formatter:
                        token_stream = lex(visible_line, lexer)
                        tokens = self.formatter.format(token_stream, None)
                    else:
                        # If no formatter, treat the whole line as one token with default attribute
                        tokens = [(visible_line, 0)]

                    # 2. Unified drawing loop that handles all cases
                    x_pos = line_num_width
                    line_x_pos = self.left_col # Tracks position in the actual line data

                    for text, attr in tokens:
                        if x_pos >= width - 1: 
                            break

                        # Truncate token text if it would go past the edge of the screen
                        remaining_width = width - x_pos - 1
                        display_text = text[:remaining_width]

                        # Draw character by character to handle selection
                        if display_text:
                            for char_index, char_to_draw in enumerate(display_text):
                                doc_char_x = line_x_pos + char_index
                                
                                final_attr = attr
                                if self.is_selected(line_idx, doc_char_x):
                                    final_attr |= curses.A_REVERSE # Add selection highlight

                                self.stdscr.addstr(screen_y, x_pos + char_index, char_to_draw, final_attr)
                            
                            x_pos += len(display_text)
                        
                        # Always advance the document position by the original token length
                        line_x_pos += len(text)
                        
                except curses.error:
                    continue
      
    def open_user_manual(self):
        """Opens the user_manual.txt file in a new, read-only buffer."""
        try:
            # Assume user_manual.txt is in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            manual_path = os.path.join(script_dir, "user_manual.txt")

            if not os.path.exists(manual_path):
                self.message = "user_manual.txt not found."
                return

            with open(manual_path, 'r', encoding='utf-8') as f:
                content_lines = f.read().splitlines()

            # Load the content into the editor
            self.content = content_lines if content_lines else ['']
            self.current_file = "User Manual (Read-Only)"
            self.cursor_y, self.cursor_x, self.top_line = 0, 0, 0
            
            # Set the read-only flag
            self.read_only = True
            
            self.message = "Opened User Manual. Press F3 for a new file to exit."
            self.setup_colors()
            
            # Clear history for this new buffer
            self.history = []
            self.redo_stack = []
            self._save_state()

        except Exception as e:
            self.message = f"Error opening manual: {e}"

    

    def _save_state(self):
        """Saves a snapshot of the current content with deepcopy for undo."""
        snapshot = {
            'content': copy.deepcopy(self.content),
            'cursor_y': self.cursor_y,
            'cursor_x': self.cursor_x
        }
        self.history.append(snapshot)
        # Any new action clears the redo stack
        self.redo_stack = []

    def _restore_state(self, state):
        """Restores the editor's content and cursor from a snapshot."""
        self.content = copy.deepcopy(state['content'])
        self.cursor_y = state['cursor_y']
        self.cursor_x = state['cursor_x']
        self._ensure_cursor_visible()

    def undo(self):
        """Performs an undo operation."""
        if len(self.history) > 1: # Must be more than the initial state
            # Save current state for a potential redo
            current_state = self.history.pop()
            self.redo_stack.append(current_state)
            
            # Restore the previous state
            last_state = self.history[-1]
            self._restore_state(last_state)
            self.message = "Undo performed."
        else:
            self.message = "Nothing to undo."

    def redo(self):
        """Performs a redo operation."""
        if self.redo_stack:
            state_to_restore = self.redo_stack.pop()
            # Push this state back to the history so we can undo it again
            self.history.append(state_to_restore)
            self._restore_state(state_to_restore)
            self.message = "Redo performed."
        else:
            self.message = "Nothing to redo."

    def handle_input(self):
        """Handle context menu state. If is active, capture..."""
        if self.context_menu_active:
            key = self.stdscr.getch()
            if key == curses.KEY_MOUSE:
                _, mx, my, _, bstate = curses.getmouse()
                # Check if click is on a menu item
                cy, cx = self.context_menu_pos
                max_len = max(len(s) for s in self.context_menu_items) + 2
                if cy <= my < cy + len(self.context_menu_items) and cx <= mx < cx + max_len:
                    item_clicked = self.context_menu_items[my - cy]
                    if item_clicked == "Copy": self.copy_text()
                    elif item_clicked == "Cut": self.cut_text()
                    elif item_clicked == "Paste": self.paste_text()
                # Any click closes the menu
                self.context_menu_active = False
            elif key == 27: # Escape key
                self.context_menu_active = False
            return

        key = self.stdscr.getch()
        if key == -1: return

        # New top-level check for browser mode
        if self.browser_mode:
            self.handle_browser_input(key)
            return

        # The rest of the logic is for editor/menu mode
        if key == 27:
            if self.menu.open:
                self.handle_menu_input(key)
                return
            self.escape_counter += 1
            if self.escape_counter == 3:
                sys.exit(0)
            return
        else:
            self.escape_counter = 0

        if key == curses.KEY_F9:
            self.menu_focus = not self.menu_focus
            self.message = "Menu navigation enabled." if self.menu_focus else "Text editing mode."
            self.menu.open = False
            return

        if self.menu_focus:
            self.handle_menu_input(key)
        else:
            self.handle_editor_input(key)

    def handle_browser_input(self, key):
        if not self.file_browser:
            self.browser_mode = False # Safety exit
            return
        
        result = None
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, _ = curses.getmouse()
                result = self.file_browser.handle_mouse(mx, my)
            except curses.error:
                pass
        else:
            result = self.file_browser.handle_key(key)

        if result:
            self.browser_mode = False # Exit browser mode on any action
            self.file_browser = None  # Clean up the browser instance

            if result == "CANCEL":
                self.message = "Open file cancelled."
            else: # A filename was returned
                self._load_file_content(result)

    def handle_menu_input(self, key):
        action = None
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, _ = curses.getmouse()
                height, width = self.stdscr.getmaxyx()

                # --- MOUSE HANDLING ---
                # First, let the Menu object try to handle the click.
                action = self.menu.handle_mouse(mx, my)

                # If the menu didn't handle it, it was a click outside the menu.
                if action is None:
                    # Check if the click was in the text area.
                    if my > 0 and my < height - 3:
                        self.menu_focus = False
                        self.menu.open = False
                        self.message = "Returned to editing mode."
                        # Place cursor at the clicked location
                        line_num_width = 5 if self.show_line_numbers else 0
                        clicked_y = min(max(0, self.top_line + my - 1), len(self.content) - 1)
                        self.cursor_y = clicked_y
                        if 0 <= clicked_y < len(self.content):
                            self.cursor_x = min(max(0, mx - line_num_width), len(self.content[clicked_y]))
                        else:
                            self.cursor_x = 0
                        self.clear_selection()
                        return # Event handled, no more processing needed
            except curses.error:
                action = None
        
        elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, ord('\n'), 27]:
            action = self.menu.handle_key(key)
        
        if action:
            if action == "CLOSE_MENU":
                self.menu.open = False
                self.menu_focus = False
                self.message = "Returned to editing mode."
            else:
                self.handle_menu_action(action)
    
    def handle_editor_input(self, key):
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                height, width = self.stdscr.getmaxyx()
                
                # Handle right-click to open context menu
                if bstate & curses.BUTTON3_CLICKED or bstate & curses.BUTTON3_PRESSED:
                    self.context_menu_active = True
                    # Clamp menu position to stay on screen
                    menu_width = max(len(s) for s in self.context_menu_items) + 2
                    menu_y = my
                    if menu_y + len(self.context_menu_items) >= height - 2:
                         menu_y = height - 3 - len(self.context_menu_items)
                    menu_x = mx
                    if menu_x + menu_width >= width:
                        menu_x = width - menu_width - 1
                    self.context_menu_pos = (max(0, menu_y), max(0, menu_x))
                    return

                # Handle left-click actions in the content area
                if my > 0 and my < height - 2:
                    line_num_width = 5 if self.show_line_numbers else 0
                    clicked_y = min(max(0, self.top_line + my - 1), len(self.content) - 1)
                    clicked_x = min(max(0, mx - line_num_width), len(self.content[clicked_y]))

                    if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                        self.clear_selection()
                        self.cursor_y, self.cursor_x = clicked_y, clicked_x
                        self.selection_start = (self.cursor_y, self.cursor_x)
                        self.selection_end = self.selection_start
                        return
                    if bstate & curses.REPORT_MOUSE_POSITION and self.selection_start is not None:
                        self.cursor_y, self.cursor_x = clicked_y, clicked_x
                        self.selection_end = (self.cursor_y, self.cursor_x)
                        return
                    if bstate & curses.BUTTON1_RELEASED and self.selection_start is not None:
                        self.cursor_y, self.cursor_x = clicked_y, clicked_x
                        self.selection_end = (self.cursor_y, self.cursor_x)
                        if self.selection_start == self.selection_end: self.clear_selection()
                        return

                # Handle clicks on the menu bar
                if my == 0:
                    self.menu_focus = True; self.message = "Menu Mode"
                    action = self.menu.handle_mouse(mx, my)
                    if action: self.handle_menu_action(action)
                    return
                
                # Handle scroll wheel
                if bstate & curses.BUTTON4_PRESSED: self.scroll_up(); return
                if bstate & curses.BUTTON5_PRESSED: self.scroll_down(); return
            except curses.error: pass
        
        # --- Keyboard Input Logic ---

        # Ctrl keys (for copy/paste/cut)
        elif key == 26: self.undo()
        elif key == 25: self.redo()
        elif key == 3: self.copy_text()
        elif key == 22: self.paste_text()
        elif key == 24: self.cut_text()

        # Selection keys (Shift + Arrows)
        elif key == curses.KEY_SLEFT: self._start_or_extend_selection(0, -1)
        elif key == curses.KEY_SRIGHT: self._start_or_extend_selection(0, 1)
        elif key == curses.KEY_SR: self._start_or_extend_selection(-1, 0)  # Shift+Up
        elif key == curses.KEY_SF: self._start_or_extend_selection(1, 0)   # Shift+Down

        # Standard cursor movement keys (these clear the selection)
        elif key == curses.KEY_UP:
            self.clear_selection()
            self.move_cursor(-1, 0)
        elif key == curses.KEY_DOWN:
            self.clear_selection()
            self.move_cursor(1, 0)
        elif key == curses.KEY_LEFT:
            self.clear_selection()
            self.move_cursor(0, -1)
        elif key == curses.KEY_RIGHT:
            self.clear_selection()
            self.move_cursor(0, 1)
        elif key == curses.KEY_NPAGE:
            self.clear_selection()
            height, _ = self.stdscr.getmaxyx()
            self.move_cursor(height - 3, 0)
        elif key == curses.KEY_PPAGE:
            self.clear_selection()
            height, _ = self.stdscr.getmaxyx()
            self.move_cursor(-(height - 3), 0)
            
        # Editing keys
        elif key in [ord('\n'), ord('\r'), curses.KEY_ENTER, 459]:
            self.insert_newline()
        elif key in [curses.KEY_BACKSPACE, 127, 8]: 
            self.backspace()
        elif key == curses.KEY_DC: 
            self.delete_forward()
        elif key == ord('\t'):  # Tab key
            self.insert_tab()
            
        # Function keys
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
            self.message = f"Line numbers turned {'on' if self.show_line_numbers else 'off'}."
        
        # Character input (also acts on selection)
        elif 32 <= key <= 126:
            self.insert_char(chr(key))

    def clear_selection(self):
        """Clears any active text selection."""
        self.selection_start = None
        self.selection_end = None

    def _start_or_extend_selection(self, dy, dx):
        """Initializes or extends a selection based on cursor movement."""
        # If no selection is active, start a new one at the current cursor position
        if self.selection_start is None:
            self.selection_start = (self.cursor_y, self.cursor_x)

        # Move the cursor using the existing logic
        self.move_cursor(dy, dx)

        # Update the end of the selection to the new cursor position
        self.selection_end = (self.cursor_y, self.cursor_x)

    def is_selected(self, y, x):
        """Checks if a given coordinate (y, x) is within the current selection."""
        if not self.selection_start or not self.selection_end:
            return False

        # Normalize coordinates so start is always before end
        # This allows selecting text from bottom-to-top or right-to-left
        start_pos = min(self.selection_start, self.selection_end)
        end_pos = max(self.selection_start, self.selection_end)

        # The character's position as a tuple
        char_pos = (y, x)

        # Check if the character's position is between the start and end of the selection
        return start_pos <= char_pos < end_pos

    def get_selected_text(self):
        if not self.selection_start: return ""
        start, end = min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)
        y1, x1 = start
        y2, x2 = end
        
        if y1 == y2:
            return self.content[y1][x1:x2]
        else:
            lines = []
            lines.append(self.content[y1][x1:])
            for i in range(y1 + 1, y2):
                lines.append(self.content[i])
            lines.append(self.content[y2][:x2])
            return "\n".join(lines)

    def delete_selected_text(self, save_state=True):
        """Deletes the highlighted text and correctly repositions/scrolls the view."""
        if not self.selection_start: 
            return

        if save_state:
            self._save_state()

        start, end = min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)
        y1, x1 = start
        y2, x2 = end
        
        # Bounds checking - ensure indices are valid
        if y1 >= len(self.content) or y2 >= len(self.content):
            self.clear_selection()
            self.message = "Invalid selection range"
            return
        
        # Clamp x positions to line lengths
        x1 = min(x1, len(self.content[y1]))
        x2 = min(x2, len(self.content[y2]))
        
        if y1 == y2:
            # Simple case: deletion is on a single line.
            self.content[y1] = self.content[y1][:x1] + self.content[y1][x2:]
        else:
            # Multi-line case: Merge start of first line with end of last line.
            self.content[y1] = self.content[y1][:x1] + self.content[y2][x2:]
            
            # Delete all the lines that were in between.
            del self.content[y1 + 1 : y2 + 1]

        # Ensure the document is never completely empty, which would cause a crash.
        if not self.content:
            self.content = ['']

        # Correctly move the cursor to the start of the former selection
        self.cursor_y, self.cursor_x = y1, x1
        self.clear_selection()
        
        # Ensure the view scrolls if the deletion happened off-screen
        self._ensure_cursor_visible()
    
    def copy_text(self):
        selected_text = self.get_selected_text()
        if selected_text:
            try:
                pyperclip.copy(selected_text)
                self.message = "Text copied to clipboard."
            except Exception as e:
                self.message = f"Copy failed: {e}"

    
    def cut_text(self):
        if self._check_read_only(): return
        if not self.selection_start:
            return
        self._save_state()
        selected_text = self.get_selected_text()
        if selected_text:
            try:
                pyperclip.copy(selected_text)
                self.delete_selected_text()
                self.message = "Text cut to clipboard."
            except Exception as e:
                self.message = f"Cut failed: {e}"

    def paste_text(self):
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text()
        
        try:
            text_to_paste = pyperclip.paste()
            if not text_to_paste:
                self.message = "Clipboard is empty."
                return
            
            lines_to_paste = text_to_paste.splitlines()
            if not lines_to_paste:
                self.message = "No valid text to paste."
                return
                
            current_line = self.content[self.cursor_y]
            
            # First line of paste is merged with current line
            first_line_of_paste = lines_to_paste[0]
            self.content[self.cursor_y] = current_line[:self.cursor_x] + first_line_of_paste
            
            # If there are more lines, handle them
            if len(lines_to_paste) > 1:
                # The part of the original line after the cursor
                end_of_current_line = current_line[self.cursor_x:]
                
                # The very last line of the paste
                last_line_of_paste = lines_to_paste[-1]
                
                # Insert the middle lines
                for i, line in enumerate(lines_to_paste[1:-1]):
                    self.content.insert(self.cursor_y + 1 + i, line)
                
                # Insert the last line, appending the end of the original line
                self.content.insert(self.cursor_y + len(lines_to_paste) - 1, last_line_of_paste + end_of_current_line)
                
                # Move cursor to the end of the paste
                self.cursor_y += len(lines_to_paste) - 1
                self.cursor_x = len(last_line_of_paste)
            else:
                # Only one line was pasted, move cursor to the end of it
                self.cursor_x += len(first_line_of_paste)
            
            self.message = "Pasted from clipboard."
            
        except Exception as e:
            import traceback
            self.message = f"Paste failed: {str(e)}"
            with open("debug_log.txt", "a") as f:
                f.write(f"Paste error: {str(e)}\n")
                traceback.print_exc(file=f)

    def scroll_up(self, lines=3):
        """Scroll the view up by the specified number of lines"""
        if self.top_line > 0:
            self.top_line = max(0, self.top_line - lines)
            # Keep cursor visible on screen
            height, _ = self.stdscr.getmaxyx()
            content_height = height - 4
            max_visible_line = self.top_line + content_height - 1
            if self.cursor_y > max_visible_line:
                self.cursor_y = max_visible_line
                # Ensure cursor doesn't go past the end of content
                self.cursor_y = min(self.cursor_y, len(self.content) - 1)
                # Ensure cursor x position is valid for the new line
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))

    def scroll_down(self, lines=3):
        """Scroll the view down by the specified number of lines"""
        height, _ = self.stdscr.getmaxyx()
        content_height = height - 4
        max_top_line = max(0, len(self.content) - content_height)
        
        if self.top_line < max_top_line:
            self.top_line = min(max_top_line, self.top_line + lines)
            # Keep cursor visible on screen
            if self.cursor_y < self.top_line:
                self.cursor_y = self.top_line
                # Ensure cursor doesn't go past the end of content
                self.cursor_y = min(self.cursor_y, len(self.content) - 1)
                # Ensure cursor x position is valid for the new line
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))


    def handle_menu_action(self, action):
        # Strip whitespace from menu item for correct matching
        menu, item = action.split(':', 1)
        item = item.strip()
        self.menu.open = False
        self.menu_focus = False

        if menu == "File":
            if item == "New": 
                self.new_file()
            elif item == "Open": 
                self.open_file()
            elif item == "Save": 
                self.save_file()
            elif item == "Save as":
                self.save_file(save_as=True)
            elif item == "Exit": 
                sys.exit(0)
            # Close menu after file operations
            self.menu.open = False
            self.menu_focus = False
            
        elif menu == "Edit":
            if item == "Undo": self.undo()
            elif item == "Redo": self.redo()
            elif item == "Cut": self.cut_text()
            elif item == "Copy": self.copy_text()
            elif item == "Paste": self.paste_text()
            # Close menu after edit operations
            self.menu.open = False
            self.menu_focus = False
            
        elif menu == "Menu":
            if item == "Toggle Line Numbers":
                self.show_line_numbers = not self.show_line_numbers
                self.message = f"Line numbers turned {'on' if self.show_line_numbers else 'off'}."
            elif item == "Change Theme":
                self.change_theme()
            # Close menu after menu operations
            self.menu.open = False
            self.menu_focus = False
            
        elif menu == "Help":
            if item == "User Manual":
                self.open_user_manual()
            elif item == "About":
                self.message = "ABOUT: TE (Text Editor) Version 9 - It's getting better."
            # Close menu after help
            self.menu.open = False
            self.menu_focus = False

    def move_cursor(self, dy, dx):
        """Moves the cursor and ensures it's visible."""
        # Calculate new y position
        new_y = max(0, min(self.cursor_y + dy, len(self.content) - 1))
            
        # If moving to a different line, reset horizontal scroll
        if new_y != self.cursor_y and dy != 0:
            self.left_col = 0
        
        self.cursor_y = new_y
        
        # Calculate new x position, clamping to the new line's length
        new_x = self.cursor_x + dx
        
        # Handle wrapping to previous line when moving left at start of line
        if new_x < 0 and self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = len(self.content[self.cursor_y])
            self.left_col = 0  # Reset horizontal scroll
        # Handle wrapping to next line when moving right at end of line
        elif new_x > len(self.content[self.cursor_y]) and self.cursor_y < len(self.content) - 1:
            self.cursor_y += 1
            self.cursor_x = 0
            self.left_col = 0  # Reset horizontal scroll
        else:
            self.cursor_x = min(max(0, new_x), len(self.content[self.cursor_y]))
        
        # Ensure the view scrolls if necessary
        self._ensure_cursor_visible()

    def _check_read_only(self):
        """Helper to check for read-only mode and set a message."""
        if self.read_only:
            self.message = "Read-Only Mode. Cannot modify file."
            return True
        return False

    def insert_char(self, char):
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text(save_state=False)  # Ensure no double-save state
        line = self.content[self.cursor_y]
        self.content[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
        self.cursor_x += 1
        self._ensure_cursor_visible()

    def insert_tab(self):
        """Inserts a tab (as spaces) at the cursor position."""
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text(save_state=False)
        
        # Insert 4 spaces for a tab (you can change this number if you prefer)
        tab_spaces = "    "  # 4 spaces
        line = self.content[self.cursor_y]
        self.content[self.cursor_y] = line[:self.cursor_x] + tab_spaces + line[self.cursor_x:]
        self.cursor_x += len(tab_spaces)
        self._ensure_cursor_visible()
      
    def insert_newline(self):
        """Inserts a newline, deleting selected text and correctly scrolling."""
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text()

        line = self.content[self.cursor_y]
        
        # Split the line and insert the new part
        self.content[self.cursor_y] = line[:self.cursor_x]
        self.content.insert(self.cursor_y + 1, line[self.cursor_x:])
        
        # Move the cursor state
        self.cursor_y += 1
        self.cursor_x = 0
        
        # Ensure the view scrolls to the new line
        self._ensure_cursor_visible()

    def backspace(self):
        """Deletes the character to the left of the cursor (standard backspace)."""
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text(save_state=False)
            return
        if self.cursor_x > 0:
            line = self.content[self.cursor_y]
            self.content[self.cursor_y] = line[:self.cursor_x - 1] + line[self.cursor_x:]
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            prev_line_len = len(self.content[self.cursor_y - 1])
            self.content[self.cursor_y - 1] += self.content.pop(self.cursor_y)
            self.cursor_y -= 1
            self.cursor_x = prev_line_len
            self.left_col = 0  # Reset horizontal scroll when joining lines
            self._ensure_cursor_visible()

    def delete_forward(self):
        """Deletes the character at the cursor's position (standard delete key)."""
        if self._check_read_only(): return
        self._save_state()
        if self.selection_start:
            self.delete_selected_text()
            return
        line = self.content[self.cursor_y]
        if self.cursor_x < len(line):
            self.content[self.cursor_y] = line[:self.cursor_x] + line[self.cursor_x + 1:]
        elif self.cursor_y < len(self.content) - 1:
            self.content[self.cursor_y] += self.content.pop(self.cursor_y + 1)

    def save_file(self, save_as=False):
        """Save the current file with improved error handling and validation."""
        if self._check_read_only(): return
        filename_to_save = None
        
        if not save_as and self.current_file:
            filename_to_save = self.current_file
        else:
            filename_input = self.get_user_input("Save As: ")
            
            # Check if user cancelled with Escape
            if filename_input is None:
                self.message = "Save cancelled."
                return
                
            if filename_input.strip() == "":
                self.message = "Save cancelled - no filename provided."
                return
            
            filename_to_save = filename_input.strip()
            
            if os.path.exists(filename_to_save):
                if not self.get_user_confirmation(f"'{os.path.basename(filename_to_save)}' exists. Overwrite? (y/n)"):
                    self.message = "Save cancelled."
                    return
        
        if not filename_to_save:
            self.message = "Save cancelled - invalid filename."
            return
        
        try:
            valid_lines = [str(line) if line is not None else "" for line in self.content]
            content_to_save = '\n'.join(valid_lines)
            
            directory = os.path.dirname(filename_to_save)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(filename_to_save, 'w', encoding='utf-8', newline='') as f:
                f.write(content_to_save)
            
            self.current_file = filename_to_save
            self.message = f"Saved to '{os.path.basename(self.current_file)}'"
            self.setup_colors()

            self.history = []
            self.redo_stack = []
            self._save_state() # Clear history on save
            
        except PermissionError:
            self.message = f"Permission denied: Cannot write to '{os.path.basename(filename_to_save)}'."
        except OSError as e:
            self.message = f"OS Error: {e}"
        except Exception as e:
            self.message = f"An unexpected error occurred: {e}"

    def get_user_confirmation(self, prompt):
        """Displays a prompt and waits for a 'y' or 'n' response. Returns True for 'y', False otherwise."""
        self.stdscr.nodelay(0)
        response = False
        try:
            # Re-draw the interface to ensure the prompt is on a clean screen
            self.draw_interface()
            
            height, width = self.stdscr.getmaxyx()
            self.stdscr.attron(curses.A_REVERSE)
            # Display the prompt without extra justification
            self.stdscr.addstr(height - 2, 0, (prompt[:width-1]).ljust(width - 1))
            self.stdscr.attroff(curses.A_REVERSE)
            self.stdscr.refresh()

            # Clear any pending keystrokes
            curses.flushinp()
            
            # Get a single character, without echo
            key = self.stdscr.getch()
            
            # Check if the user pressed 'y' or 'Y'
            if key in [ord('y'), ord('Y')]:
                response = True
        except curses.error:
            pass # Ignore errors during confirmation
        finally:
            # Restore non-blocking input mode
            self.stdscr.nodelay(1)
        return response

    def open_file(self):
        start_dir = os.getcwd()
        if self.current_file:
            start_dir = os.path.dirname(self.current_file)
        
        self.file_browser = FileBrowser(self.stdscr, start_dir=start_dir)
        self.browser_mode = True
        self.message = "Opening file browser..."

      
    def _load_file_content(self, filename):
        """
        Loads file content by trying UTF-8 first, latin-1 fall back
        """
        # Validate the filename before trying to open it.
        if not (filename and os.path.exists(filename) and not os.path.isdir(filename)):
            if os.path.isdir(filename):
                self.message = f"Error: '{os.path.basename(filename)}' is a directory."
            elif filename:
                self.message = f"File not found: {filename}"
            else:
                self.message = "Open cancelled."
            return

        try:
            # Try to open with UTF-8, the modern standard.
            with open(filename, 'r', encoding='utf-8') as f:
                content_lines = f.read().splitlines()
            self.message = f"Opened {filename} (UTF-8)"

        except UnicodeDecodeError:
            # If UTF-8 fails, it's a legacy file. Fall back to 'latin-1'.
            try:
                with open(filename, 'r', encoding='latin-1') as f:
                    content_lines = f.read().splitlines()
                self.message = f"Opened {filename} (Decoded as Latin-1)"
            except Exception as e:
                # This would be a very unusual error, like a permission issue during the second read.
                self.message = f"Error opening file on fallback: {e}"
                return
        except Exception as e:
            # 4. Catch other file-related errors like permissions issues.
            self.message = f"Error opening file: {e}"
            return
            
        # 5. If we successfully loaded the content, update the editor's state.
        self.content = content_lines if content_lines else ['']
        self.current_file = filename
        self.read_only = False
        self.cursor_y, self.cursor_x, self.top_line = 0, 0, 0
        self.setup_colors() # Re-run syntax highlighting for the file type.
        self.history = []; self.redo_stack = []; self._save_state()

    def new_file(self):
        self.content = ['']
        self.current_file = None
        self.read_only = False
        self.cursor_y, self.cursor_x, self.top_line = 0, 0, 0
        self.message = "New file created."
        self.setup_colors()
        self.history = []; self.redo_stack = []; self._save_state()

    def change_theme(self):
        themes = sorted(list(get_all_styles()))
        try:
            current_index = themes.index(self.color_theme)
            next_index = (current_index + 1) % len(themes)
        except ValueError:
            next_index = 0 # Fallback if current theme isn't found
        self.color_theme = themes[next_index]
        self.message = f"Theme changed to {self.color_theme}"
        # We must re-initialize the formatter with the new style
        self.setup_colors()

    def get_user_input(self, prompt):
        """Enhanced user input with bounds checking, input handling, cancellation"""
        height, width = self.stdscr.getmaxyx()
        
        # Ensure we have enough space for input
        if height < 3 or width < len(prompt) + 5:
            return ""
        
        # Set a short escape delay (25ms) to distinguish ESC from escape sequences
        os.environ.setdefault('ESCDELAY', '25')
        
        # Use blocking mode for input
        self.stdscr.nodelay(False)

        try:
            input_line = height - 2
            user_input = ""
            cursor_pos = 0
            
            while True:
                # Clear and redraw the input line
                self.stdscr.move(input_line, 0)
                self.stdscr.clrtoeol()
                
                # Display the prompt with reverse video
                self.stdscr.attron(curses.A_REVERSE)
                self.stdscr.addstr(input_line, 0, prompt)
                self.stdscr.attroff(curses.A_REVERSE)
                
                # Display the current input
                display_text = user_input[:width - len(prompt) - 2]
                if display_text:
                    self.stdscr.addstr(input_line, len(prompt), display_text)
                
                # Position cursor
                self.stdscr.move(input_line, len(prompt) + cursor_pos)
                self.stdscr.refresh()
                
                # Get a single character
                try:
                    key = self.stdscr.getch()
                except:
                    continue

                # Handle escape key - check if it's really escape or start of sequence
                if key == 27:
                    # Set a very brief non-blocking check
                    self.stdscr.nodelay(True)
                    next_key = self.stdscr.getch()
                    self.stdscr.nodelay(False)
                    
                    if next_key == -1:
                        # No follow-up key, it's a real escape
                        return None
                    else:
                        # It's part of an escape sequence, put it back and continue
                        curses.ungetch(next_key)
                        continue
                
                # Handle enter key - confirm input
                if key in [10, 13, curses.KEY_ENTER]:
                    return user_input.strip()
                
                # Handle backspace
                elif key in [curses.KEY_BACKSPACE, 127, 8, 263]:
                    if cursor_pos > 0:
                        user_input = user_input[:cursor_pos-1] + user_input[cursor_pos:]
                        cursor_pos -= 1
                
               # Handle delete key
                elif key in [curses.KEY_DC, 330]:
                    if cursor_pos < len(user_input):
                        user_input = user_input[:cursor_pos] + user_input[cursor_pos+1:]
                
                # Handle left arrow
                elif key == curses.KEY_LEFT:
                    if cursor_pos > 0:
                        cursor_pos -= 1
                
                # Handle right arrow
                elif key == curses.KEY_RIGHT:
                    if cursor_pos < len(user_input):
                        cursor_pos += 1
                
                # Handle home key
                elif key == curses.KEY_HOME:
                    cursor_pos = 0
                
                # Handle end key
                elif key == curses.KEY_END:
                    cursor_pos = len(user_input)
                
                # Handle regular character input
                elif 32 <= key <= 126:
                    max_length = width - len(prompt) - 2
                    if len(user_input) < max_length:
                        user_input = user_input[:cursor_pos] + chr(key) + user_input[cursor_pos:]
                        cursor_pos += 1
                        
        except curses.error:
            return None
        except KeyboardInterrupt:
            return None
        finally:
            # Always restore the original state
            self.stdscr.nodelay(True)

def main(stdscr):
    try:
        editor = TextEditor(stdscr)
        editor.run()
    except Exception as e:
        curses.endwin()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("There might be an issue with your terminal's capabilities.")
    except Exception as e:
        print(f"A fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
