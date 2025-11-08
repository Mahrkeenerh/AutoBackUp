#!/usr/bin/env python3
"""
AutoBackup - Simple backup utility for Linux.

Usage:
    autobackup              # Run backup once (or start scheduled mode from systemd)
    autobackup --daemon     # Run in daemon mode with scheduling
    autobackup --config PATH # Use specific config file
"""

import sys
import argparse
import logging
import datetime
from time import sleep
from pathlib import Path
from typing import Optional

from .backup import load_config, validate_config, perform_backup, notify, BackupError


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    log_dir = Path.home() / ".local" / "share" / "autobackup"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "autobackup.log"

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_daemon(config: dict, config_path: Optional[Path] = None):
    """Run in daemon mode with scheduling."""
    logger = logging.getLogger(__name__)
    logger.info("Starting AutoBackup daemon mode")
    if config_path:
        logger.info(f"Using custom config file: {config_path}")

    while True:
        # Check if it's time to run
        current_time = datetime.datetime.now().strftime(config['time_format'])

        if current_time == config['time_value']:
            logger.info(f"Time match ({config['time_format']}={current_time}), running backup...")

            # Reload config before each backup
            try:
                config = load_config(config_path)
                errors = validate_config(config)
                if errors:
                    logger.error("Config validation failed:")
                    for error in errors:
                        logger.error(f"  - {error}")
                    notify("AutoBackup Error", f"Config validation failed: {errors[0]}")
                    return 1
            except BackupError as e:
                logger.error(f"Failed to reload config: {e}")
                notify("AutoBackup Error", str(e))
                return 1

            # Perform backup
            try:
                perform_backup(config)
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                notify("AutoBackup Error", f"Backup failed: {e}")

            # Sleep to avoid running multiple times in the same time window
            logger.info(f"Sleeping for {config['sleep']} seconds")
            sleep(config['sleep'])
        else:
            # Check again in 60 seconds
            sleep(60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AutoBackup - Simple backup utility for Linux"
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to config file (default: ~/.config/autobackup/config.json)'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run in daemon mode with scheduling (normally used by systemd)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load and validate config
        config = load_config(args.config)
        errors = validate_config(config)

        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            notify("AutoBackup Error", f"Config error: {errors[0]}")
            return 1

        # Check mode
        if args.daemon or config.get('repeat', False):
            # Daemon mode with scheduling
            if not config.get('repeat', False):
                logger.error("--daemon requires 'repeat': true in config")
                notify("AutoBackup Error", "Daemon mode requires repeat=true in config")
                return 1

            return run_daemon(config, args.config)
        else:
            # Single run mode
            logger.info("Running backup once...")
            success = perform_backup(config)
            return 0 if success else 1

    except BackupError as e:
        logger.error(f"Backup error: {e}")
        notify("AutoBackup Error", str(e))
        return 1
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        notify("AutoBackup Error", f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
