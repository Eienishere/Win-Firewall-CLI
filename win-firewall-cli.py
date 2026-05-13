"""
Firewall Manager - Windows Firewall Application Internet Access Manager
Must be run as Administrator.

Requirement: pip install rich
"""

import subprocess
import json
import os
import sys
import time

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.live import Live
    from rich.spinner import Spinner
    from rich import box
    from rich.style import Style
    from rich.align import Align
    from rich.padding import Padding
except ImportError:
    print("\n  [!] 'rich' library not found.")
    print("  Install it with: pip install rich\n")
    sys.exit(1)

console = Console()

DATA_FILE = "firewall_apps.json"

# ── Color palette ─────────────────────────────────────────────────────────────
C_PRIMARY   = "bright_cyan"
C_ACCENT    = "bright_magenta"
C_SUCCESS   = "bright_green"
C_DANGER    = "bright_red"
C_WARNING   = "yellow"
C_DIM       = "grey62"
C_HEADER_BG = "on_grey19"
C_OPEN      = "bright_green"
C_BLOCKED   = "bright_red"

BANNER = r"""
  ███████╗██╗██████╗ ███████╗██╗    ██╗ █████╗ ██╗     ██╗
  ██╔════╝██║██╔══██╗██╔════╝██║    ██║██╔══██╗██║     ██║
  █████╗  ██║██████╔╝█████╗  ██║ █╗ ██║███████║██║     ██║
  ██╔══╝  ██║██╔══██╗██╔══╝  ██║███╗██║██╔══██║██║     ██║
  ██║     ██║██║  ██║███████╗╚███╔███╔╝██║  ██║███████╗███████╗
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝
"""

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header():
    banner_text = Text(BANNER, style=f"bold {C_PRIMARY}")
    console.print(Align.center(banner_text))
    sub = Text("  Windows Firewall — Internet Access Manager  ", style=f"bold {C_ACCENT} {C_HEADER_BG}")
    console.print(Align.center(sub))
    console.print()

def divider(title: str = ""):
    if title:
        console.print(Rule(f"[bold {C_DIM}]{title}[/]", style=C_DIM))
    else:
        console.print(Rule(style=C_DIM))

def save(apps: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)

def load() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def rule_exists(rule_name: str) -> bool:
    result = subprocess.run(
        ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
        capture_output=True, text=True
    )
    return "No rules match" not in result.stdout and result.returncode == 0

def access_status(alias: str) -> Text:
    rule_name = f"FW_MANAGER_BLOCK_{alias}"
    if rule_exists(rule_name):
        t = Text()
        t.append("● ", style=C_BLOCKED)
        t.append("BLOCKED  ", style=f"bold {C_BLOCKED}")
        return t
    t = Text()
    t.append("● ", style=C_OPEN)
    t.append("ALLOWED  ", style=f"bold {C_OPEN}")
    return t

def run_with_spinner(message: str, fn, *args):
    """Runs a function in the background while showing a spinner."""
    result = [None]
    error  = [None]

    import threading
    def worker():
        try:
            result[0] = fn(*args)
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=worker)
    t.start()

    with console.status(f"[bold {C_WARNING}]{message}[/]", spinner="dots", spinner_style=C_ACCENT):
        t.join()

    if error[0]:
        raise error[0]
    return result[0]

def block_access(alias: str, path: str) -> bool:
    rule_name = f"FW_MANAGER_BLOCK_{alias}"
    for direction in ["out", "in"]:
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}", f"dir={direction}", "action=block",
            f"program={path}", "enable=yes"
        ], capture_output=True)
    return rule_exists(rule_name)

def allow_access(alias: str) -> bool:
    rule_name = f"FW_MANAGER_BLOCK_{alias}"
    subprocess.run([
        "netsh", "advfirewall", "firewall", "delete", "rule",
        f"name={rule_name}"
    ], capture_output=True)
    return not rule_exists(rule_name)

# ─────────────────────────────────────────────
# Step 1 – Add application flow
# ─────────────────────────────────────────────

def add_app_flow(apps: dict):
    clear()
    header()
    console.print(Panel(
        f"[bold {C_ACCENT}]📂  Add Application Mode[/]\n"
        f"[{C_DIM}]Enter a path and alias; you will be asked whether to continue after each entry.[/]",
        border_style=C_ACCENT, padding=(0, 2)
    ))
    console.print()

    while True:
        path = Prompt.ask(f"  [bold {C_PRIMARY}]Application path[/]").strip()
        if not path:
            console.print(f"  [bold {C_WARNING}]⚠  Path cannot be empty![/]\n")
            continue
        if not os.path.isfile(path):
            console.print(f"  [bold {C_WARNING}]⚠  File not found:[/] [{C_DIM}]{path}[/]")
            if not Confirm.ask(f"  [bold {C_WARNING}]Add it anyway?[/]"):
                continue

        alias = Prompt.ask(f"  [bold {C_PRIMARY}]Alias         [/]").strip()
        if not alias:
            console.print(f"  [bold {C_WARNING}]⚠  Alias cannot be empty![/]\n")
            continue

        if alias in apps:
            console.print(f"  [bold {C_WARNING}]⚠  '[/][{C_ACCENT}]{alias}[/][bold {C_WARNING}]' already exists.[/]")
            if not Confirm.ask(f"  [bold {C_WARNING}]Overwrite it?[/]"):
                continue

        apps[alias] = path
        save(apps)
        console.print(f"\n  [bold {C_SUCCESS}]✔  '{alias}' saved successfully.[/]\n")

        if not Confirm.ask(f"  [bold {C_PRIMARY}]Add another application?[/]"):
            break

# ─────────────────────────────────────────────
# Step 2 – List & manage access
# ─────────────────────────────────────────────

def build_table(apps: dict) -> Table:
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style=C_DIM,
        header_style=f"bold {C_ACCENT}",
        show_lines=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("#",      style=f"bold {C_DIM}",     width=4,  justify="right")
    table.add_column("Alias",  style=f"bold {C_PRIMARY}", min_width=20)
    table.add_column("Status", min_width=16)
    table.add_column("Path",   style=C_DIM,               overflow="fold")

    for i, (alias, path) in enumerate(apps.items(), 1):
        status = access_status(alias)
        table.add_row(str(i), alias, status, path)

    return table

def menu_line() -> str:
    return (
        f"  [{C_PRIMARY}]Number[/] → Toggle Access  "
        f"[{C_ACCENT}][A][/] Add New  "
        f"[{C_WARNING}][D][/] Delete  "
        f"[{C_DANGER}][Q][/] Quit"
    )

def list_and_manage(apps: dict):
    while True:
        clear()
        header()

        if not apps:
            console.print(Panel(
                f"[bold {C_WARNING}]📋  No applications registered yet.\n"
                f"[{C_DIM}]Get started by adding an application.[/]",
                border_style=C_WARNING, padding=(1, 4)
            ))
            console.print()
            Prompt.ask(f"  [{C_DIM}]Press Enter to go to Add mode[/]", default="")
            add_app_flow(apps)
            continue

        # Load status table with spinner
        table = run_with_spinner("Reading firewall rules…", build_table, apps)

        console.print(Panel(
            table,
            title=f"[bold {C_PRIMARY}]📋 Registered Applications[/]",
            border_style=C_PRIMARY,
            padding=(0, 1),
        ))
        console.print()
        divider("Actions")
        console.print(menu_line())
        divider()
        console.print()

        choice = Prompt.ask(f"  [bold {C_ACCENT}]»[/]").strip()
        entries = list(apps.items())

        if choice.lower() == "q":
            clear()
            console.print(Align.center(
                Text("\n  👋  Goodbye!\n", style=f"bold {C_PRIMARY}")
            ))
            sys.exit(0)

        elif choice.lower() == "a":
            add_app_flow(apps)

        elif choice.lower() == "d":
            console.print()
            del_no = Prompt.ask(f"  [{C_WARNING}]Enter the number to delete[/]").strip()
            try:
                idx = int(del_no) - 1
                if 0 <= idx < len(entries):
                    alias, _ = entries[idx]
                    if Confirm.ask(f"  [bold {C_DANGER}]Delete '{alias}'?[/]"):
                        del apps[alias]
                        save(apps)
                        console.print(f"  [bold {C_SUCCESS}]✔  '{alias}' deleted.[/]")
                        time.sleep(1)
                else:
                    console.print(f"  [bold {C_WARNING}]⚠  Invalid number.[/]")
                    time.sleep(1)
            except ValueError:
                console.print(f"  [bold {C_WARNING}]⚠  Invalid input.[/]")
                time.sleep(1)

        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entries):
                    alias, path = entries[idx]
                    rule_name = f"FW_MANAGER_BLOCK_{alias}"
                    console.print()

                    if rule_exists(rule_name):
                        success = run_with_spinner(
                            f"Allowing access for '{alias}'…",
                            allow_access, alias
                        )
                        if success:
                            console.print(f"  [bold {C_SUCCESS}]✔  Access allowed.[/]")
                        else:
                            console.print(f"  [bold {C_DANGER}]✘  Operation failed — administrator privileges may be required.[/]")
                    else:
                        success = run_with_spinner(
                            f"Blocking access for '{alias}'…",
                            block_access, alias, path
                        )
                        if success:
                            console.print(f"  [bold {C_SUCCESS}]✔  Access blocked.[/]")
                        else:
                            console.print(f"  [bold {C_DANGER}]✘  Operation failed — administrator privileges may be required.[/]")

                    time.sleep(1.2)
                else:
                    console.print(f"  [bold {C_WARNING}]⚠  Invalid number.[/]")
                    time.sleep(1)
            except ValueError:
                console.print(f"  [bold {C_WARNING}]⚠  Invalid input.[/]")
                time.sleep(1)

# ─────────────────────────────────────────────
# Main flow
# ─────────────────────────────────────────────

def main():
    if os.name == "nt":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            clear()
            console.print(Panel(
                f"[bold {C_DANGER}]⚠  ADMINISTRATOR PRIVILEGES REQUIRED[/]\n\n"
                f"[{C_DIM}]Please run this script as an administrator:\n"
                f"Right-click → 'Run as administrator'[/]",
                border_style=C_DANGER, padding=(1, 4)
            ))
            Prompt.ask(f"\n  [{C_DIM}]Press Enter to exit[/]", default="")
            sys.exit(1)

    apps = load()

    if not apps:
        clear()
        header()
        console.print(Panel(
            f"[bold {C_WARNING}]First launch — no applications registered yet.[/]\n"
            f"[{C_DIM}]You can add applications now.[/]",
            border_style=C_WARNING, padding=(0, 2)
        ))
        console.print()
        add_app_flow(apps)

    list_and_manage(apps)


if __name__ == "__main__":
    main()
