"""
Smart CLI Manager for TaskHero AI.

This module provides an enhanced CLI manager that uses the SmartIndexer
for intelligent indexing decisions based on log analysis.
"""

import os
import time
from typing import Optional
from colorama import Fore, Style, init

from ..core.base_manager import BaseManager
from ..code.smart_indexer import SmartIndexer
from ..code.indexer import FileIndexer
from ..code.file_selector import FileSelector
from ..project_management.project_analyzer import ProjectAnalyzer
from ..ai.ai_manager import AIManager

# Initialize colorama for Windows
init(autoreset=True)


class SmartCLIManager(BaseManager):
    """Enhanced CLI Manager with smart indexing capabilities."""
    
    def __init__(self):
        """Initialize the Smart CLI Manager."""
        super().__init__()
        self.smart_indexer: Optional[SmartIndexer] = None
        self.indexer: Optional[FileIndexer] = None
        self.file_selector: Optional[FileSelector] = None
        self.project_analyzer: Optional[ProjectAnalyzer] = None
        self.ai_manager: Optional[AIManager] = None
        
    def _handle_index_code(self) -> None:
        """Handle index code option with smart indexing."""
        print(f"\n{Fore.GREEN}🚀 Smart Code Indexing{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Get directory to index
        directory = self._get_directory_to_index()
        if not directory:
            return
            
        # Initialize smart indexer
        if not self.smart_indexer or self.smart_indexer.root_path != directory:
            print(f"{Fore.YELLOW}🔧 Initializing smart indexer for: {directory}{Style.RESET_ALL}")
            self.smart_indexer = SmartIndexer(directory)
            
            # Also initialize regular components for compatibility
            self.indexer = self.smart_indexer.indexer
            self.file_selector = FileSelector()
            self.project_analyzer = ProjectAnalyzer(self.indexer)
            
            # Set AI manager dependencies when indexer is created
            if self.ai_manager:
                self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
        
        # Step 1: Analyze current indexing status
        print(f"\n{Fore.GREEN}📊 Step 1: Analyzing current indexing status...{Style.RESET_ALL}")
        
        status = self.smart_indexer.get_indexing_status()
        
        print(f"{Fore.CYAN}Current Status: {status['overall_status'].upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Message: {status['message']}{Style.RESET_ALL}")
        
        if status['analysis']['log_files_found'] > 0:
            print(f"{Fore.CYAN}Recent logs found: {status['analysis']['log_files_found']}{Style.RESET_ALL}")
            if status['analysis']['last_indexing_time']:
                time_str = status['analysis']['last_indexing_time'].strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Fore.CYAN}Last indexing: {time_str}{Style.RESET_ALL}")
        
        # Show recommendations
        if status['analysis']['recommendations']:
            print(f"\n{Fore.YELLOW}💡 Recommendations:{Style.RESET_ALL}")
            for rec in status['analysis']['recommendations']:
                print(f"  • {rec}")
        
        # Step 2: Ask user what to do
        print(f"\n{Fore.GREEN}🤔 Step 2: Choose indexing action{Style.RESET_ALL}")
        
        options = [
            ("Smart Index", "Let the system decide what needs indexing"),
            ("Force Reindex", "Force complete re-indexing of all files"),
            ("Status Only", "Just show status and exit"),
            ("Cancel", "Return to main menu")
        ]
        
        print(f"\n{Fore.CYAN}Available options:{Style.RESET_ALL}")
        for i, (option, description) in enumerate(options, 1):
            print(f"  {i}. {Fore.WHITE}{option}{Style.RESET_ALL} - {description}")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Select option (1-{len(options)}): {Style.RESET_ALL}").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(options):
                    selected_option = options[choice_idx][0]
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1-{len(options)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
        
        # Step 3: Execute chosen action
        if selected_option == "Cancel":
            print(f"{Fore.YELLOW}Indexing cancelled.{Style.RESET_ALL}")
            return
        elif selected_option == "Status Only":
            print(f"{Fore.GREEN}✅ Status check complete.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}⚡ Step 3: Executing {selected_option.lower()}...{Style.RESET_ALL}")
        
        # Perform the indexing
        force_reindex = (selected_option == "Force Reindex")
        
        start_time = time.time()
        result = self.smart_indexer.smart_index(force_reindex=force_reindex)
        
        # Step 4: Show results
        print(f"\n{Fore.GREEN}📋 Step 4: Indexing Results{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if result['status'] == 'no_action_needed':
            print(f"{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏱️  Analysis time: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
        elif result['status'] == 'completed':
            print(f"{Fore.GREEN}🎉 Indexing completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Files indexed: {result['files_indexed']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📁 Files processed: {result['files_to_process']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏱️  Processing time: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📄 Log file: {result.get('log_file', 'N/A')}{Style.RESET_ALL}")
            
            # Show scan type
            scan_type = result['analysis'].get('scan_type', 'unknown')
            print(f"{Fore.CYAN}🔍 Scan type: {scan_type}{Style.RESET_ALL}")
        elif result['status'] == 'failed':
            print(f"{Fore.RED}❌ Indexing failed: {result['error']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏱️  Time before failure: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
        
        # Step 5: Cleanup and final status
        print(f"\n{Fore.GREEN}🧹 Step 5: Cleanup and final status{Style.RESET_ALL}")
        
        # Cleanup old logs (keep last 7 days)
        deleted_logs = self.smart_indexer.cleanup_old_logs(keep_days=7)
        if deleted_logs > 0:
            print(f"{Fore.CYAN}🗑️  Cleaned up {deleted_logs} old log files{Style.RESET_ALL}")
        
        # Show final status
        final_status = self.smart_indexer.get_indexing_status()
        print(f"{Fore.GREEN}✅ Final status: {final_status['overall_status'].upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Total indexed files: {final_status['metadata_files']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}🎯 Smart indexing complete!{Style.RESET_ALL}")
    
    def _get_directory_to_index(self) -> Optional[str]:
        """Get directory to index from user input."""
        print(f"\n{Fore.CYAN}📂 Directory Selection{Style.RESET_ALL}")
        
        # Default to current directory
        current_dir = os.getcwd()
        print(f"Current directory: {Fore.WHITE}{current_dir}{Style.RESET_ALL}")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}Use current directory? (y/n/path): {Style.RESET_ALL}").strip().lower()
            
            if choice in ['y', 'yes', '']:
                return current_dir
            elif choice in ['n', 'no']:
                # Ask for custom path
                custom_path = input(f"{Fore.YELLOW}Enter directory path: {Style.RESET_ALL}").strip()
                if custom_path and os.path.isdir(custom_path):
                    return os.path.abspath(custom_path)
                else:
                    print(f"{Fore.RED}Invalid directory path: {custom_path}{Style.RESET_ALL}")
            elif os.path.isdir(choice):
                return os.path.abspath(choice)
            else:
                print(f"{Fore.RED}Invalid input. Enter 'y' for current directory, 'n' to specify path, or a valid directory path.{Style.RESET_ALL}")
    
    def run(self) -> None:
        """Run the smart CLI manager."""
        print(f"\n{Fore.GREEN}🚀 TaskHero AI - Smart CLI Manager{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Enhanced with intelligent indexing capabilities{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        while True:
            print(f"\n{Fore.GREEN}📋 Main Menu{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*30}{Style.RESET_ALL}")
            
            options = [
                ("Smart Index Code", "Intelligent code indexing with log analysis"),
                ("AI Task Creation", "Create tasks using AI (requires indexed code)"),
                ("Project Analysis", "Analyze project structure and dependencies"),
                ("File Search", "Search through indexed files"),
                ("System Status", "Check indexing and system status"),
                ("Exit", "Exit the application")
            ]
            
            for i, (option, description) in enumerate(options, 1):
                print(f"  {i}. {Fore.WHITE}{option}{Style.RESET_ALL} - {description}")
            
            try:
                choice = input(f"\n{Fore.YELLOW}Select option (1-{len(options)}): {Style.RESET_ALL}").strip()
                choice_idx = int(choice) - 1
                
                if choice_idx == 0:  # Smart Index Code
                    self._handle_index_code()
                elif choice_idx == 1:  # AI Task Creation
                    self._handle_ai_task_creation()
                elif choice_idx == 2:  # Project Analysis
                    self._handle_project_analysis()
                elif choice_idx == 3:  # File Search
                    self._handle_file_search()
                elif choice_idx == 4:  # System Status
                    self._handle_system_status()
                elif choice_idx == 5:  # Exit
                    print(f"\n{Fore.GREEN}👋 Thank you for using TaskHero AI Smart CLI!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1-{len(options)}.{Style.RESET_ALL}")
                    
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ An error occurred: {str(e)}{Style.RESET_ALL}")
                self.logger.error(f"CLI error: {e}", exc_info=True)
    
    def _handle_ai_task_creation(self) -> None:
        """Handle AI task creation."""
        if not self.smart_indexer:
            print(f"{Fore.RED}❌ Please index code first before using AI task creation.{Style.RESET_ALL}")
            return
            
        # Check if we have a recent index
        status = self.smart_indexer.get_indexing_status()
        if status['overall_status'] in ['missing', 'incomplete']:
            print(f"{Fore.RED}❌ Index is {status['overall_status']}. Please run indexing first.{Style.RESET_ALL}")
            return
            
        print(f"{Fore.YELLOW}🤖 AI Task Creation feature coming soon...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This will integrate with the existing AI task creation system.{Style.RESET_ALL}")
    
    def _handle_project_analysis(self) -> None:
        """Handle project analysis."""
        if not self.smart_indexer:
            print(f"{Fore.RED}❌ Please index code first before project analysis.{Style.RESET_ALL}")
            return
            
        print(f"{Fore.YELLOW}📊 Project Analysis feature coming soon...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This will provide insights into project structure and dependencies.{Style.RESET_ALL}")
    
    def _handle_file_search(self) -> None:
        """Handle file search."""
        if not self.smart_indexer:
            print(f"{Fore.RED}❌ Please index code first before file search.{Style.RESET_ALL}")
            return
            
        print(f"{Fore.YELLOW}🔍 File Search feature coming soon...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This will provide semantic search through indexed files.{Style.RESET_ALL}")
    
    def _handle_system_status(self) -> None:
        """Handle system status check."""
        print(f"\n{Fore.GREEN}🔍 System Status Check{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.smart_indexer:
            status = self.smart_indexer.get_indexing_status()
            
            print(f"{Fore.CYAN}📂 Project: {self.smart_indexer.project_name}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📁 Root path: {self.smart_indexer.root_path}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Index status: {status['overall_status'].upper()}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💬 Message: {status['message']}{Style.RESET_ALL}")
            
            if status['analysis']['last_indexing_time']:
                time_str = status['analysis']['last_indexing_time'].strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Fore.CYAN}⏰ Last indexing: {time_str}{Style.RESET_ALL}")
            
            # Show recent logs
            recent_logs = self.smart_indexer.get_recent_indexing_logs()
            if recent_logs:
                print(f"\n{Fore.CYAN}📄 Recent log files ({len(recent_logs)}):{Style.RESET_ALL}")
                for log in recent_logs[:3]:  # Show last 3
                    log_name = os.path.basename(log['file'])
                    time_str = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  • {log_name} ({time_str})")
        else:
            print(f"{Fore.YELLOW}⚠️  No smart indexer initialized yet.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Run 'Smart Index Code' to initialize the system.{Style.RESET_ALL}")


def main():
    """Main entry point for the smart CLI manager."""
    try:
        manager = SmartCLIManager()
        manager.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 