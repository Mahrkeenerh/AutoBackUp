#!/bin/bash
set -e

echo "========================================"
echo "  AutoBackup Installation for Pop!_OS  "
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root/sudo"
    echo "AutoBackup installs to your home directory as a user service"
    exit 1
fi

# Check Python version
echo "[1/8] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  ✓ Found Python $PYTHON_VERSION"

# Check if notify-send is available
echo "[2/8] Checking notify-send..."
if ! command -v notify-send &> /dev/null; then
    echo "WARNING: notify-send not found (usually provided by libnotify-bin)"
    echo "Install it with: sudo apt install libnotify-bin"
else
    echo "  ✓ notify-send is available"
fi

# Create directories
echo "[3/8] Creating directories..."
mkdir -p "$HOME/.config/autobackup"
mkdir -p "$HOME/.local/share/autobackup"
mkdir -p "$HOME/.config/systemd/user"
echo "  ✓ Directories created"

# Create virtual environment
echo "[4/8] Creating virtual environment..."
VENV_DIR="$HOME/.local/share/autobackup/venv"
if [ -d "$VENV_DIR" ]; then
    echo "  ! Virtual environment already exists, removing old one..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install the package
echo "[5/8] Installing AutoBackup..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy the source files to venv
cp -r "$PROJECT_DIR/src/autobackup" "$VENV_DIR/lib/python"*/site-packages/
echo "  ✓ AutoBackup installed"

# Copy example config if config doesn't exist
echo "[6/8] Setting up configuration..."
CONFIG_FILE="$HOME/.config/autobackup/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "  ! Config already exists at $CONFIG_FILE"
else
    cp "$PROJECT_DIR/examples/config.example.json" "$CONFIG_FILE"
    echo "  ✓ Created config at $CONFIG_FILE"
    echo "  ⚠  IMPORTANT: Edit $CONFIG_FILE with your backup paths!"
fi

# Create destination directory from config
if command -v python3 &> /dev/null; then
    DEST_DIR=$(python3 -c "import json, os; config=json.load(open('$CONFIG_FILE')); print(os.path.expanduser(config['destination']))" 2>/dev/null)
    if [ -n "$DEST_DIR" ] && [ ! -d "$DEST_DIR" ]; then
        mkdir -p "$DEST_DIR"
        echo "  ✓ Created destination directory at $DEST_DIR"
    fi
fi

# Install systemd service
echo "[7/8] Installing systemd service..."
cp "$PROJECT_DIR/systemd/autobackup.service" "$HOME/.config/systemd/user/"
cp "$PROJECT_DIR/systemd/autobackup.timer" "$HOME/.config/systemd/user/"

# Reload systemd
systemctl --user daemon-reload

# Enable and start the service
systemctl --user enable autobackup.service
systemctl --user enable autobackup.timer
systemctl --user start autobackup.timer

echo "  ✓ Systemd service installed and enabled"

# Create symlink for CLI
echo "[8/8] Creating command-line shortcut..."
mkdir -p "$HOME/.local/bin"

# Create a wrapper script
cat > "$HOME/.local/bin/autobackup" << 'EOF'
#!/bin/bash
exec "$HOME/.local/share/autobackup/venv/bin/python" -m autobackup "$@"
EOF

chmod +x "$HOME/.local/bin/autobackup"
echo "  ✓ Created 'autobackup' command"

echo
echo "========================================"
echo "  Installation Complete! ✓"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Edit your config: $CONFIG_FILE"
echo "  2. Test the backup: autobackup"
echo "  3. Check service status: systemctl --user status autobackup.service"
echo "  4. View logs: journalctl --user -u autobackup.service -f"
echo
echo "The backup will run automatically based on your config schedule."
echo "Logs are also saved to: ~/.local/share/autobackup/autobackup.log"
echo

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "⚠  NOTE: ~/.local/bin is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
fi
