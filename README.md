# AutoBackup

Simple automated backup utility for Pop!_OS and Linux.

## Installation

```bash
./install.sh
```

Sets up:
- Virtual environment at `~/.local/share/autobackup/venv`
- Config at `~/.config/autobackup/config.json`
- Systemd service and timer
- CLI command at `~/.local/bin/autobackup`

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
- `sources` - Directories to backup (recursive copy). Automatically excludes `*.ini` and `My *` patterns
- `lists` - Directories to list contents only (creates `ListingContents.txt`, no copy)
- `destination` - Where to save backups
- `destination_format` - Backup folder naming (strftime format, e.g., `%Y-%m-%d` → `2025-11-08`)
- `repeat` - Run repeatedly (true) or once (false)
- `time_format` - When to run: `%H` (hour 0-23), `%d` (day 1-31), `%w` (weekday 0-6)
- `time_value` - Time to trigger backup (e.g., "19" for 7 PM when `time_format` is `%H`)
- `sleep` - Seconds to wait after backup before next check
- `keep_copies` - Number of backup versions to keep (old backups auto-deleted)

**Note:** `~` expands to home directory. All paths are expanded automatically.

**After editing config:**
```bash
systemctl --user restart autobackup.service
```

## Usage

### Manual Backup
```bash
# Run backup once
autobackup

# Run with verbose output
autobackup --verbose

# Use custom config file
autobackup --config /path/to/config.json

# Run in daemon mode manually
autobackup --daemon
```

### Service Management
```bash
# Check status
systemctl --user status autobackup.service

# Start/stop service
systemctl --user start autobackup.service
systemctl --user stop autobackup.service

# Restart (e.g., after config changes)
systemctl --user restart autobackup.service

# Enable/disable autostart
systemctl --user enable autobackup.service
systemctl --user disable autobackup.service

# Check timer status
systemctl --user status autobackup.timer
systemctl --user list-timers
```

### Logs
```bash
# Follow live logs
journalctl --user -u autobackup.service -f

# View recent logs
journalctl --user -u autobackup.service -n 50

# Log file
tail -f ~/.local/share/autobackup/autobackup.log
```

## How It Works

**Scheduled Mode (default):**
- Systemd timer starts the service in daemon mode
- Service checks time every 60 seconds
- When `time_format` matches `time_value`, backup runs
- After backup, sleeps for `sleep` seconds before resuming checks
- Automatically maintains `keep_copies` most recent backups

**One-time Mode:**
- Set `repeat: false` in config
- Run `autobackup` manually
- Exits after single backup

## Uninstall

```bash
./uninstall.sh
```

Removes service, timer, virtual environment, and CLI command. Optionally preserves config and logs.

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

**Service won't start:**
```bash
# Check service logs
journalctl --user -u autobackup.service -n 50

# Test manually
autobackup --verbose

# Verify config
python3 -c "import json; print(json.load(open('$HOME/.config/autobackup/config.json')))"
```

**Backup already exists error:**
- Backup folder with same timestamp exists
- Adjust `destination_format` for finer granularity (e.g., add `%H-%M`)

**Config validation errors:**
- Check all source/list paths exist
- Check destination directory exists
- Verify `repeat`, `sleep`, `keep_copies` are correct types

## Requirements

- Pop!_OS 22.04+ or Ubuntu 22.04+
- Python 3.8+
- notify-send (optional, for notifications)
