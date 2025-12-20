#!/bin/bash
set -e

echo "========================================"
echo "  AutoBackup Uninstallation"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root/sudo"
    exit 1
fi

# Stop and disable systemd services
echo "[1/4] Stopping and disabling systemd services..."
systemctl --user stop autobackup.service 2>/dev/null || true
systemctl --user stop autobackup.timer 2>/dev/null || true
systemctl --user disable autobackup.service 2>/dev/null || true
systemctl --user disable autobackup.timer 2>/dev/null || true
echo "  Services stopped and disabled"

# Remove systemd symlinks
echo "[2/4] Removing systemd symlinks..."
rm -f "$HOME/.config/systemd/user/autobackup.service"
rm -f "$HOME/.config/systemd/user/autobackup.timer"
systemctl --user daemon-reload
echo "  Systemd symlinks removed"

# Remove command-line shortcut
echo "[3/4] Removing command-line shortcut..."
rm -f "$HOME/.local/bin/autobackup"
echo "  Shortcut removed"

# Ask about config and logs
echo "[4/4] Cleaning up config and logs..."
read -p "Remove config and log files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.config/autobackup"
    rm -rf "$HOME/.local/share/autobackup"
    echo "  Config and logs removed"
else
    echo "  Config and logs preserved at:"
    echo "    ~/.config/autobackup/"
    echo "    ~/.local/share/autobackup/"
fi

echo
echo "========================================"
echo "  Uninstallation Complete!"
echo "========================================"
echo
echo "AutoBackup system integrations have been removed."
echo "Repository remains at: $SCRIPT_DIR"
echo
echo "To completely remove, delete the repository:"
echo "  rm -rf \"$SCRIPT_DIR\""
echo
