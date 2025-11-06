# AutoBackup

Simple, automated backup utility for Pop!_OS and Ubuntu-based Linux distributions.

## Features

- 📁 **Automated Backups** - Schedule backups to run daily, weekly, or monthly
- 🔔 **Desktop Notifications** - Get notified when backups complete
- 📝 **Directory Listings** - Create manifests of directory contents
- 🗂️ **Rotation Policy** - Automatically remove old backups
- ⏰ **Systemd Integration** - Runs automatically on startup
- 📊 **Logging** - All operations logged to file and systemd journal

## Quick Start

### Installation

```bash
# Clone or download this repository
cd AutoBackUp

# Run the installation script
./scripts/install.sh
```

The installer will:
- Create a virtual environment in `~/.local/share/autobackup/`
- Install systemd services for auto-startup
- Create a config template at `~/.config/autobackup/config.json`
- Add the `autobackup` command to your PATH

### Configuration

Edit your configuration file:

```bash
nano ~/.config/autobackup/config.json
```

Example configuration:

```json
{
    "sources": [
        "~/Documents",
        "~/Pictures"
    ],
    "lists": [
        "~/.config"
    ],
    "destination": "~/Backups",
    "destination_format": "%Y-%m-%d",
    "repeat": true,
    "time_format": "%H",
    "time_value": "19",
    "sleep": 3600,
    "keep_copies": 7
}
```

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `sources` | Directories to backup (full recursive copy) | `["~/Documents"]` |
| `lists` | Directories to list contents of (no copy) | `["~/.config"]` |
| `destination` | Where to save backups | `"~/Backups"` |
| `destination_format` | Backup folder naming (strftime format) | `"%Y-%m-%d"` |
| `repeat` | Run repeatedly (true) or once (false) | `true` |
| `time_format` | Time unit to match: `%H` (hour), `%d` (day of month), `%w` (weekday) | `"%H"` |
| `time_value` | When to run backup | `"19"` (7 PM) |
| `sleep` | Seconds to wait after backup (prevents duplicates) | `3600` |
| `keep_copies` | Number of backup versions to keep | `7` |

**Note:** Use `~` for home directory - it will be expanded automatically.

### Schedule Examples

**Daily backup at 7 PM:**
```json
{
    "time_format": "%H",
    "time_value": "19"
}
```

**Weekly backup on Sunday (day 0):**
```json
{
    "time_format": "%w",
    "time_value": "0"
}
```

**Monthly backup on the 1st:**
```json
{
    "time_format": "%d",
    "time_value": "01"
}
```

## Usage

### Manual Backup

Run a backup immediately:

```bash
autobackup
```

Run with verbose output:

```bash
autobackup --verbose
```

### Systemd Service Management

Check service status:

```bash
systemctl --user status autobackup.service
```

View logs:

```bash
journalctl --user -u autobackup.service -f
```

Restart service (after config changes):

```bash
systemctl --user restart autobackup.service
```

Stop auto-startup:

```bash
systemctl --user stop autobackup.timer
systemctl --user disable autobackup.timer
```

Re-enable auto-startup:

```bash
systemctl --user enable autobackup.timer
systemctl --user start autobackup.timer
```

## Logs

Logs are saved to two locations:

1. **File:** `~/.local/share/autobackup/autobackup.log`
2. **Journal:** `journalctl --user -u autobackup.service`

View recent log file:

```bash
tail -f ~/.local/share/autobackup/autobackup.log
```

## Uninstallation

```bash
./scripts/uninstall.sh
```

This will:
- Stop and disable the systemd service
- Remove the virtual environment
- Remove the `autobackup` command
- Optionally remove config files and logs

## Backup Structure

Backups are organized by timestamp:

```
~/Backups/
├── 2025-01-15/
│   ├── Documents/
│   ├── Pictures/
│   └── ListingContents.txt
├── 2025-01-16/
│   ├── Documents/
│   ├── Pictures/
│   └── ListingContents.txt
└── 2025-01-17/
    ├── Documents/
    ├── Pictures/
    └── ListingContents.txt
```

The `ListingContents.txt` file contains directory listings of paths specified in `lists`.

## Troubleshooting

### Command not found: autobackup

Add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Service not starting

Check for config errors:

```bash
autobackup --verbose
```

View service logs:

```bash
journalctl --user -u autobackup.service -n 50
```

### Backup destination doesn't exist

The destination directory must exist before running backups:

```bash
mkdir -p ~/Backups  # or your configured destination
```

### Notifications not showing

Install libnotify-bin:

```bash
sudo apt install libnotify-bin
```

## Advanced Usage

### Custom Config File

Use a different config file:

```bash
autobackup --config /path/to/config.json
```

### Run in Daemon Mode Manually

```bash
autobackup --daemon
```

(This is normally handled by systemd)

## Requirements

- **OS:** Pop!_OS 22.04+ or Ubuntu 22.04+
- **Python:** 3.8 or higher (pre-installed)
- **notify-send:** For desktop notifications (usually pre-installed)

## Files and Directories

```
~/.config/autobackup/config.json          # Your configuration
~/.local/share/autobackup/venv/           # Virtual environment
~/.local/share/autobackup/autobackup.log  # Log file
~/.config/systemd/user/autobackup.*       # Systemd services
~/.local/bin/autobackup                   # Command-line wrapper
```

## Support

For bugs or questions:
- Create an issue on GitHub
- Email: samuelbuban@gmail.com

## License

Free to use and modify.

## Disclaimer

Always test your backup configuration before relying on it. The author takes no responsibility for data loss.
