#!/usr/bin/env python3
"""
SmartFile 2026 - A DOS-era style text-based file browser.
Reminiscent of Norton Commander and classic DOS file managers.
A tribute to the original SmartFile by Shailendra Mishra and John Thomas (1998).
"""

import curses
import os
import stat
import time
import sys
import subprocess
import platform
import argparse


# Will be set by argument parsing before curses starts
GRAYSCALE = False


def format_size(size):
    """Format file size in classic DOS style."""
    if size < 1024:
        return f"{size:>9}"
    elif size < 1024 * 1024:
        return f"{size // 1024:>8}K"
    elif size < 1024 * 1024 * 1024:
        return f"{size // (1024 * 1024):>8}M"
    else:
        return f"{size // (1024 * 1024 * 1024):>8}G"


def format_date(mtime):
    """Format modification time in DOS style: MM-DD-YY  HH:MMa."""
    t = time.localtime(mtime)
    ampm = "a" if t.tm_hour < 12 else "p"
    hour = t.tm_hour % 12
    if hour == 0:
        hour = 12
    return f"{t.tm_mon:02d}-{t.tm_mday:02d}-{t.tm_year % 100:02d}  {hour:2d}:{t.tm_min:02d}{ampm}"


def get_dir_entries(path):
    """Get directory entries sorted: directories first, then files. Both alphabetical."""
    entries = []
    try:
        items = os.listdir(path)
    except PermissionError:
        return entries

    dirs = []
    files = []

    for name in items:
        full = os.path.join(path, name)
        try:
            st = os.stat(full)
            is_dir = stat.S_ISDIR(st.st_mode)
            size = st.st_size if not is_dir else 0
            mtime = st.st_mtime
            is_exec = not is_dir and (st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        except (OSError, PermissionError):
            is_dir = False
            size = 0
            mtime = 0
            is_exec = False

        entry = {
            "name": name,
            "is_dir": is_dir,
            "size": size,
            "mtime": mtime,
            "is_exec": is_exec,
        }

        if is_dir:
            dirs.append(entry)
        else:
            files.append(entry)

    dirs.sort(key=lambda e: e["name"].lower())
    files.sort(key=lambda e: e["name"].lower())

    return dirs + files


def draw_box(win, y, x, h, w, title="", color=None):
    """Draw a single-line box with optional title, DOS style."""
    if color is None:
        color = curses.color_pair(1)

    # Corners and edges
    win.addch(y, x, curses.ACS_ULCORNER, color)
    win.addch(y, x + w - 1, curses.ACS_URCORNER, color)
    win.addch(y + h - 1, x, curses.ACS_LLCORNER, color)
    try:
        win.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER, color)
    except curses.error:
        pass

    for i in range(1, w - 1):
        win.addch(y, x + i, curses.ACS_HLINE, color)
        try:
            win.addch(y + h - 1, x + i, curses.ACS_HLINE, color)
        except curses.error:
            pass
    for i in range(1, h - 1):
        win.addch(y + i, x, curses.ACS_VLINE, color)
        try:
            win.addch(y + i, x + w - 1, curses.ACS_VLINE, color)
        except curses.error:
            pass

    if title:
        title_str = f" {title} "
        tx = x + (w - len(title_str)) // 2
        win.addstr(y, tx, title_str, color | curses.A_BOLD)


def draw_double_box(win, y, x, h, w, title="", color=None):
    """Draw a double-line box for the main frame - pure DOS aesthetic."""
    if color is None:
        color = curses.color_pair(1)

    # Double-line box drawing characters (Unicode)
    TL = "\u2554"  # ╔
    TR = "\u2557"  # ╗
    BL = "\u255a"  # ╚
    BR = "\u255d"  # ╝
    H = "\u2550"   # ═
    V = "\u2551"   # ║

    win.addstr(y, x, TL, color)
    win.addstr(y, x + w - 1, TR, color)
    win.addstr(y + h - 1, x, BL, color)
    try:
        win.addstr(y + h - 1, x + w - 1, BR, color)
    except curses.error:
        pass

    for i in range(1, w - 1):
        win.addstr(y, x + i, H, color)
        try:
            win.addstr(y + h - 1, x + i, H, color)
        except curses.error:
            pass
    for i in range(1, h - 1):
        win.addstr(y + i, x, V, color)
        try:
            win.addstr(y + i, x + w - 1, V, color)
        except curses.error:
            pass

    if title:
        title_str = f" {title} "
        tx = x + (w - len(title_str)) // 2
        win.addstr(y, tx, title_str, color | curses.A_BOLD)


def open_file(filepath):
    """Open a file with the system default application."""
    try:
        if platform.system() == "Darwin":
            subprocess.Popen(["open", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["start", filepath], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def splash_screen(stdscr):
    """Show a nostalgic DOS-style splash screen."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    if GRAYSCALE:
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_WHITE)
    else:
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLUE)

    bg = curses.color_pair(13)
    bright = curses.color_pair(14) | curses.A_BOLD
    dim = curses.color_pair(13)

    stdscr.bkgd(" ", bg)
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    logo = [
        "  ____                       _   _____ _ _      ",
        " / ___| _ __ ___   __ _ _ __| |_|  ___(_) | ___ ",
        " \\___ \\| '_ ` _ \\ / _` | '__| __| |_  | | |/ _ \\",
        "  ___) | | | | | | (_| | |  | |_|  _| | | |  __/",
        " |____/|_| |_| |_|\\__,_|_|   \\__|_|   |_|_|\\___|",
        "  ____    ___  ____    __",
        " |___ \\  / _ \\|___ \\  / /_",
        "   __) || | | | __) || '_ \\",
        "  / __/ | |_| |/ __/ | (_) |",
        " |_____|\\___/|_____|\\___/",
    ]

    box_w = 52
    box_h = 20
    box_y = max((max_y - box_h) // 2, 0)
    box_x = max((max_x - box_w) // 2, 0)

    draw_double_box(stdscr, box_y, box_x, box_h, box_w, color=bright)

    # Logo
    logo_start_y = box_y + 2
    for i, line in enumerate(logo):
        x = box_x + (box_w - len(line)) // 2
        try:
            stdscr.addstr(logo_start_y + i, x, line, bright)
        except curses.error:
            pass

    # Tribute text
    tribute_y = logo_start_y + len(logo) + 1
    lines = [
        "A tribute to the original SmartFile",
        "by Shailendra Mishra and John Thomas, 1998",
    ]
    for i, line in enumerate(lines):
        x = box_x + (box_w - len(line)) // 2
        try:
            stdscr.addstr(tribute_y + i, x, line, dim)
        except curses.error:
            pass

    # Press any key
    prompt = "Press any key to continue..."
    prompt_y = box_y + box_h - 2
    prompt_x = box_x + (box_w - len(prompt)) // 2
    try:
        stdscr.addstr(prompt_y, prompt_x, prompt, bright)
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
    # Splash screen
    splash_screen(stdscr)

    # Setup curses
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # Color scheme
    if GRAYSCALE:
        # Grayscale monochrome theme
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Main background
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Directories
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Selected item
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Selected directory
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Status bar
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Title bar
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Executables
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Selected executable
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)    # File info
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Help overlay
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Bottom key bar
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Key numbers in bar
    else:
        # Classic DOS blue theme
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)     # Main background
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)    # Directories
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)     # Selected item
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_CYAN)    # Selected directory
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)     # Status bar
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Title bar
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLUE)     # Executables
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_CYAN)     # Selected executable
        curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLUE)      # File info
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)     # Help overlay
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Bottom key bar
        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_WHITE)     # Key numbers in bar

    C_MAIN = curses.color_pair(1)
    C_DIR = curses.color_pair(2) | curses.A_BOLD
    C_SEL = curses.color_pair(3)
    C_SELDIR = curses.color_pair(4) | curses.A_BOLD
    C_STATUS = curses.color_pair(5)
    C_TITLE = curses.color_pair(6) | curses.A_BOLD
    C_EXEC = curses.color_pair(7)
    C_SELEXEC = curses.color_pair(8)
    C_INFO = curses.color_pair(9)
    C_KEYBAR = curses.color_pair(11)
    C_KEYNUM = curses.color_pair(12) | curses.A_BOLD

    stdscr.bkgd(" ", C_MAIN)

    # State
    current_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    cursor = 0
    scroll_offset = 0
    entries = get_dir_entries(current_path)
    history = []  # Stack of (path, cursor, scroll) for going back
    show_hidden = False
    message = ""
    message_time = 0

    def filtered_entries():
        if show_hidden:
            return entries
        return [e for e in entries if not e["name"].startswith(".")]

    def refresh_entries():
        nonlocal entries, cursor, scroll_offset
        entries = get_dir_entries(current_path)
        fe = filtered_entries()
        if cursor >= len(fe):
            cursor = max(0, len(fe) - 1)
        if scroll_offset > cursor:
            scroll_offset = cursor

    refresh_entries()

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 10 or max_x < 40:
            stdscr.addstr(0, 0, "Terminal too small!", curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()
            continue

        fe = filtered_entries()

        # ── Title bar ──
        title_text = " SmartFile 2026 "
        title_bar = " " * max_x
        try:
            stdscr.addstr(0, 0, title_bar, C_TITLE)
            stdscr.addstr(0, (max_x - len(title_text)) // 2, title_text, C_TITLE)
        except curses.error:
            pass

        # ── Bottom key bar (F-key hints like Norton Commander) ──
        key_hints = [
            ("1", "Help"),
            ("2", "About"),
            ("3", "Edit"),
            ("4", "Open"),
            ("5", "Copy"),
            ("6", "Move"),
            ("7", "MkDir"),
            ("8", "Del"),
            ("9", "Hide"),
            ("10", "Quit"),
        ]
        try:
            bar_y = max_y - 1
            stdscr.addstr(bar_y, 0, " " * max_x, C_KEYBAR)
            col = 0
            slot_w = max_x // 10
            for num, label in key_hints:
                if col + len(num) + len(label) + 1 < max_x:
                    stdscr.addstr(bar_y, col, num, C_KEYNUM)
                    stdscr.addstr(bar_y, col + len(num), label.ljust(slot_w - len(num)), C_KEYBAR)
                col += slot_w
        except curses.error:
            pass

        # ── Main panel ──
        panel_y = 1
        panel_x = 0
        panel_h = max_y - 3  # Leave room for title, status, keybar
        panel_w = max_x

        # Draw the main double-line box
        draw_double_box(stdscr, panel_y, panel_x, panel_h, panel_w, color=C_MAIN)

        # ── Path bar (inside top of box) ──
        path_display = current_path
        avail_w = panel_w - 4
        if len(path_display) > avail_w:
            path_display = "..." + path_display[-(avail_w - 3):]
        try:
            stdscr.addstr(panel_y, 2, f" {path_display} ", C_MAIN | curses.A_BOLD)
        except curses.error:
            pass

        # ── Column headers ──
        header_y = panel_y + 1
        name_col = panel_x + 2
        name_w = panel_w - 32
        if name_w < 12:
            name_w = 12
        size_col = name_col + name_w
        date_col = size_col + 10

        header = f"{'Name':<{name_w}}{'Size':>9}  {'Modified':<14}"
        try:
            stdscr.addstr(header_y, name_col, header[:panel_w - 4], C_INFO)
        except curses.error:
            pass

        # Separator line
        sep_y = header_y + 1
        sep_char = "\u2500"  # ─
        try:
            stdscr.addstr(sep_y, name_col, sep_char * (panel_w - 4), C_MAIN)
        except curses.error:
            pass

        # ── File list ──
        list_y_start = sep_y + 1
        list_y_end = panel_y + panel_h - 2
        visible_count = list_y_end - list_y_start

        # Adjust scroll
        if cursor < scroll_offset:
            scroll_offset = cursor
        if cursor >= scroll_offset + visible_count:
            scroll_offset = cursor - visible_count + 1
        if scroll_offset < 0:
            scroll_offset = 0

        for i in range(visible_count):
            idx = scroll_offset + i
            draw_y = list_y_start + i

            if draw_y >= list_y_end:
                break

            if idx < len(fe):
                entry = fe[idx]
                is_selected = idx == cursor

                # Determine colors
                if entry["is_dir"]:
                    if is_selected:
                        color = C_SELDIR
                    else:
                        color = C_DIR
                    icon = "\u25ba "  # ►
                    size_str = "   <DIR>"
                elif entry["is_exec"]:
                    if is_selected:
                        color = C_SELEXEC
                    else:
                        color = C_EXEC
                    icon = "  "
                    size_str = format_size(entry["size"])
                else:
                    if is_selected:
                        color = C_SEL
                    else:
                        color = C_MAIN
                    icon = "  "
                    size_str = format_size(entry["size"])

                date_str = format_date(entry["mtime"])
                display_name = icon + entry["name"]

                # Truncate name if needed
                max_name = name_w
                if len(display_name) > max_name:
                    display_name = display_name[: max_name - 1] + "\u2026"

                line = f"{display_name:<{max_name}}{size_str}  {date_str}"

                # Fill entire row for selection highlight
                if is_selected:
                    full_line = line.ljust(panel_w - 4)
                    try:
                        stdscr.addstr(draw_y, name_col, full_line[: panel_w - 4], color)
                    except curses.error:
                        pass
                else:
                    try:
                        stdscr.addstr(draw_y, name_col, line[: panel_w - 4], color)
                    except curses.error:
                        pass

        # ── Scroll indicator ──
        if len(fe) > visible_count:
            if scroll_offset > 0:
                try:
                    stdscr.addstr(list_y_start, panel_x + panel_w - 2, "\u25b2", C_INFO)  # ▲
                except curses.error:
                    pass
            if scroll_offset + visible_count < len(fe):
                try:
                    stdscr.addstr(list_y_end - 1, panel_x + panel_w - 2, "\u25bc", C_INFO)  # ▼
                except curses.error:
                    pass

        # ── Status bar ──
        status_y = panel_y + panel_h
        total_files = sum(1 for e in fe if not e["is_dir"])
        total_dirs = sum(1 for e in fe if e["is_dir"])
        total_size = sum(e["size"] for e in fe if not e["is_dir"])

        # Show message if recent, otherwise show stats
        now = time.time()
        if message and (now - message_time) < 3:
            status_text = f" {message}"
        else:
            message = ""
            hidden_count = len(entries) - len(fe)
            hidden_str = f"  ({hidden_count} hidden)" if hidden_count > 0 else ""
            size_display = format_size(total_size).strip()
            status_text = f" {total_dirs} dir(s), {total_files} file(s), {size_display} bytes{hidden_str}"

        try:
            stdscr.addstr(status_y, 0, status_text.ljust(max_x), C_STATUS)
        except curses.error:
            pass

        stdscr.refresh()

        # ── Input handling ──
        key = stdscr.getch()

        if key == curses.KEY_UP or key == ord("k"):
            if cursor > 0:
                cursor -= 1

        elif key == curses.KEY_DOWN or key == ord("j"):
            if cursor < len(fe) - 1:
                cursor += 1

        elif key == curses.KEY_PPAGE:  # Page Up
            cursor = max(0, cursor - visible_count)

        elif key == curses.KEY_NPAGE:  # Page Down
            cursor = min(len(fe) - 1, cursor + visible_count)

        elif key == curses.KEY_HOME:
            cursor = 0
            scroll_offset = 0

        elif key == curses.KEY_END:
            cursor = max(0, len(fe) - 1)

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter
            if fe:
                entry = fe[cursor]
                if entry["is_dir"]:
                    new_path = os.path.join(current_path, entry["name"])
                    try:
                        os.listdir(new_path)  # Test access
                        history.append((current_path, cursor, scroll_offset))
                        current_path = os.path.abspath(new_path)
                        cursor = 0
                        scroll_offset = 0
                        refresh_entries()
                    except PermissionError:
                        message = "Access denied!"
                        message_time = time.time()
                else:
                    # Open file with system default
                    filepath = os.path.join(current_path, entry["name"])
                    open_file(filepath)
                    message = f"Opened: {entry['name']}"
                    message_time = time.time()

        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace - go up
            if history:
                current_path, cursor, scroll_offset = history.pop()
                refresh_entries()
            else:
                parent = os.path.dirname(current_path)
                if parent != current_path:
                    old_name = os.path.basename(current_path)
                    current_path = parent
                    refresh_entries()
                    # Try to land cursor on the dir we came from
                    for i, e in enumerate(filtered_entries()):
                        if e["name"] == old_name:
                            cursor = i
                            break
                    else:
                        cursor = 0
                    scroll_offset = max(0, cursor - visible_count // 2)

        elif key == ord(".") or key == curses.KEY_F9:  # Toggle hidden files
            show_hidden = not show_hidden
            fe_new = filtered_entries()
            if cursor >= len(fe_new):
                cursor = max(0, len(fe_new) - 1)
            message = "Hidden files: " + ("shown" if show_hidden else "hidden")
            message_time = time.time()

        elif key == ord("/"):  # Quick search
            curses.curs_set(1)
            search_str = ""
            # Draw search prompt
            try:
                stdscr.addstr(status_y, 0, " Search: ".ljust(max_x), C_STATUS)
                stdscr.move(status_y, 9)
            except curses.error:
                pass
            stdscr.refresh()

            while True:
                ch = stdscr.getch()
                if ch in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Escape
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    search_str = search_str[:-1]
                elif 32 <= ch < 127:
                    search_str += chr(ch)

                # Live search - jump to first match
                if search_str:
                    for i, e in enumerate(fe):
                        if e["name"].lower().startswith(search_str.lower()):
                            cursor = i
                            if cursor < scroll_offset or cursor >= scroll_offset + visible_count:
                                scroll_offset = max(0, cursor - visible_count // 2)
                            break

                try:
                    prompt = f" Search: {search_str}"
                    stdscr.addstr(status_y, 0, prompt.ljust(max_x), C_STATUS)
                    stdscr.move(status_y, 9 + len(search_str))
                except curses.error:
                    pass
                stdscr.refresh()

            curses.curs_set(0)

        elif key == ord("~"):  # Go to home directory
            history.append((current_path, cursor, scroll_offset))
            current_path = os.path.expanduser("~")
            cursor = 0
            scroll_offset = 0
            refresh_entries()

        elif key == ord("r") or key == curses.KEY_F5:  # Refresh
            refresh_entries()
            message = "Refreshed"
            message_time = time.time()

        elif key == curses.KEY_F1:  # Help
            # Show help overlay
            help_lines = [
                "SmartFile 2026 - Keyboard Reference",
                "",
                "\u2500\u2500\u2500 Navigation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500",
                "  Up/Down, j/k ... Move cursor",
                "  PgUp/PgDn ...... Scroll page",
                "  Home/End ....... First/last item",
                "  Enter .......... Open dir or file",
                "  Backspace ...... Go up / back",
                "  ~ .............. Go to home dir",
                "",
                "\u2500\u2500\u2500 Actions \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500",
                "  / .............. Search files",
                "  . or F9 ........ Toggle hidden",
                "  r or F5 ........ Refresh",
                "  F1 ............. This help",
                "  F2 ............. About / splash",
                "  q, F10, Esc .... Quit",
                "",
                "  Press any key to close...",
            ]
            help_h = len(help_lines) + 4
            help_w = 46
            help_y = max(1, (max_y - help_h) // 2)
            help_x = max(0, (max_x - help_w) // 2)

            draw_double_box(stdscr, help_y, help_x, help_h, help_w,
                            title="Help", color=curses.color_pair(10))
            for i, line in enumerate(help_lines):
                try:
                    stdscr.addstr(help_y + 2 + i, help_x + 2, line[:help_w - 4],
                                  curses.color_pair(10))
                except curses.error:
                    pass
            stdscr.refresh()
            stdscr.getch()

        elif key == curses.KEY_F2:  # About / splash screen
            splash_screen(stdscr)
            stdscr.bkgd(" ", C_MAIN)

        elif key == curses.KEY_F4:  # Open with system
            if fe:
                entry = fe[cursor]
                filepath = os.path.join(current_path, entry["name"])
                open_file(filepath)
                message = f"Opened: {entry['name']}"
                message_time = time.time()

        elif key == ord("q") or key == 27 or key == curses.KEY_F10:  # Quit
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartFile 2026 - DOS-era text file browser")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="Starting directory")
    parser.add_argument("--gray", "--grey", "--grayscale", action="store_true",
                        help="Use grayscale monochrome theme")
    args = parser.parse_args()
    GRAYSCALE = args.gray
    sys.argv = [sys.argv[0], args.path]  # Normalize for main()
    curses.wrapper(main)
