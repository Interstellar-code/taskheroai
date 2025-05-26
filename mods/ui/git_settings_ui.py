"""
Git Settings UI for TaskHero AI.

Provides user interface for configuring Git integration and auto-update settings.
"""

import asyncio
from typing import Dict, Any, Optional

try:
    from colorama import Fore, Style
except ImportError:
    # Fallback if colorama is not available
    class Fore:
        CYAN = YELLOW = GREEN = RED = ""
    class Style:
        RESET_ALL = BRIGHT = ""

try:
    from ..core import BaseManager
except ImportError:
    # Fallback BaseManager for testing
    class BaseManager:
        def __init__(self, name):
            self.name = name
            import logging
            self.logger = logging.getLogger(name)

        def update_status(self, key, value):
            pass


class GitSettingsUI(BaseManager):
    """User interface for Git settings management."""

    def __init__(self, git_manager=None):
        """
        Initialize the Git Settings UI.

        Args:
            git_manager: Git manager instance
        """
        super().__init__("GitSettingsUI")
        self.git_manager = git_manager

    def _perform_initialization(self) -> None:
        """Initialize the Git Settings UI."""
        self.update_status("git_settings_ui_ready", True)
        self.logger.info("Git Settings UI initialized")

    def display_git_settings_menu(self) -> None:
        """Display the Git settings menu."""
        print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🔄 Git & Updates Configuration".center(70) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        # Get current status
        if self.git_manager:
            status = self.git_manager.get_update_status()
            settings = status.get("settings", {})
            last_check = status.get("last_check")
        else:
            settings = {}
            last_check = None

        # Current Status Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📊 Current Status" + Style.RESET_ALL)

        # Git availability
        git_available = status.get("git_available", False) if self.git_manager else False
        git_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if git_available else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"Git Available: [{git_indicator}]")

        # Repository status
        is_repo = status.get("is_git_repo", False) if self.git_manager else False
        repo_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if is_repo else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"Git Repository: [{repo_indicator}]")

        # Auto-check status
        auto_check = settings.get("auto_check_enabled", True)
        auto_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if auto_check else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"Auto-check Updates: [{auto_indicator}]")

        # Last check
        if last_check and last_check.get("check_timestamp"):
            print(f"Last Check: {Fore.CYAN}{last_check['check_timestamp'][:19]}{Style.RESET_ALL}")
            if last_check.get("update_available"):
                print(f"Update Status: {Fore.YELLOW}Update Available!{Style.RESET_ALL}")
            else:
                print(f"Update Status: {Fore.GREEN}Up to date{Style.RESET_ALL}")
        else:
            print(f"Last Check: {Fore.YELLOW}Never{Style.RESET_ALL}")

        # Configuration Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "⚙️ Configuration" + Style.RESET_ALL)
        print(f"1. {Style.BRIGHT}🔄 Toggle Auto-check Updates{Style.RESET_ALL} [{auto_indicator}]")

        notifications = settings.get("notifications_enabled", True)
        notif_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if notifications else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"2. {Style.BRIGHT}🔔 Toggle Update Notifications{Style.RESET_ALL} [{notif_indicator}]")

        print(f"3. {Style.BRIGHT}🌐 Change Repository URL{Style.RESET_ALL}")

        # Update Operations Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🚀 Update Operations" + Style.RESET_ALL)
        print(f"4. {Style.BRIGHT}🔍 Check for Updates Now{Style.RESET_ALL}")
        print(f"5. {Style.BRIGHT}⬇️ Download & Install Updates{Style.RESET_ALL}")
        print(f"6. {Style.BRIGHT}📋 View Update History{Style.RESET_ALL}")

        # Information Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "ℹ️ Information" + Style.RESET_ALL)
        print(f"7. {Style.BRIGHT}📊 View Version Information{Style.RESET_ALL}")
        print(f"8. {Style.BRIGHT}🔧 Git Repository Status{Style.RESET_ALL}")
        print(f"9. {Style.BRIGHT}🗑️ Clear Update Cache{Style.RESET_ALL}")

        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(f"0. {Style.BRIGHT}🔙 Back to AI Settings{Style.RESET_ALL}")

        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

    async def handle_git_settings_menu(self) -> None:
        """Handle the Git settings menu interaction."""
        while True:
            try:
                self.display_git_settings_menu()
                choice = self.get_user_choice("Choose an option")

                if choice == "0":
                    break
                elif choice == "1":
                    await self._toggle_auto_check()
                elif choice == "2":
                    await self._toggle_notifications()
                elif choice == "3":
                    await self._change_repository_url()
                elif choice == "4":
                    await self._check_for_updates()
                elif choice == "5":
                    await self._perform_update()
                elif choice == "6":
                    await self._view_update_history()
                elif choice == "7":
                    await self._view_version_info()
                elif choice == "8":
                    await self._view_git_status()
                elif choice == "9":
                    await self._clear_cache()
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 0-9.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Returning to AI Settings...{Style.RESET_ALL}")
                break
            except Exception as e:
                self.logger.error(f"Error in Git settings menu: {e}")
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _toggle_auto_check(self) -> None:
        """Toggle auto-check updates setting."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            status = self.git_manager.get_update_status()
            current_setting = status.get("settings", {}).get("auto_check_enabled", True)
            new_setting = not current_setting

            success = self.git_manager.update_git_setting("auto_check_enabled", new_setting)

            if success:
                status_text = "enabled" if new_setting else "disabled"
                print(f"\n{Fore.GREEN}✓ Auto-check updates {status_text}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to update setting{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _toggle_notifications(self) -> None:
        """Toggle update notifications setting."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            status = self.git_manager.get_update_status()
            current_setting = status.get("settings", {}).get("notifications_enabled", True)
            new_setting = not current_setting

            success = self.git_manager.update_git_setting("notifications_enabled", new_setting)

            if success:
                status_text = "enabled" if new_setting else "disabled"
                print(f"\n{Fore.GREEN}✓ Update notifications {status_text}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to update setting{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _change_repository_url(self) -> None:
        """Change the repository URL."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            status = self.git_manager.get_update_status()
            current_url = status.get("settings", {}).get("repository_url", "")

            print(f"\n{Fore.CYAN}Current repository URL:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{current_url}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Enter new repository URL (or press Enter to keep current):{Style.RESET_ALL}")

            new_url = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()

            if new_url and new_url != current_url:
                success = self.git_manager.update_git_setting("repository_url", new_url)
                if success:
                    print(f"\n{Fore.GREEN}✓ Repository URL updated{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}✗ Failed to update repository URL{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Repository URL unchanged{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _check_for_updates(self) -> None:
        """Check for updates now."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            print(f"\n{Fore.CYAN}🔍 Checking for updates...{Style.RESET_ALL}")

            result = self.git_manager.check_for_updates(force_check=True)

            if result.get("success"):
                comparison = result.get("comparison", {})

                print(f"\n{Fore.GREEN}✓ Update check completed{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

                # Current version info
                current = result.get("current", {})
                print(f"Current Version: {Fore.YELLOW}{current.get('version', 'unknown')}{Style.RESET_ALL}")
                print(f"Current Commit: {Fore.YELLOW}{current.get('commit_hash', 'unknown')[:8]}{Style.RESET_ALL}")

                # Remote version info
                remote = result.get("remote", {})
                if remote.get("success"):
                    print(f"Remote Version: {Fore.YELLOW}{remote.get('version', 'unknown')}{Style.RESET_ALL}")
                    print(f"Remote Commit: {Fore.YELLOW}{remote.get('commit_hash', 'unknown')[:8]}{Style.RESET_ALL}")

                # Update status
                if comparison.get("update_available"):
                    print(f"\n{Fore.GREEN}🎉 Update Available!{Style.RESET_ALL}")
                    print(f"Message: {Fore.CYAN}{comparison.get('message', '')}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.GREEN}✓ You are up to date{Style.RESET_ALL}")
                    print(f"Message: {Fore.CYAN}{comparison.get('message', '')}{Style.RESET_ALL}")

                if not comparison.get("can_update") and comparison.get("update_available"):
                    print(f"\n{Fore.YELLOW}⚠️ Cannot update automatically:{Style.RESET_ALL}")
                    if comparison.get("uncommitted_changes"):
                        print(f"  • Uncommitted changes detected")
                    if not comparison.get("is_git_repo"):
                        print(f"  • Not a Git repository")

            else:
                print(f"\n{Fore.RED}✗ Update check failed{Style.RESET_ALL}")
                print(f"Error: {Fore.YELLOW}{result.get('error', 'Unknown error')}{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _perform_update(self) -> None:
        """Perform update with user confirmation."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            # First check if update is available
            print(f"\n{Fore.CYAN}🔍 Checking update status...{Style.RESET_ALL}")
            check_result = self.git_manager.check_for_updates(force_check=True)

            if not check_result.get("success"):
                print(f"\n{Fore.RED}✗ Cannot check for updates: {check_result.get('error')}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            comparison = check_result.get("comparison", {})

            if not comparison.get("update_available"):
                print(f"\n{Fore.GREEN}✓ No updates available{Style.RESET_ALL}")
                print(f"Message: {Fore.CYAN}{comparison.get('message', '')}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            if not comparison.get("can_update"):
                print(f"\n{Fore.YELLOW}⚠️ Cannot update automatically{Style.RESET_ALL}")
                print(f"Reason: {Fore.CYAN}{comparison.get('message', '')}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Show update information
            print(f"\n{Fore.GREEN}🎉 Update Available!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            current = check_result.get("current", {})
            remote = check_result.get("remote", {})

            print(f"Current: {Fore.YELLOW}{current.get('version', 'unknown')} ({current.get('commit_hash', 'unknown')[:8]}){Style.RESET_ALL}")
            print(f"New:     {Fore.GREEN}{remote.get('version', 'unknown')} ({remote.get('commit_hash', 'unknown')[:8]}){Style.RESET_ALL}")

            # Warning about backup
            print(f"\n{Fore.YELLOW}⚠️ Important:{Style.RESET_ALL}")
            print(f"  • User files will be backed up automatically")
            print(f"  • Settings and tasks will be preserved")
            print(f"  • The application will restart after update")

            # Confirmation
            print(f"\n{Fore.CYAN}Do you want to proceed with the update? (y/N):{Style.RESET_ALL}")
            confirm = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip().lower()

            if confirm not in ['y', 'yes']:
                print(f"\n{Fore.YELLOW}Update cancelled{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Perform update
            print(f"\n{Fore.CYAN}🚀 Starting update process...{Style.RESET_ALL}")
            update_result = self.git_manager.perform_update(backup_user_files=True)

            if update_result.get("success"):
                print(f"\n{Fore.GREEN}🎉 Update completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

                git_result = update_result.get("git_result", {})
                print(f"Updated to commit: {Fore.GREEN}{git_result.get('new_commit', 'unknown')[:8]}{Style.RESET_ALL}")

                if update_result.get("backup_created"):
                    print(f"Backup created: {Fore.CYAN}✓{Style.RESET_ALL}")

                print(f"\n{Fore.YELLOW}⚠️ Please restart TaskHero AI to use the updated version{Style.RESET_ALL}")

            else:
                print(f"\n{Fore.RED}✗ Update failed{Style.RESET_ALL}")
                print(f"Error: {Fore.YELLOW}{update_result.get('error', 'Unknown error')}{Style.RESET_ALL}")
                print(f"Stage: {Fore.YELLOW}{update_result.get('stage', 'unknown')}{Style.RESET_ALL}")

                if update_result.get("backup_restored"):
                    print(f"Backup restored: {Fore.GREEN}✓{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _view_update_history(self) -> None:
        """View update history."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            status = self.git_manager.get_update_status()
            history = status.get("settings", {}).get("update_history", [])

            print(f"\n{Fore.CYAN}📋 Update History{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            if not history:
                print(f"{Fore.YELLOW}No update history available{Style.RESET_ALL}")
            else:
                for i, entry in enumerate(reversed(history[-10:]), 1):  # Show last 10
                    timestamp = entry.get("timestamp", "unknown")[:19]
                    commit = entry.get("commit", "unknown")[:8]
                    branch = entry.get("branch", "unknown")
                    success = entry.get("success", False)

                    status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}" if success else f"{Fore.RED}✗{Style.RESET_ALL}"

                    print(f"{i:2}. [{status_icon}] {Fore.CYAN}{timestamp}{Style.RESET_ALL}")
                    print(f"     Commit: {Fore.YELLOW}{commit}{Style.RESET_ALL} | Branch: {Fore.YELLOW}{branch}{Style.RESET_ALL}")
                    print()

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _view_version_info(self) -> None:
        """View detailed version information."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            if self.git_manager.version_manager:
                current = self.git_manager.version_manager.get_current_version()

                print(f"\n{Fore.CYAN}📊 Version Information{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

                print(f"Version: {Fore.YELLOW}{current.get('version', 'unknown')}{Style.RESET_ALL}")
                print(f"Commit Hash: {Fore.YELLOW}{current.get('commit_hash', 'unknown')}{Style.RESET_ALL}")
                print(f"Branch: {Fore.YELLOW}{current.get('branch', 'unknown')}{Style.RESET_ALL}")
                print(f"Last Commit: {Fore.YELLOW}{current.get('last_commit_date', 'unknown')}{Style.RESET_ALL}")
                print(f"Git Repository: {Fore.GREEN if current.get('is_git_repo') else Fore.RED}{'Yes' if current.get('is_git_repo') else 'No'}{Style.RESET_ALL}")
                print(f"Uncommitted Changes: {Fore.RED if current.get('has_uncommitted_changes') else Fore.GREEN}{'Yes' if current.get('has_uncommitted_changes') else 'No'}{Style.RESET_ALL}")

                if current.get("error"):
                    print(f"Error: {Fore.RED}{current['error']}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Version manager not available{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _view_git_status(self) -> None:
        """View Git repository status."""
        try:
            import subprocess
            from pathlib import Path

            print(f"\n{Fore.CYAN}🔧 Git Repository Status{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            # Git status
            try:
                result = subprocess.run(
                    ["git", "status", "--short"],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )

                if result.returncode == 0:
                    if result.stdout.strip():
                        print(f"Working Directory Status:")
                        print(f"{Fore.YELLOW}{result.stdout}{Style.RESET_ALL}")
                    else:
                        print(f"Working Directory: {Fore.GREEN}Clean{Style.RESET_ALL}")
                else:
                    print(f"Git Status: {Fore.RED}Error - {result.stderr}{Style.RESET_ALL}")

            except Exception as e:
                print(f"Git Status: {Fore.RED}Error - {e}{Style.RESET_ALL}")

            # Remote status
            try:
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )

                if result.returncode == 0 and result.stdout.strip():
                    print(f"\nRemote Repositories:")
                    print(f"{Fore.CYAN}{result.stdout}{Style.RESET_ALL}")
                else:
                    print(f"\nRemote Repositories: {Fore.YELLOW}None configured{Style.RESET_ALL}")

            except Exception as e:
                print(f"\nRemote Status: {Fore.RED}Error - {e}{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _clear_cache(self) -> None:
        """Clear update cache."""
        if not self.git_manager:
            print(f"{Fore.RED}Git manager not available{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            if self.git_manager.version_manager:
                self.git_manager.version_manager.clear_cache()
                print(f"\n{Fore.GREEN}✓ Update cache cleared{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Version manager not available{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def get_user_choice(self, prompt: str = "Choose an option") -> str:
        """Get user input choice."""
        print(f"\n{Fore.GREEN}{prompt}:{Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
        return choice
