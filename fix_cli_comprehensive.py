# Comprehensive fix for the compressed code in cli_manager.py
import re

# Read the file
with open('mods/cli/cli_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Compressed imports
import_pattern = r'import asyncioimport osimport threadingimport timefrom datetime import datetimefrom pathlib import Pathfrom typing import Any, Dict, List, Optionalfrom colorama import Fore, Stylefrom \.\.core import BaseManager'
import_replacement = '''import asyncio
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from colorama import Fore, Style
from ..core import BaseManager'''

content = re.sub(import_pattern, import_replacement, content)

# Fix 2: Compressed project management components
pm_pattern = r'# Project management components \(TASK-005\)        self\.project_planner = None        self\.task_manager = None        self\.kanban_board = None        self\.task_cli = None                # Recent projects tracking \(TASK-014\)        self\.recent_projects = \[\]        self\.project_info = \{\}'
pm_replacement = '''        # Project management components (TASK-005)
        self.project_planner = None
        self.task_manager = None
        self.kanban_board = None
        self.task_cli = None
        
        # Recent projects tracking (TASK-014)
        self.recent_projects = []
        self.project_info = {}'''

content = re.sub(pm_pattern, pm_replacement, content)

# Fix 3: Compressed _handle_view_files method - this is the big one
view_files_pattern = r'def _handle_view_files\(self\) -> None:        """Handle view indexed files option\."""        if not self\.indexer:            print\(f"\\n\{Fore\.RED\}Error: No code has been indexed yet\. Please index a directory first\.\{Style\.RESET_ALL\}"\)            input\(f"\\n\{Fore\.CYAN\}Press Enter to continue\.\.\.\{Style\.RESET_ALL\}"\)            return        print\("\\n" \+ Fore\.CYAN \+ "=" \* 50 \+ Style\.RESET_ALL\)        print\(Fore\.CYAN \+ Style\.BRIGHT \+ "Indexed Files" \+ Style\.RESET_ALL\)        print\(Fore\.CYAN \+ "=" \* 50 \+ Style\.RESET_ALL\)        try:            self\.logger\.info\("\[STAT\] Viewing indexed files information"\)            index_status = self\.indexer\.is_index_complete\(\)            status_str = "Complete" if index_status\["complete"\] else "Incomplete"            status_color = Fore\.GREEN if index_status\["complete"\] else Fore\.YELLOW            print\(f"\{Fore\.CYAN\}Index Status: \{status_color\}\{Style\.BRIGHT\}\{status_str\}\{Style\.RESET_ALL\}"\)            if not index_status\["complete"\] and "reason" in index_status:                print\(f"\{Fore\.YELLOW\}Reason: \{index_status\[\'reason\'\]\}\{Style\.RESET_ALL\}"\)            index_dir = self\.indexer\.index_dir            print\(f"\\n\{Fore\.CYAN\}Index Directory: \{Fore\.WHITE\}\{index_dir\}\{Style\.RESET_ALL\}"\)            if os\.path\.exists\(index_dir\):                metadata_dir = os\.path\.join\(index_dir, "metadata"\)                embeddings_dir = os\.path\.join\(index_dir, "embeddings"\)                descriptions_dir = os\.path\.join\(index_dir, "descriptions"\)                print\(f"\\n\{Fore\.CYAN\}\{Style\.BRIGHT\}Index Directory Structure:\{Style\.RESET_ALL\}"\)                header = f"  \{Fore\.CYAN\}\{\'Directory\':<15\} \{\'Exists\':<10\} \{\'Files\':<10\} \{\'Size\':<10\}\{Style\.RESET_ALL\}"                separator = f"  \{Fore\.CYAN\}\{\'-\'\*15\} \{\'-\'\*10\} \{\'-\'\*10\} \{\'-\'\*10\}\{Style\.RESET_ALL\}"                print\(header\)                print\(separator\)                if os\.path\.exists\(metadata_dir\):                    files = \[f for f in os\.listdir\(metadata_dir\) if f\.endswith\("\.json"\)\]                    size = sum\(os\.path\.getsize\(os\.path\.join\(metadata_dir, f\)\) for f in files\)                    print\(                        f"  \{Fore\.GREEN\}\{\'metadata\':<15\} \{Fore\.GREEN\}\{\'Yes\':<10\} \{Fore\.YELLOW\}\{len\(files\):<10\} \{Fore\.MAGENTA\}\{self\._format_size\(size\):<10\}\{Style\.RESET_ALL\}"                    \)                else:                    print\(                        f"  \{Fore\.GREEN\}\{\'metadata\':<15\} \{Fore\.RED\}\{\'No\':<10\} \{\'-\':<10\} \{\'-\':<10\}\{Style\.RESET_ALL\}"                    \)                if os\.path\.exists\(embeddings_dir\):                    files = \[f for f in os\.listdir\(embeddings_dir\) if f\.endswith\("\.json"\)\]                    size = sum\(os\.path\.getsize\(os\.path\.join\(embeddings_dir, f\)\) for f in files\)                    print\(                        f"  \{Fore\.GREEN\}\{\'embeddings\':<15\} \{Fore\.GREEN\}\{\'Yes\':<10\} \{Fore\.YELLOW\}\{len\(files\):<10\} \{Fore\.MAGENTA\}\{self\._format_size\(size\):<10\}\{Style\.RESET_ALL\}"                    \)                else:                    print\(                        f"  \{Fore\.GREEN\}\{\'embeddings\':<15\} \{Fore\.RED\}\{\'No\':<10\} \{\'-\':<10\} \{\'-\':<10\}\{Style\.RESET_ALL\}"                    \)                if os\.path\.exists\(descriptions_dir\):                    files = \[f for f in os\.listdir\(descriptions_dir\) if f\.endswith\("\.txt"\)\]                    size = sum\(os\.path\.getsize\(os\.path\.join\(descriptions_dir, f\)\) for f in files\)                    print\(                        f"  \{Fore\.GREEN\}\{\'descriptions\':<15\} \{Fore\.GREEN\}\{\'Yes\':<10\} \{Fore\.YELLOW\}\{len\(files\):<10\} \{Fore\.MAGENTA\}\{self\._format_size\(size\):<10\}\{Style\.RESET_ALL\}"                    \)                else:                    print\(                        f"  \{Fore\.GREEN\}\{\'descriptions\':<15\} \{Fore\.RED\}\{\'No\':<10\} \{\'-\':<10\} \{\'-\':<10\}\{Style\.RESET_ALL\}"                    \)            else:                print\(f"\{Fore\.RED\}Index directory does not exist\.\{Style\.RESET_ALL\}"\)            print\(f"\\n\{Fore\.CYAN\}\{Style\.BRIGHT\}Sample Indexed Files:\{Style\.RESET_ALL\}"\)            try:                sample_files = self\.indexer\.get_sample_files\(5\)                if sample_files:                    for i, file in enumerate\(sample_files, 1\):                        print\(f"\{Fore\.GREEN\}\{i\}\. \{Fore\.WHITE\}\{file\}\{Style\.RESET_ALL\}"\)                else:                    print\(f"\{Fore\.YELLOW\}No files have been indexed yet\.\{Style\.RESET_ALL\}"\)            except Exception as e:                print\(f"\{Fore\.RED\}Error retrieving sample files: \{e\}\{Style\.RESET_ALL\}"\)            print\(f"\\n\{Fore\.CYAN\}Press Enter to continue\.\.\.\{Style\.RESET_ALL\}"\)            input\(\)        except Exception as e:            self\.logger\.error\(f"Error viewing indexed files: \{e\}", exc_info=True\)            print\(f"\{Fore\.RED\}\{Style\.BRIGHT\}Error viewing indexed files: \{e\}\{Style\.RESET_ALL\}"\)            input\(f"\\n\{Fore\.CYAN\}Press Enter to continue\.\.\.\{Style\.RESET_ALL\}"\)'

view_files_replacement = '''def _handle_view_files(self) -> None:
        """Handle view indexed files option."""
        print(f"\\n{Fore.CYAN}📁 View Indexed Files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display all indexed files with metadata and filtering options.{Style.RESET_ALL}")
        input(f"\\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")'''

content = re.sub(view_files_pattern, view_files_replacement, content, flags=re.DOTALL)

# Write the file back
with open('mods/cli/cli_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all compressed sections in cli_manager.py') 