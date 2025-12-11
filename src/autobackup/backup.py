"""Core backup functionality for AutoBackUp."""

import os
import shutil
import datetime
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupError(Exception):
    """Custom exception for backup errors."""
    pass


def notify(title: str, message: str):
    """Send desktop notification using notify-send."""
    try:
        import subprocess
        subprocess.run(
            ["notify-send", "-i", "drive-harddisk", title, message],
            check=False,
            timeout=5
        )
    except Exception as e:
        logger.warning(f"Failed to send notification: {e}")


def load_config(config_path: Optional[Path] = None) -> Dict:
    """Load configuration from JSON file."""
    if config_path is None:
        # Try XDG config location first, fall back to current directory
        xdg_config = Path.home() / ".config" / "autobackup" / "config.json"
        local_config = Path("config.json")
        old_config = Path("config.txt")

        if xdg_config.exists():
            config_path = xdg_config
        elif local_config.exists():
            config_path = local_config
        elif old_config.exists():
            config_path = old_config
        else:
            raise BackupError(f"Config file not found. Expected at {xdg_config}")

    logger.info(f"Loading config from {config_path}")

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise BackupError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise BackupError(f"Failed to load config: {e}")


def validate_config(config: Dict) -> List[str]:
    """
    Validate configuration and return list of errors.
    Returns empty list if valid.
    """
    errors = []

    # Check sources
    if 'sources' not in config and 'lists' not in config:
        errors.append("Config must have 'sources' or 'lists'")
        return errors

    sources = config.get('sources', [])
    lists = config.get('lists', [])

    # Validate source paths
    for source in sources:
        source_path = Path(source).expanduser()
        if not source_path.exists():
            errors.append(f"Source path doesn't exist: {source}")
        elif not source_path.is_dir():
            errors.append(f"Source path is not a directory: {source}")

    # Validate list paths
    for list_path in lists:
        list_path_obj = Path(list_path).expanduser()
        if not list_path_obj.exists():
            errors.append(f"List path doesn't exist: {list_path}")
        elif not list_path_obj.is_dir():
            errors.append(f"List path is not a directory: {list_path}")

    # Check destination
    if 'destination' not in config:
        errors.append("Missing 'destination' in config")
    else:
        dest = Path(config['destination']).expanduser()
        if not dest.exists():
            errors.append(f"Destination path doesn't exist: {config['destination']}")
        elif not dest.is_dir():
            errors.append(f"Destination is not a directory: {config['destination']}")

    # Check destination_format
    if 'destination_format' not in config:
        errors.append("Missing 'destination_format' in config")
    else:
        try:
            datetime.datetime.now().strftime(config['destination_format'])
        except Exception:
            errors.append(f"Invalid destination_format: {config['destination_format']}")

    # Check repeat
    if 'repeat' in config and not isinstance(config['repeat'], bool):
        errors.append("'repeat' must be true or false")

    # Check time_format if repeat is enabled
    if config.get('repeat', False):
        if 'time_format' not in config:
            errors.append("Missing 'time_format' (required when repeat=true)")
        else:
            try:
                datetime.datetime.now().strftime(config['time_format'])
            except Exception:
                errors.append(f"Invalid time_format: {config['time_format']}")

        if 'time_value' not in config:
            errors.append("Missing 'time_value' (required when repeat=true)")

        if 'sleep' not in config:
            errors.append("Missing 'sleep' (required when repeat=true)")
        elif not isinstance(config['sleep'], int):
            errors.append("'sleep' must be an integer")

    # Check keep_copies
    if 'keep_copies' not in config:
        errors.append("Missing 'keep_copies' in config")
    elif not isinstance(config['keep_copies'], int) or config['keep_copies'] < 1:
        errors.append("'keep_copies' must be an integer >= 1")

    return errors


def cleanup_old_backups(destination_dir: Path, keep_copies: int):
    """Remove old backups, keeping only the most recent keep_copies."""
    if not destination_dir.exists():
        return

    # Get all subdirectories with their modification times
    backups = []
    for item in destination_dir.iterdir():
        if item.is_dir():
            backups.append((item, item.stat().st_mtime))

    # Sort by modification time (oldest first)
    backups.sort(key=lambda x: x[1])

    # Remove oldest backups
    while len(backups) >= keep_copies:
        old_backup = backups.pop(0)[0]
        logger.info(f"Removing old backup: {old_backup}")
        try:
            shutil.rmtree(old_backup)
        except Exception as e:
            logger.error(f"Failed to remove old backup {old_backup}: {e}")


def create_listing_file(destination: Path, list_paths: List[str]):
    """Create separate listing files for each directory in a listings directory."""
    listings_dir = destination / "listings"

    try:
        # Create the listings directory
        listings_dir.mkdir(parents=True, exist_ok=True)

        for list_path in list_paths:
            list_path_obj = Path(list_path).expanduser()

            # Create a sanitized filename from the path
            # Replace path separators and problematic characters with underscores
            sanitized_name = str(list_path_obj).replace(os.sep, '_').replace(':', '_').replace('~', 'home')
            if sanitized_name.startswith('_'):
                sanitized_name = sanitized_name[1:]
            listing_file = listings_dir / f"{sanitized_name}.txt"

            with open(listing_file, 'w') as f:
                f.write(f"{list_path}\n\n")
                if list_path_obj.exists() and list_path_obj.is_dir():
                    contents = sorted(os.listdir(list_path_obj))
                    f.write("\n".join(contents))
                    f.write("\n")

            logger.info(f"Created listing file: {listing_file}")
    except Exception as e:
        logger.error(f"Failed to create listing files: {e}")
        raise BackupError(f"Failed to create listing files: {e}")


def perform_backup(config: Dict) -> bool:
    """
    Perform backup based on configuration.
    Returns True if successful, False otherwise.
    """
    sources = config.get('sources', [])
    lists = config.get('lists', [])
    destination_raw = Path(config['destination']).expanduser()
    dest_format = config['destination_format']
    keep_copies = config['keep_copies']

    # Create timestamped backup directory
    timestamp = datetime.datetime.now().strftime(dest_format)
    destination = destination_raw / timestamp

    # Check for duplicate (same timestamp)
    if destination.exists():
        msg = f"Backup already exists: {destination}"
        logger.warning(msg)
        notify("Backup Already Exists", msg)
        return False

    logger.info(f"Starting backup to {destination}")
    notify("AutoBackup", "Starting backup...")

    # Cleanup old backups first
    cleanup_old_backups(destination_raw, keep_copies)

    # Create backup directory
    try:
        destination.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create backup directory: {e}")
        notify("Backup Error", f"Failed to create directory: {e}")
        return False

    # Create listing file if list paths specified
    if lists:
        try:
            create_listing_file(destination, lists)
        except BackupError as e:
            notify("Backup Error", str(e))
            return False

    # Custom ignore function that can check full paths
    def ignore_function(directory, names):
        """Custom ignore function that handles both patterns and path-based exclusions."""
        ignored = set()

        # Pattern-based ignores
        pattern_ignore = shutil.ignore_patterns(
            "*.ini", "My *",
            # Cache directories
            ".cache", "Cache", "cache", "cache2", "CachedData",
            # Package managers
            "node_modules", ".npm", ".yarn", ".pnpm-store",
            ".gradle", ".m2", ".cargo",
            # Python
            "__pycache__", "*.pyc", "*.pyo",
            # Thumbnails and trash
            ".thumbnails", ".Trash", ".Trash-*",
            # IDE caches
            ".vscode", ".idea",
            # Browser specific
            "cache2",  # Firefox cache
            # Logs
            "*.log",
            # Special files that can't be copied
            "*Socket", "*Lock", "*Cookie", "*.pipe"
        )
        ignored.update(pattern_ignore(directory, names))

        # Path-based ignores - check if we're in specific subdirectories
        dir_path = Path(directory)
        for name in names:
            full_path = dir_path / name
            # Ignore .local/share directory
            if full_path.match("*/.local/share"):
                ignored.add(name)
            # Ignore .steam directories (huge runtime environments)
            elif full_path.match("*/.steam"):
                ignored.add(name)
            # Ignore .var (flatpak app data)
            elif full_path.match("*/.var"):
                ignored.add(name)

        return ignored

    # Copy source directories
    errors = []
    for source in sources:
        source_path = Path(source).expanduser()
        dest_path = destination / source_path.name

        try:
            logger.info(f"Copying {source_path} -> {dest_path}")
            shutil.copytree(
                source_path,
                dest_path,
                ignore=ignore_function,
                symlinks=True,  # Copy symlinks as symlinks, don't follow them
                ignore_dangling_symlinks=True,  # Ignore broken symlinks
                dirs_exist_ok=True
            )
        except Exception as e:
            # Convert exception to string and limit size to avoid overwhelming logs
            error_str = str(e)
            if len(error_str) > 1000:
                error_str = error_str[:1000] + f"... ({len(error_str)} chars total)"
            error_msg = f"Failed to copy {source}: {error_str}"
            logger.error(error_msg)
            errors.append(f"Failed to copy {source}")

    # Report results
    if errors:
        notify("Backup Completed with Errors", f"{len(errors)} errors occurred")
        return False
    else:
        logger.info("Backup completed successfully")
        notify("AutoBackup", "Backup completed successfully!")
        return True
