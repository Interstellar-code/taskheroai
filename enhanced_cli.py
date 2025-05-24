"""
Enhanced CLI Interface Module for TaskHero AI

This module provides enhanced CLI functionality including:
- Enhanced main menu with integrated task management
- Status indicators and quick project overview
- Additional task management commands
- Help system and keyboard shortcuts
- Search functionality
"""

import os
import time
from typing import Dict, List, Any, Optional
from colorama import Fore, Back, Style, init
from pathlib import Path

# Initialize colorama for Windows
init(autoreset=True)

def get_terminal_size():
    """Get terminal size, with fallback for Windows."""
    try:
        import shutil
        return shutil.get_terminal_size()
    except:
        # Fallback for older Python versions or limited environments
        return (80, 24)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class EnhancedCLI:
    """Enhanced CLI interface for TaskHero AI."""
    
    def __init__(self, app_instance):
        """Initialize the enhanced CLI with a reference to the main app instance."""
        self.app = app_instance
        
    def display_enhanced_menu(self) -> None:
        """Display the enhanced main menu with integrated task management."""
        terminal_width, _ = get_terminal_size()
        menu_width = min(70, terminal_width - 4)
        
        print("\n" + Fore.CYAN + "=" * menu_width + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "TaskHeroAI - AI-Powered Code & Project Assistant".center(menu_width) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * menu_width + Style.RESET_ALL)

        # Show status indicators
        self._display_status_indicators()
        
        # Show quick project overview if task manager is available
        self._display_quick_overview()

        print(Fore.CYAN + "-" * menu_width + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🤖 AI Features" + Style.RESET_ALL)
        print(Fore.GREEN + "1. " + Style.BRIGHT + "💡 Index Code" + Style.RESET_ALL + f" {Fore.CYAN}(Start here){Style.RESET_ALL}")
        print(Fore.GREEN + "2. " + Style.BRIGHT + "💬 Chat with AI" + Style.RESET_ALL + f" {Fore.YELLOW}(Expensive){Style.RESET_ALL}")
        print(Fore.GREEN + "3. " + Style.BRIGHT + "🚀 Max Chat Mode" + Style.RESET_ALL + f" {Fore.RED}(Very Expensive){Style.RESET_ALL}")
        print(Fore.GREEN + "4. " + Style.BRIGHT + "🤖 Agent Mode" + Style.RESET_ALL + f" {Fore.GREEN}(Recommended){Style.RESET_ALL}")
        print(Fore.GREEN + "5. " + Style.BRIGHT + "🔄 Force Reindex" + Style.RESET_ALL)
        print(Fore.GREEN + "6. " + Style.BRIGHT + "📁 View Indexed Files" + Style.RESET_ALL)
        print(Fore.GREEN + "7. " + Style.BRIGHT + "📊 View Project Info" + Style.RESET_ALL)
        print(Fore.GREEN + "8. " + Style.BRIGHT + "🕒 Recent Projects" + Style.RESET_ALL)
        
        print(Fore.CYAN + "-" * menu_width + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📋 Task Management" + Style.RESET_ALL)
        print(Fore.MAGENTA + "9. " + Style.BRIGHT + "📋 Task Dashboard" + Style.RESET_ALL + f" {Fore.CYAN}(Full features){Style.RESET_ALL}")
        print(Fore.MAGENTA + "10. " + Style.BRIGHT + "🎯 Kanban Board" + Style.RESET_ALL + f" {Fore.GREEN}(Visual tasks){Style.RESET_ALL}")
        print(Fore.MAGENTA + "11. " + Style.BRIGHT + "➕ Quick Create Task" + Style.RESET_ALL)
        print(Fore.MAGENTA + "12. " + Style.BRIGHT + "👀 Quick View Tasks" + Style.RESET_ALL)
        print(Fore.MAGENTA + "13. " + Style.BRIGHT + "🔍 Search Tasks" + Style.RESET_ALL)
        print(Fore.MAGENTA + "14. " + Style.BRIGHT + "📈 Project Overview" + Style.RESET_ALL)
        
        print(Fore.CYAN + "-" * menu_width + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🛠️ Tools & Settings" + Style.RESET_ALL)
        print(Fore.GREEN + "15. " + Style.BRIGHT + "🗑️  Project Cleanup" + Style.RESET_ALL)
        print(Fore.GREEN + "16. " + Style.BRIGHT + "⚙️  Settings" + Style.RESET_ALL)
        print(Fore.GREEN + "17. " + Style.BRIGHT + "❓ Help" + Style.RESET_ALL)
        print(Fore.GREEN + "18. " + Style.BRIGHT + "🧹 Clear Screen" + Style.RESET_ALL)
        print(Fore.GREEN + "0. " + Style.BRIGHT + "🚪 Exit" + Style.RESET_ALL)

        print(Fore.CYAN + "=" * menu_width + Style.RESET_ALL)
        
        # Show keyboard shortcuts
        print(f"{Fore.CYAN}💡 Quick shortcuts: {Fore.YELLOW}Ctrl+C{Fore.CYAN} = Cancel, {Fore.YELLOW}h{Fore.CYAN} = Help, {Fore.YELLOW}q{Fore.CYAN} = Quick search{Style.RESET_ALL}")

    def _display_status_indicators(self) -> None:
        """Display system status indicators."""
        status_items = []
        
        if not self.app.indexer:
            status_items.append(f"{Fore.RED}⚠ No code indexed{Style.RESET_ALL}")
        elif self.app.index_outdated:
            status_items.append(f"{Fore.YELLOW}⚠ Index outdated{Style.RESET_ALL}")
        else:
            status_items.append(f"{Fore.GREEN}✓ Code indexed{Style.RESET_ALL}")
        
        # Project management status
        if hasattr(self.app, 'project_planner') and self.app.project_planner:
            try:
                dashboard = self.app.project_planner.get_project_dashboard()
                total_tasks = dashboard.get('total_tasks', 0)
                if total_tasks > 0:
                    progress = dashboard.get('progress_percentage', 0)
                    status_items.append(f"{Fore.CYAN}📋 {total_tasks} tasks ({progress}% done){Style.RESET_ALL}")
                else:
                    status_items.append(f"{Fore.YELLOW}📋 No tasks{Style.RESET_ALL}")
            except:
                status_items.append(f"{Fore.YELLOW}📋 PM ready{Style.RESET_ALL}")
        
        if status_items:
            print(f"\n{Fore.CYAN}Status: {' | '.join(status_items)}{Style.RESET_ALL}")

    def _display_quick_overview(self) -> None:
        """Display a quick project overview."""
        if hasattr(self.app, 'project_planner') and self.app.project_planner:
            try:
                dashboard = self.app.project_planner.get_project_dashboard()
                if dashboard.get('total_tasks', 0) > 0:
                    print(f"\n{Fore.YELLOW}📊 Quick Overview: {dashboard['project_name']}{Style.RESET_ALL}")
                    
                    # Show task status summary in one line
                    task_summary = dashboard.get('task_summary', {})
                    summary_parts = []
                    status_colors = {
                        'todo': Fore.YELLOW,
                        'inprogress': Fore.BLUE, 
                        'testing': Fore.MAGENTA,
                        'devdone': Fore.GREEN,
                        'done': Fore.GREEN + Style.BRIGHT,
                        'backlog': Fore.WHITE
                    }
                    
                    for status, count in task_summary.items():
                        if count > 0:
                            color = status_colors.get(status, Fore.WHITE)
                            status_name = self.app.project_planner.settings['statuses'].get(status, status.title())
                            summary_parts.append(f"{color}{status_name}: {count}{Style.RESET_ALL}")
                    
                    if summary_parts:
                        print(f"{Fore.CYAN}   {' | '.join(summary_parts)}{Style.RESET_ALL}")
                    
                    # Show upcoming deadlines
                    upcoming = dashboard.get('upcoming_deadlines', [])
                    if upcoming:
                        deadline = upcoming[0]
                        print(f"{Fore.RED}   ⚠ Next deadline: {deadline['task']} - {deadline['due_date']}{Style.RESET_ALL}")
            except Exception as e:
                # Silently ignore overview errors
                pass

    def quick_create_task(self) -> None:
        """Quick task creation with minimal input."""
        print(f"\n{Fore.CYAN}⚡ Quick Task Creation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        # Initialize project management components if not already done
        if not hasattr(self.app, 'project_planner') or not self.app.project_planner:
            from mods.project_management.project_planner import ProjectPlanner
            self.app.project_planner = ProjectPlanner()
            self.app.task_manager = self.app.project_planner.task_manager
        
        try:
            title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
            if not title:
                print(f"{Fore.RED}Task title cannot be empty.{Style.RESET_ALL}")
                return
            
            # Ask for priority (optional)
            print(f"\n{Fore.CYAN}Priority (optional):{Style.RESET_ALL}")
            print(f"1. Low")
            print(f"2. Medium (default)")
            print(f"3. High")
            
            priority_choice = input(f"{Fore.GREEN}Select priority (1-3, default=2): {Style.RESET_ALL}").strip()
            priority_map = {"1": "low", "2": "medium", "3": "high"}
            priority = priority_map.get(priority_choice, "medium")
            
            # Create the task
            task_data = {
                "title": title,
                "description": f"Quick task created via enhanced CLI",
                "priority": priority,
                "status": "todo",
                "tags": ["quick-create"]
            }
            
            success = self.app.task_manager.create_task_from_dict(task_data)
            
            if success:
                print(f"\n{Fore.GREEN}✅ Task created successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Title: {title}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Priority: {priority.title()}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Status: TODO{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to create task.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error creating task: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def quick_view_tasks(self) -> None:
        """Quick view of current tasks with compact display."""
        print(f"\n{Fore.CYAN}👀 Quick Task View{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        # Initialize project management components if not already done
        if not hasattr(self.app, 'project_planner') or not self.app.project_planner:
            from mods.project_management.project_planner import ProjectPlanner
            self.app.project_planner = ProjectPlanner()
            self.app.task_manager = self.app.project_planner.task_manager
        
        try:
            # Get active tasks (todo, inprogress, testing)
            all_tasks = self.app.task_manager.get_all_tasks()
            active_statuses = ['todo', 'inprogress', 'testing']
            
            active_tasks = []
            for status in active_statuses:
                if status in all_tasks and all_tasks[status]:
                    for task in all_tasks[status]:
                        active_tasks.append((status, task))
            
            if not active_tasks:
                print(f"{Fore.YELLOW}No active tasks found.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Use option 10 to create a new task.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Found {len(active_tasks)} active tasks:{Style.RESET_ALL}\n")
                
                status_colors = {
                    'todo': Fore.YELLOW,
                    'inprogress': Fore.BLUE, 
                    'testing': Fore.MAGENTA
                }
                
                for i, (status, task) in enumerate(active_tasks, 1):
                    color = status_colors.get(status, Fore.WHITE)
                    status_name = self.app.project_planner.settings['statuses'].get(status, status.title())
                    
                    # Priority indicator
                    priority_indicator = ""
                    if hasattr(task, 'priority') and task.priority:
                        priority_value = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
                        if priority_value == 'high':
                            priority_indicator = f" {Fore.RED}[HIGH]{Style.RESET_ALL}"
                        elif priority_value == 'low':
                            priority_indicator = f" {Fore.WHITE}[LOW]{Style.RESET_ALL}"
                    
                    print(f"  {i:2d}. {color}[{status_name.upper()}]{Style.RESET_ALL} {task.title}{priority_indicator}")
                    
                    # Show due date if exists
                    if hasattr(task, 'due_date') and task.due_date:
                        print(f"      📅 Due: {task.due_date}")
                
                print(f"\n{Fore.CYAN}💡 Use option 9 for full task dashboard or option 12 to search tasks{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error loading tasks: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def quick_search_tasks(self) -> None:
        """Quick search functionality for tasks."""
        print(f"\n{Fore.CYAN}🔍 Quick Task Search{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        # Initialize project management components if not already done
        if not hasattr(self.app, 'project_planner') or not self.app.project_planner:
            from mods.project_management.project_planner import ProjectPlanner
            self.app.project_planner = ProjectPlanner()
            self.app.task_manager = self.app.project_planner.task_manager
        
        try:
            search_query = input(f"{Fore.GREEN}Enter search term: {Style.RESET_ALL}").strip()
            if not search_query:
                print(f"{Fore.YELLOW}Search cancelled.{Style.RESET_ALL}")
                return
            
            # Perform search
            results = self.app.task_manager.search_tasks(search_query)
            
            if not results:
                print(f"{Fore.YELLOW}No tasks found matching '{search_query}'{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}Found {len(results)} tasks matching '{search_query}':{Style.RESET_ALL}\n")
                
                status_colors = {
                    'todo': Fore.YELLOW,
                    'inprogress': Fore.BLUE, 
                    'testing': Fore.MAGENTA,
                    'devdone': Fore.GREEN,
                    'done': Fore.GREEN + Style.BRIGHT,
                    'backlog': Fore.WHITE
                }
                
                for i, task in enumerate(results, 1):
                    status = getattr(task, 'status', 'unknown')
                    color = status_colors.get(status, Fore.WHITE)
                    status_name = self.app.project_planner.settings['statuses'].get(status, status.title())
                    
                    print(f"  {i:2d}. {color}[{status_name.upper()}]{Style.RESET_ALL} {task.title}")
                    
                    # Show description preview if available
                    if hasattr(task, 'description') and task.description:
                        desc_preview = task.description[:80] + "..." if len(task.description) > 80 else task.description
                        print(f"      📝 {desc_preview}")
                
                print(f"\n{Fore.CYAN}💡 Use option 9 for full task management features{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error searching tasks: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def show_project_overview(self) -> None:
        """Show a detailed project overview."""
        print(f"\n{Fore.CYAN}📈 Project Overview{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Initialize project management components if not already done
        if not hasattr(self.app, 'project_planner') or not self.app.project_planner:
            from mods.project_management.project_planner import ProjectPlanner
            self.app.project_planner = ProjectPlanner()
            self.app.task_manager = self.app.project_planner.task_manager
        
        try:
            dashboard = self.app.project_planner.get_project_dashboard()
            
            # Project header
            print(f"\n{Fore.YELLOW}🏠 Project: {Style.BRIGHT}{dashboard['project_name']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📅 Last Updated: {dashboard['last_updated']}{Style.RESET_ALL}")
            
            # Progress summary
            total_tasks = dashboard.get('total_tasks', 0)
            completed_tasks = dashboard.get('completed_tasks', 0)
            progress = dashboard.get('progress_percentage', 0)
            
            print(f"\n{Fore.CYAN}📊 Progress Summary:{Style.RESET_ALL}")
            print(f"   Total Tasks: {Style.BRIGHT}{total_tasks}{Style.RESET_ALL}")
            print(f"   Completed: {Style.BRIGHT}{completed_tasks}{Style.RESET_ALL}")
            print(f"   Progress: {Style.BRIGHT}{progress}%{Style.RESET_ALL}")
            
            # Task breakdown
            task_summary = dashboard.get('task_summary', {})
            if task_summary:
                print(f"\n{Fore.CYAN}📋 Task Breakdown:{Style.RESET_ALL}")
                status_colors = {
                    'backlog': Fore.WHITE,
                    'todo': Fore.YELLOW,
                    'inprogress': Fore.BLUE, 
                    'testing': Fore.MAGENTA,
                    'devdone': Fore.GREEN,
                    'done': Fore.GREEN + Style.BRIGHT
                }
                
                for status, count in task_summary.items():
                    if count > 0:
                        color = status_colors.get(status, Fore.WHITE)
                        status_name = self.app.project_planner.settings['statuses'].get(status, status.title())
                        print(f"   {color}• {status_name}: {count}{Style.RESET_ALL}")
            
            # Upcoming deadlines
            upcoming = dashboard.get('upcoming_deadlines', [])
            if upcoming:
                print(f"\n{Fore.RED}⚠️  Upcoming Deadlines:{Style.RESET_ALL}")
                for i, deadline in enumerate(upcoming[:5], 1):  # Show top 5
                    priority_color = Fore.RED if deadline.get('priority') == 'high' else Fore.YELLOW
                    print(f"   {i}. {priority_color}{deadline['task']} - Due: {deadline['due_date']}{Style.RESET_ALL}")
            
            # Quick actions
            print(f"\n{Fore.CYAN}🚀 Quick Actions:{Style.RESET_ALL}")
            print(f"   • Option 10: Create new task")
            print(f"   • Option 11: View active tasks")
            print(f"   • Option 12: Search tasks")
            print(f"   • Option 9: Full task dashboard")
            
        except Exception as e:
            print(f"{Fore.RED}Error loading project overview: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def show_settings_menu(self) -> None:
        """Show the settings menu with toggle options."""
        print(f"\n{Fore.CYAN}⚙️  Settings{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        # Show current settings
        markdown_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL}" if self.app.enable_markdown_rendering else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        thinking_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL}" if self.app.show_thinking_blocks else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        streaming_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL}" if self.app.enable_streaming_mode else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        
        print(f"\n{Fore.YELLOW}Current Settings:{Style.RESET_ALL}")
        print(f"1. Markdown Rendering: {markdown_status}")
        print(f"2. Thinking Blocks: {thinking_status}")
        print(f"3. Streaming Mode: {streaming_status}")
        
        print(f"\n{Fore.GREEN}Select setting to toggle (1-3), or 0 to return:{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()
        
        if choice == "1":
            self.app.toggle_markdown_rendering()
        elif choice == "2":
            self.app.toggle_thinking_blocks()
        elif choice == "3":
            self.app.toggle_streaming_mode()
        elif choice == "0":
            return
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
            time.sleep(1)

    def show_help(self) -> None:
        """Show comprehensive help information."""
        print(f"\n{Fore.CYAN}❓ TaskHero AI Help{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}🤖 AI Features{Style.RESET_ALL}")
        print(f"   1. Index Code - Analyze your codebase (start here)")
        print(f"   2. Chat with AI - Interactive AI assistance")
        print(f"   3. Max Chat Mode - Enhanced AI with full context")
        print(f"   4. Agent Mode - Efficient AI agent (recommended)")
        print(f"   5. Force Reindex - Rebuild the code index")
        print(f"   6. View Indexed Files - See what's been analyzed")
        print(f"   7. View Project Info - Project statistics")
        print(f"   8. Recent Projects - Access previous projects")
        
        print(f"\n{Fore.YELLOW}📋 Task Management{Style.RESET_ALL}")
        print(f"   9. Task Dashboard - Full task management interface")
        print(f"   10. Kanban Board - Interactive visual task board")
        print(f"   11. Quick Create Task - Fast task creation")
        print(f"   12. Quick View Tasks - See active tasks")
        print(f"   13. Search Tasks - Find specific tasks")
        print(f"   14. Project Overview - Project progress summary")
        
        print(f"\n{Fore.YELLOW}🛠️ Tools & Settings{Style.RESET_ALL}")
        print(f"   15. Project Cleanup - Remove old project data")
        print(f"   16. Settings - Configure application options")
        print(f"   17. Help - Show this help information")
        print(f"   18. Clear Screen - Clear terminal display")
        print(f"   0. Exit - Close the application")
        
        print(f"\n{Fore.CYAN}📚 For more information, visit the project documentation.{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def launch_kanban_board(self) -> None:
        """Launch the interactive Kanban board interface."""
        print(f"\n{Fore.CYAN}🎯 Launching Kanban Board...{Style.RESET_ALL}")
        
        # Initialize project management components if not already done
        if not hasattr(self.app, 'project_planner') or not self.app.project_planner:
            print(f"{Fore.YELLOW}Initializing project management...{Style.RESET_ALL}")
            from mods.project_management.project_planner import ProjectPlanner
            self.app.project_planner = ProjectPlanner()
            self.app.task_manager = self.app.project_planner.task_manager
        
        try:
            # Import and launch the Kanban board
            from mods.project_management.kanban_board import launch_kanban_board
            launch_kanban_board(self.app.task_manager)
            
        except ImportError as e:
            print(f"{Fore.RED}Error: Kanban board module not found.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Make sure the kanban_board module is properly installed.{Style.RESET_ALL}")
            print(f"Details: {e}")
        except Exception as e:
            print(f"{Fore.RED}Error launching Kanban board: {e}{Style.RESET_ALL}")
        
        # Pause before returning to menu
        input(f"\n{Fore.GREEN}Press Enter to return to main menu...{Style.RESET_ALL}") 