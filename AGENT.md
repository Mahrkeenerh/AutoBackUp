# AutoBackUp - Agent Context

## Overview

AutoBackUp is a user-level backup daemon that periodically copies directories to timestamped backup folders. It runs as a systemd user service, triggered by a timer, and can also generate file listings without copying.

## Quick Commands

```bash
# Start/stop/restart
systemctl --user start autobackup.service
systemctl --user stop autobackup.service
systemctl --user restart autobackup.service

# Enable/disable timer (auto-start)
systemctl --user enable autobackup.timer
systemctl --user disable autobackup.timer

# View logs
journalctl --user -u autobackup.service -f
journalctl --user -u autobackup.service -n 100

# Check status
systemctl --user status autobackup.service
systemctl --user status autobackup.timer

# Manual backup run
autobackup --verbose
```

## Configuration

**Config file:** `~/.config/autobackup/config.json`

**Key settings:**
| Setting | Description |
|---------|-------------|
| `sources` | Directories to backup (recursive copy) |
| `lists` | Directories to list only (no copy, creates .txt inventory) |
| `destination` | Where backups are stored |
| `destination_format` | Folder naming (strftime, e.g., `%Y-%m-%d`) |
| `time_format` | Schedule unit (`%H`=hour, `%d`=day, `%w`=weekday) |
| `time_value` | When to run (e.g., `19` for 7 PM if time_format is `%H`) |
| `keep_copies` | Number of backups to retain (older ones deleted) |

**Example config:**
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

## Troubleshooting

### Service won't start

1. Check logs: `journalctl --user -u autobackup.service -n 50`
2. Verify config syntax: `python3 -m json.tool ~/.config/autobackup/config.json`
3. Test manually: `autobackup --verbose`
4. Check venv exists: `ls -la /path/to/repo/venv/`

### Backup not running at expected time

1. Check timer status: `systemctl --user list-timers`
2. Verify config `time_format` and `time_value` match your schedule
3. The daemon checks time every 60 seconds; slight delays are normal

### Permission denied errors

1. Check source directories exist and are readable
2. Check destination directory is writable
3. AutoBackUp skips special files (sockets, pipes, devices) automatically

### Disk space issues

1. Reduce `keep_copies` in config to retain fewer backups
2. Check destination disk space: `df -h ~/Backups`
3. Old backups are auto-deleted when new ones are created

### No desktop notifications

1. Install libnotify: `sudo apt install libnotify-bin`
2. Verify: `notify-send "Test" "Message"`
3. Notifications require a running desktop session

## Excluded Patterns

The backup automatically excludes:
- Cache directories (`.cache`, `node_modules`, `__pycache__`)
- Package manager caches (`.npm`, `.yarn`, `.cargo`, `.gradle`)
- IDE directories (`.vscode`, `.idea`)
- System directories (`.local/share`, `.steam`, `.var`)
- Log files (`*.log`)
- Special files (sockets, pipes, device files)

## File Locations

| File | Path |
|------|------|
| Config | `~/.config/autobackup/config.json` |
| Logs | `journalctl --user -u autobackup` |
| Log file | `~/.local/share/autobackup/autobackup.log` |
| Service | `~/.config/systemd/user/autobackup.service` (symlink) |
| Timer | `~/.config/systemd/user/autobackup.timer` (symlink) |
| CLI | `~/.local/bin/autobackup` (wrapper script) |
