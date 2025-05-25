#!/usr/bin/env python
"""Fix script for malformed CLI manager methods."""

import re

def fix_cli_manager():
    # Read the file
    with open('mods/cli/cli_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix malformed _handle_menu_choice method
    menu_choice_replacement = '''    def _handle_menu_choice(self, choice: str) -> None:
        """Handle user menu choice with reorganized menu structure."""
        try:
            # Indexing & Embedding Section (1-4)
            if choice == "1":
                self._handle_index_code()
            elif choice == "2":
                self._handle_view_files()
            elif choice == "3":
                self._handle_view_project()
            elif choice == "4":
                self._handle_recent_projects()
            # Chat with Code Section (5-7)
            elif choice == "5":
                self._handle_chat_ai()
            elif choice == "6":
                self._handle_max_chat()
            elif choice == "7":
                self._handle_agent_mode()
            # TaskHero Management Section (8-12)
            elif choice == "8":
                self._handle_task_dashboard()
            elif choice == "9":
                self._handle_kanban_board()
            elif choice == "10":
                self._handle_quick_create_task()
            elif choice == "11":
                self._handle_quick_view_tasks()
            elif choice == "12":
                self._handle_search_tasks()
            # Settings & Tools Section
            elif choice == "0":
                self._handle_exit()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-12 or 0 to exit.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error handling choice {choice}: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")'''

    # Fix malformed placeholder methods
    placeholder_methods_replacement = '''    def _handle_view_files(self) -> None:
        """Handle view indexed files option."""
        print(f"\\n{Fore.CYAN}📁 View Indexed Files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display all indexed files with metadata and filtering options.{Style.RESET_ALL}")
        input(f"\\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_view_project(self) -> None:
        """Handle view project info option."""
        print(f"\\n{Fore.CYAN}📊 View Project Info{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display project structure, statistics, and analysis.{Style.RESET_ALL}")
        input(f"\\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_recent_projects(self) -> None:
        """Handle recent projects option."""
        print(f"\\n{Fore.CYAN}📚 Recent Projects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will show recently indexed projects with quick switching.{Style.RESET_ALL}")
        input(f"\\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")'''

    # Find and replace the malformed menu choice method
    pattern1 = r'    def _handle_menu_choice\(self, choice: str\) -> None:.*?print\(f"\{Fore\.RED\}Error: \{e\}\{Style\.RESET_ALL\}"\)'
    content = re.sub(pattern1, menu_choice_replacement, content, flags=re.DOTALL)

    # Find and replace the malformed placeholder methods
    pattern2 = r'def _handle_view_files\(self\) -> None:.*?input\(f"\\n\{Fore\.CYAN\}Press Enter to continue\.\.\.\{Style\.RESET_ALL\}"\)'
    content = re.sub(pattern2, placeholder_methods_replacement, content, flags=re.DOTALL)

    # Write back to file
    with open('mods/cli/cli_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print('✅ Fixed the malformed methods in cli_manager.py')

if __name__ == "__main__":
    fix_cli_manager() 