#!/bin/bash
set -e

echo "========================================"
echo "  AutoBackup Installation"
echo "========================================"
echo

# Get the directory where this script lives (the repository root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root/sudo"
    echo "AutoBackup installs as a user service"
    exit 1
fi

# Check Python version
echo "[1/6] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  Found Python $PYTHON_VERSION"

# Check if notify-send is available
echo "[2/6] Checking notify-send..."
if ! command -v notify-send &> /dev/null; then
    echo "  WARNING: notify-send not found (usually provided by libnotify-bin)"
    echo "  Install it with: sudo apt install libnotify-bin"
else
    echo "  notify-send is available"
fi

# Create virtual environment in repository
echo "[3/6] Setting up virtual environment..."
VENV_DIR="$SCRIPT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment exists, updating..."
else
    echo "  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Install the package into venv
source "$VENV_DIR/bin/activate"
cp -r "$SCRIPT_DIR/src/autobackup" "$VENV_DIR/lib/python"*/site-packages/
deactivate
echo "  Virtual environment ready"

# Create config directory and example config if needed
echo "[4/6] Setting up configuration..."
mkdir -p "$HOME/.config/autobackup"
mkdir -p "$HOME/.local/share/autobackup"

CONFIG_FILE="$HOME/.config/autobackup/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "  Config already exists at $CONFIG_FILE"
else
    cat > "$CONFIG_FILE" << 'EOF'
{
    "sources": [
        "~/Documents",
        "~/Pictures"
    ],
    "lists": [
        "~/.config",
        "~/.local/bin"
    ],
    "destination": "~/Backups",
    "destination_format": "%Y-%m-%d",
    "repeat": true,
    "time_format": "%H",
    "time_value": "19",
    "sleep": 3600,
    "keep_copies": 7
}
EOF
    echo "  Created config at $CONFIG_FILE"
fi

# Symlink systemd service files (not copy!)
echo "[5/6] Installing systemd service (symlinks)..."
mkdir -p "$HOME/.config/systemd/user"
ln -sf "$SCRIPT_DIR/systemd/autobackup.service" "$HOME/.config/systemd/user/"
ln -sf "$SCRIPT_DIR/systemd/autobackup.timer" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
echo "  Systemd services symlinked"

# Create CLI wrapper script
echo "[6/6] Creating command-line shortcut..."
mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/autobackup" << EOF
#!/bin/bash
exec "$SCRIPT_DIR/venv/bin/python" -m autobackup "\$@"
EOF

chmod +x "$HOME/.local/bin/autobackup"
echo "  Created 'autobackup' command"

echo
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Edit your config: $CONFIG_FILE"
echo "     - Set your source directories to backup"
echo "     - Set your destination directory"
echo "     - Configure backup schedule"
echo
echo "  2. Enable and start the service:"
echo "     systemctl --user enable autobackup.service autobackup.timer"
echo "     systemctl --user start autobackup.timer"
echo
echo "  3. Test manually (optional):"
echo "     autobackup --verbose"
echo
echo "  4. Monitor logs:"
echo "     journalctl --user -u autobackup.service -f"
echo

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "NOTE: ~/.local/bin is not in your PATH"
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
fi
