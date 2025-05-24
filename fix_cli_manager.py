import re

# Read the file
with open('mods/cli/cli_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the compressed import section first
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

# Fix the project management components line
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

# Write the file back
with open('mods/cli/cli_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed compressed sections in cli_manager.py') 