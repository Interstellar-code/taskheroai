#!/usr/bin/env python3
"""
TaskHero AI Task Migration Script

This script migrates existing tasks from the old location (/mods/project_management/planning)
to the new location (/theherotasks) and updates the app_settings.json configuration.
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


class TaskMigrator:
    """Handles migration of tasks from old to new location."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize the task migrator.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.old_planning_dir = self.project_root / "mods" / "project_management" / "planning"
        self.new_planning_dir = self.project_root / "theherotasks"
        self.app_settings_path = self.project_root / "app_settings.json"

        # Task status directories
        self.status_dirs = ["todo", "inprogress", "testing", "devdone", "done", "backlog", "archive"]

    def check_migration_needed(self) -> Dict[str, any]:
        """Check if migration is needed and return status information.

        Returns:
            Dictionary with migration status information
        """
        status = {
            "migration_needed": False,
            "old_location_exists": False,
            "new_location_exists": False,
            "tasks_in_old_location": 0,
            "tasks_in_new_location": 0,
            "old_location_path": str(self.old_planning_dir),
            "new_location_path": str(self.new_planning_dir)
        }

        # Check if old location exists and has tasks
        if self.old_planning_dir.exists():
            status["old_location_exists"] = True
            status["tasks_in_old_location"] = self._count_tasks_in_directory(self.old_planning_dir)

        # Check if new location exists and has tasks
        if self.new_planning_dir.exists():
            status["new_location_exists"] = True
            status["tasks_in_new_location"] = self._count_tasks_in_directory(self.new_planning_dir)

        # Migration is needed if old location has tasks and either:
        # 1. New location doesn't exist, or
        # 2. New location has fewer tasks than old location
        if status["tasks_in_old_location"] > 0:
            if not status["new_location_exists"] or status["tasks_in_new_location"] < status["tasks_in_old_location"]:
                status["migration_needed"] = True

        return status

    def _count_tasks_in_directory(self, directory: Path) -> int:
        """Count the number of task files in a directory structure.

        Args:
            directory: Directory to count tasks in

        Returns:
            Number of .md files found in status subdirectories
        """
        count = 0
        for status_dir in self.status_dirs:
            status_path = directory / status_dir
            if status_path.exists():
                count += len(list(status_path.glob("*.md")))
        return count

    def migrate_tasks(self, backup: bool = True) -> Dict[str, any]:
        """Migrate tasks from old location to new location.

        Args:
            backup: Whether to create a backup of the old location

        Returns:
            Dictionary with migration results
        """
        result = {
            "success": False,
            "tasks_migrated": 0,
            "errors": [],
            "backup_created": False,
            "backup_path": None
        }

        try:
            # Check if migration is needed
            status = self.check_migration_needed()
            if not status["migration_needed"]:
                result["success"] = True
                result["message"] = "No migration needed"
                return result

            # Create backup if requested
            if backup and self.old_planning_dir.exists():
                backup_path = self.project_root / f"mods_planning_backup_{int(time.time())}"
                shutil.copytree(self.old_planning_dir, backup_path)
                result["backup_created"] = True
                result["backup_path"] = str(backup_path)
                print(f"✓ Created backup at: {backup_path}")

            # Create new directory structure
            self.new_planning_dir.mkdir(parents=True, exist_ok=True)
            for status_dir in self.status_dirs:
                (self.new_planning_dir / status_dir).mkdir(exist_ok=True)

            print(f"✓ Created new directory structure at: {self.new_planning_dir}")

            # Migrate tasks
            tasks_migrated = 0
            for status_dir in self.status_dirs:
                old_status_path = self.old_planning_dir / status_dir
                new_status_path = self.new_planning_dir / status_dir

                if old_status_path.exists():
                    for task_file in old_status_path.glob("*.md"):
                        try:
                            new_task_path = new_status_path / task_file.name

                            # Copy file if it doesn't exist in new location or is newer
                            if not new_task_path.exists() or task_file.stat().st_mtime > new_task_path.stat().st_mtime:
                                shutil.copy2(task_file, new_task_path)
                                tasks_migrated += 1
                                print(f"  ✓ Migrated: {status_dir}/{task_file.name}")

                        except Exception as e:
                            error_msg = f"Failed to migrate {task_file}: {e}"
                            result["errors"].append(error_msg)
                            print(f"  ✗ {error_msg}")

            result["tasks_migrated"] = tasks_migrated
            result["success"] = True

            # Update app_settings.json
            self._update_app_settings()

            print(f"\n✓ Migration completed successfully!")
            print(f"  Tasks migrated: {tasks_migrated}")
            print(f"  New location: {self.new_planning_dir}")

        except Exception as e:
            result["errors"].append(f"Migration failed: {e}")
            print(f"✗ Migration failed: {e}")

        return result

    def _update_app_settings(self) -> None:
        """Update app_settings.json with the new task storage path."""
        try:
            # Load existing settings or create new
            if self.app_settings_path.exists():
                with open(self.app_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {}

            # Update task storage path
            settings["task_storage_path"] = str(self.new_planning_dir)

            # Save updated settings
            with open(self.app_settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✓ Updated app_settings.json with new task storage path")

        except Exception as e:
            print(f"✗ Failed to update app_settings.json: {e}")


def main():
    """Main function for command-line usage."""
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Migrate TaskHero AI tasks to new location")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--check-only", action="store_true", help="Only check migration status")
    parser.add_argument("--project-root", help="Project root directory (default: current directory)")

    args = parser.parse_args()

    # Initialize migrator
    migrator = TaskMigrator(args.project_root)

    print("TaskHero AI Task Migration Tool")
    print("=" * 50)

    # Check migration status
    status = migrator.check_migration_needed()

    print(f"Old location: {status['old_location_path']}")
    print(f"New location: {status['new_location_path']}")
    print(f"Tasks in old location: {status['tasks_in_old_location']}")
    print(f"Tasks in new location: {status['tasks_in_new_location']}")
    print(f"Migration needed: {status['migration_needed']}")

    if args.check_only:
        return

    if not status["migration_needed"]:
        print("\n✓ No migration needed!")
        return

    # Confirm migration
    print(f"\nThis will migrate {status['tasks_in_old_location']} tasks to the new location.")
    if not args.no_backup:
        print("A backup will be created before migration.")

    confirm = input("\nProceed with migration? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Migration cancelled.")
        return

    # Perform migration
    print("\nStarting migration...")
    result = migrator.migrate_tasks(backup=not args.no_backup)

    if result["success"]:
        print(f"\n🎉 Migration completed successfully!")
        if result["backup_created"]:
            print(f"Backup created at: {result['backup_path']}")
    else:
        print(f"\n❌ Migration failed!")
        for error in result["errors"]:
            print(f"  Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
