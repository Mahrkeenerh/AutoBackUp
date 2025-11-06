#!/bin/bash
set -e

echo "=========================================="
echo "  AutoBackup Uninstallation for Pop!_OS  "
echo "=========================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root/sudo"
    exit 1
fi

# Stop and disable systemd services
echo "[1/5] Stopping and disabling systemd services..."
if systemctl --user is-active --quiet autobackup.service; then
    systemctl --user stop autobackup.service
fi
if systemctl --user is-active --quiet autobackup.timer; then
    systemctl --user stop autobackup.timer
fi

if systemctl --user is-enabled --quiet autobackup.service 2>/dev/null; then
    systemctl --user disable autobackup.service
fi
if systemctl --user is-enabled --quiet autobackup.timer 2>/dev/null; then
    systemctl --user disable autobackup.timer
fi
echo "  ✓ Services stopped and disabled"

# Remove systemd files
echo "[2/5] Removing systemd files..."
rm -f "$HOME/.config/systemd/user/autobackup.service"
rm -f "$HOME/.config/systemd/user/autobackup.timer"
systemctl --user daemon-reload
echo "  ✓ Systemd files removed"

# Remove virtual environment and data
echo "[3/5] Removing virtual environment..."
rm -rf "$HOME/.local/share/autobackup/venv"
echo "  ✓ Virtual environment removed"

# Remove command-line shortcut
echo "[4/5] Removing command-line shortcut..."
rm -f "$HOME/.local/bin/autobackup"
echo "  ✓ Shortcut removed"

# Ask about config and logs
echo "[5/5] Cleaning up config and logs..."
read -p "Do you want to remove config files and logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.config/autobackup"
    rm -rf "$HOME/.local/share/autobackup"
    echo "  ✓ Config and logs removed"
else
    echo "  ✓ Config and logs preserved at:"
    echo "     ~/.config/autobackup/"
    echo "     ~/.local/share/autobackup/"
fi

echo
echo "========================================"
echo "  Uninstallation Complete! ✓"
echo "========================================"
echo
echo "AutoBackup has been removed from your system."
echo
