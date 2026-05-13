```
  ███████╗██╗██████╗ ███████╗██╗    ██╗ █████╗ ██╗     ██╗
  ██╔════╝██║██╔══██╗██╔════╝██║    ██║██╔══██╗██║     ██║
  █████╗  ██║██████╔╝█████╗  ██║ █╗ ██║███████║██║     ██║
  ██╔══╝  ██║██╔══██╗██╔══╝  ██║███╗██║██╔══██║██║     ██║
  ██║     ██║██║  ██║███████╗╚███╔███╔╝██║  ██║███████╗███████╗
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝
```

<div align="center">

**Windows Firewall — Internet Access Manager**

A sleek terminal UI for blocking and unblocking application internet access
via Windows Firewall rules — no GUI, no bloat, just control.

![Python](https://img.shields.io/badge/Python-3.8%2B-brightcyan?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-magenta?style=flat-square)
![Admin](https://img.shields.io/badge/Requires-Administrator-red?style=flat-square)

</div>

---

## What It Does

Firewall Manager gives you a fast, keyboard-driven terminal interface to manage Windows Firewall rules on a per-application basis. Register any `.exe`, toggle its internet access on or off with a single keypress, and confirm the result immediately — all without touching the Windows Firewall GUI.

Rules are written directly via `netsh advfirewall`, blocking both inbound and outbound traffic for each registered application.

---

## Requirements

| Requirement | Details |
|---|---|
| OS | Windows 10 / 11 |
| Python | 3.8 or later |
| Privileges | **Must run as Administrator** |
| Dependency | `rich` ≥ 13.0 |

Install the dependency:

```bash
pip install rich
```

---

## Quick Start

```bash
# 1. Clone or download firewall_manager.py

# 2. Open a terminal as Administrator
#    Right-click → "Run as administrator"

# 3. Run the script
python firewall_manager.py
```

On first launch, you will be prompted to register your first application.

---

## Usage

### Adding an Application

When prompted, provide:

- **Application path** — full path to the `.exe` file
  `C:\Program Files\Some App\app.exe`
- **Alias** — a short name you'll use to identify it
  `some-app`

Entries are saved to `firewall_apps.json` in the same directory.

### Main Menu

```
  Number → Toggle Access    [A] Add New    [D] Delete    [Q] Quit
```

| Key | Action |
|---|---|
| `1`–`N` | Toggle internet access for that application |
| `A` | Add a new application |
| `D` | Delete a registered application |
| `Q` | Quit |

### Status Indicators

| Indicator | Meaning |
|---|---|
| `● ALLOWED` | No blocking rule active — internet access is open |
| `● BLOCKED` | Firewall rule is active — internet access is cut off |

---

## How It Works

Each block creates two Windows Firewall rules (inbound + outbound) named:

```
FW_MANAGER_BLOCK_<alias>
```

Unblocking deletes both rules. You can verify rules independently:

```powershell
# List all rules created by this tool
Get-NetFirewallRule | Where-Object { $_.Name -like "FW_MANAGER_BLOCK_*" }

# Check a specific rule
netsh advfirewall firewall show rule name=FW_MANAGER_BLOCK_<alias>
```

---

## Verifying It Works

The fastest way to confirm blocking is active — use `curl.exe` (built into Windows):

**Register it:**
```
Path  : C:\Windows\System32\curl.exe
Alias : curl-test
```

**Block it, then test:**
```cmd
curl https://example.com
```
→ Times out = rule is working

**Unblock it, then test again:**
```cmd
curl https://example.com
```
→ Returns HTML = rule removed successfully

You can also inspect rules visually:

```
Win + R → wf.msc → Inbound / Outbound Rules
Filter by name: FW_MANAGER_BLOCK_
```

---

## Data Storage

Application entries are stored locally in `firewall_apps.json`:

```json
{
  "curl-test": "C:\\Windows\\System32\\curl.exe",
  "some-app": "C:\\Program Files\\Some App\\app.exe"
}
```

This file is created automatically on first save and can be edited manually if needed.

---

## Notes

- Deleting an application from the list does **not** automatically remove its firewall rule. Toggle it to ALLOWED first if you want to restore access before deleting.
- Rules persist across reboots — they are permanent Windows Firewall entries until removed.
- If an operation fails, ensure the terminal session has Administrator privileges.

---

## License

MIT — do whatever you want with it.
