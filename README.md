# AutoBackup

Simple automated backup utility for Pop!_OS and Linux.

## Installation

```bash
./install.sh
```

Creates a virtual environment, installs systemd services, and sets up config at `~/.config/autobackup/config.json`.

## Configuration

Edit `~/.config/autobackup/config.json`:

```json
{
    "sources": ["~/Documents", "~/Pictures"],
    "lists": ["~/.config"],
    "destination": "~/Backups",
    "destination_format": "%Y-%m-%d",
    "repeat": true,
    "time_format": "%H",
    "time_value": "19",
    "sleep": 3600,
    "keep_copies": 7
}
```

**Options:**
- `sources` - Directories to backup (recursive copy)
- `lists` - Directories to list contents only (no copy)
- `destination` - Where to save backups
- `destination_format` - Backup folder naming (strftime format)
- `repeat` - Run repeatedly (true) or once (false)
- `time_format` - When to run: `%H` (hour), `%d` (day of month), `%w` (weekday)
- `time_value` - Time to trigger backup (e.g., "19" for 7 PM)
- `sleep` - Seconds to wait after backup
- `keep_copies` - Number of backup versions to keep

**Note:** `~` expands to home directory.

## Usage

```bash
# Run backup now
autobackup

# Run with verbose output
autobackup --verbose

# Check service status
systemctl --user status autobackup.service

# View logs
journalctl --user -u autobackup.service -f
# or
tail -f ~/.local/share/autobackup/autobackup.log
```

## Uninstall

```bash
./uninstall.sh
```

## Troubleshooting

**Command not found:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**No notifications:**
```bash
sudo apt install libnotify-bin
```

**Service errors:**
```bash
autobackup --verbose
journalctl --user -u autobackup.service -n 50
```

## Requirements

- Pop!_OS 22.04+ or Ubuntu 22.04+
- Python 3.8+
- notify-send (optional, for notifications)
