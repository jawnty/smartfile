```
  ____                       _   _____ _ _
 / ___| _ __ ___   __ _ _ __| |_|  ___(_) | ___
 \___ \| '_ ` _ \ / _` | '__| __| |_  | | |/ _ \
  ___) | | | | | | (_| | |  | |_|  _| | | |  __/
 |____/|_| |_| |_|\__,_|_|   \__|_|   |_|_|\___|
  ____    ___  ____    __
 |___ \  / _ \|___ \  / /_
   __) || | | | __) || '_ \
  / __/ | |_| |/ __/ | (_) |
 |_____|\___|_____|\_____/
```

**A tribute to the original SmartFile, by Shailendra Mishra and John Thomas (1998)**

---

Remember `C:\PROJECTS\SMARTFILE\SMARTFILE.C`? Remember Turbo C++ 3.0, `conio.h`,
writing directly to video memory at `0xB800`, and `findfirst`/`findnext` loops?

Remember the box-drawing characters, the arrow key navigation, the grayscale monitor?

That was 1998. We built a file manager from scratch on MS-DOS. No frameworks, no
Stack Overflow, no AI -- just two guys, a Turbo C++ compiler, and a 14-inch CRT.

**SmartFile 2026** brings it back. Same spirit, new millennium. A text-based file
browser for your terminal that works on your actual filesystem. Navigate with
arrow keys, open folders with Enter, go back with Backspace. Just like we did.

## Try It In Your Browser

The web demo lets you explore a virtual DOS filesystem -- yes, `C:\GAMES\DOOM` is
in there, and so is `C:\PROJECTS\SMARTFILE\SMARTFILE.C` with code that should look
very familiar.

**[Open the web demo](https://jawnty.github.io/smartfile/)**

## Run It For Real

The real SmartFile 2026 runs in your terminal and browses your actual files.
No dependencies beyond Python 3.

```bash
# Clone the repo
git clone https://github.com/jawnty/smartfile.git
cd smartfile

# Run it
python3 smartfile.py

# Start in a specific directory
python3 smartfile.py ~/projects

# Grayscale mode -- just like our old monitor
python3 smartfile.py --gray
```

## Keyboard Reference

| Key | Action |
|---|---|
| `Up` / `Down` | Navigate the file list |
| `Enter` | Open directory / launch file |
| `Backspace` | Go back / up one level |
| `PgUp` / `PgDn` | Scroll by page |
| `Home` / `End` | Jump to first / last item |
| `/` | Search (type to filter) |
| `.` or `F9` | Toggle hidden files |
| `~` | Jump to home directory |
| `r` or `F5` | Refresh |
| `F1` | Help |
| `F2` | About / splash screen |
| `q` or `Esc` | Quit |

## The Tech Then vs Now

| | 1998 | 2026 |
|---|---|---|
| **Language** | C | Python |
| **Compiler** | Turbo C++ 3.0 | `python3` |
| **Display** | Direct video memory (`0xB800`) | curses |
| **File API** | `findfirst` / `findnext` | `os.listdir` |
| **OS** | MS-DOS | Anything with a terminal |
| **Monitor** | 14" grayscale CRT | Whatever you've got |
| **Build system** | `BUILD.BAT` | None needed |
| **Lines of code** | ~800 | ~700 |
| **Vibe** | Identical | Identical |

---

*Built with the same energy as the original -- late nights and good memories.*

*Shailendra, this one's for you. -- John*
