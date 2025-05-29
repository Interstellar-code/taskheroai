"""SQL analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class SQLAnalyzer(BaseAnalyzer):
    """Analyzer for SQL files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.sql', '.ddl', '.dml', '.pgsql', '.mysql', '.sqlite'}
        self.language_name = 'sql'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze SQL file content."""
        return {
            'functions': self._extract_functions(content),
            'classes': self._extract_tables(content),  # Tables as "classes"
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_sql_patterns(content),
            'tables': self._extract_tables(content),
            'views': self._extract_views(content),
            'procedures': self._extract_procedures(content),
            'triggers': self._extract_triggers(content),
            'indexes': self._extract_indexes(content),
            'constraints': self._extract_constraints(content)
        }
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract SQL functions and stored procedures."""
        functions = []
        lines = content.split('\n')
        
        # SQL function patterns
        function_patterns = [
            r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)\s*\(([^)]*)\)',  # CREATE FUNCTION
            r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)\s*\(([^)]*)\)', # CREATE PROCEDURE
            r'DELIMITER\s+\$\$\s*CREATE\s+FUNCTION\s+(\w+)\s*\(([^)]*)\)',   # MySQL function
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip().upper()
            
            for pattern in function_patterns:
                match = re.search(pattern, stripped, re.IGNORECASE)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2) if len(match.groups()) > 1 else ''
                    
                    # Parse arguments
                    args = self._parse_sql_arguments(args_str)
                    
                    # Determine function type
                    if 'PROCEDURE' in stripped:
                        func_type = 'stored_procedure'
                    else:
                        func_type = 'function'
                    
                    functions.append({
                        'name': func_name,
                        'args': args,
                        'line_number': i,
                        'signature': line.strip(),
                        'type': func_type
                    })
                    break
        
        return functions
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract table definitions."""
        tables = []
        lines = content.split('\n')
        
        # Table creation patterns
        table_patterns = [
            r'CREATE\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)',
            r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMPORARY\s+)?TABLE\s+(\w+)',
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in table_patterns:
                match = re.search(pattern, stripped, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    
                    # Extract columns from table definition
                    columns = self._extract_table_columns(lines, i)
                    
                    tables.append({
                        'name': table_name,
                        'line_number': i,
                        'columns': columns,
                        'type': 'table',
                        'is_temporary': 'TEMPORARY' in stripped.upper()
                    })
                    break
        
        return tables
    
    def _extract_views(self, content: str) -> List[Dict[str, Any]]:
        """Extract view definitions."""
        views = []
        lines = content.split('\n')
        
        view_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(view_pattern, line.strip(), re.IGNORECASE)
            if match:
                view_name = match.group(1)
                
                # Extract view query
                view_query = self._extract_view_query(lines, i)
                
                views.append({
                    'name': view_name,
                    'line_number': i,
                    'query': view_query,
                    'type': 'view'
                })
        
        return views
    
    def _extract_procedures(self, content: str) -> List[Dict[str, Any]]:
        """Extract stored procedure definitions."""
        procedures = []
        lines = content.split('\n')
        
        procedure_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)\s*\(([^)]*)\)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(procedure_pattern, line.strip(), re.IGNORECASE)
            if match:
                proc_name = match.group(1)
                args_str = match.group(2)
                
                # Parse arguments
                args = self._parse_sql_arguments(args_str)
                
                procedures.append({
                    'name': proc_name,
                    'args': args,
                    'line_number': i,
                    'type': 'stored_procedure'
                })
        
        return procedures
    
    def _extract_triggers(self, content: str) -> List[Dict[str, Any]]:
        """Extract trigger definitions."""
        triggers = []
        lines = content.split('\n')
        
        trigger_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+(\w+)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(trigger_pattern, line.strip(), re.IGNORECASE)
            if match:
                trigger_name = match.group(1)
                
                # Extract trigger details
                trigger_details = self._extract_trigger_details(lines, i)
                
                triggers.append({
                    'name': trigger_name,
                    'line_number': i,
                    'type': 'trigger',
                    **trigger_details
                })
        
        return triggers
    
    def _extract_indexes(self, content: str) -> List[Dict[str, Any]]:
        """Extract index definitions."""
        indexes = []
        lines = content.split('\n')
        
        index_patterns = [
            r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)\s+ON\s+(\w+)',
            r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+(?:UNIQUE\s+)?INDEX\s+(\w+)',
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in index_patterns:
                match = re.search(pattern, stripped, re.IGNORECASE)
                if match:
                    if 'CREATE' in stripped.upper():
                        index_name = match.group(1)
                        table_name = match.group(2)
                    else:
                        table_name = match.group(1)
                        index_name = match.group(2)
                    
                    indexes.append({
                        'name': index_name,
                        'table': table_name,
                        'line_number': i,
                        'type': 'index',
                        'is_unique': 'UNIQUE' in stripped.upper()
                    })
                    break
        
        return indexes
    
    def _extract_constraints(self, content: str) -> List[Dict[str, Any]]:
        """Extract constraint definitions."""
        constraints = []
        lines = content.split('\n')
        
        constraint_patterns = [
            r'CONSTRAINT\s+(\w+)\s+(PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CHECK)',
            r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+CONSTRAINT\s+(\w+)',
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in constraint_patterns:
                match = re.search(pattern, stripped, re.IGNORECASE)
                if match:
                    if 'ALTER' in stripped.upper():
                        table_name = match.group(1)
                        constraint_name = match.group(2)
                        constraint_type = 'unknown'
                    else:
                        constraint_name = match.group(1)
                        constraint_type = match.group(2).lower().replace(' ', '_')
                        table_name = None
                    
                    constraints.append({
                        'name': constraint_name,
                        'type': constraint_type,
                        'table': table_name,
                        'line_number': i
                    })
                    break
        
        return constraints
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract SQL imports (schema references, external data sources)."""
        imports = []
        lines = content.split('\n')
        
        import_patterns = [
            r'USE\s+(\w+)',  # USE database
            r'\\i\s+([^\s;]+)',  # PostgreSQL \i include
            r'SOURCE\s+([^\s;]+)',  # MySQL SOURCE
            r'@([^\s;]+)',  # SQL Server script execution
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in import_patterns:
                match = re.search(pattern, stripped, re.IGNORECASE)
                if match:
                    import_name = match.group(1)
                    
                    # Determine import type
                    if 'USE' in stripped.upper():
                        import_type = 'database_use'
                    elif '\\i' in stripped:
                        import_type = 'postgresql_include'
                    elif 'SOURCE' in stripped.upper():
                        import_type = 'mysql_source'
                    elif stripped.startswith('@'):
                        import_type = 'sqlserver_script'
                    else:
                        import_type = 'unknown'
                    
                    imports.append({
                        'name': import_name,
                        'line_number': i,
                        'statement': stripped,
                        'type': import_type
                    })
                    break
        
        return imports
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract SQL exports (tables, views, functions that can be referenced)."""
        exports = []
        
        # Extract from already parsed objects
        tables = self._extract_tables(content)
        views = self._extract_views(content)
        functions = self._extract_functions(content)
        
        # Add tables as exports
        for table in tables:
            exports.append({
                'name': table['name'],
                'type': 'table',
                'line_number': table['line_number']
            })
        
        # Add views as exports
        for view in views:
            exports.append({
                'name': view['name'],
                'type': 'view',
                'line_number': view['line_number']
            })
        
        # Add functions as exports
        for func in functions:
            exports.append({
                'name': func['name'],
                'type': func['type'],
                'line_number': func['line_number']
            })
        
        return exports
    
    def _extract_sql_patterns(self, content: str) -> List[str]:
        """Extract SQL-specific patterns."""
        patterns = []
        content_upper = content.upper()
        
        # DDL patterns
        if 'CREATE TABLE' in content_upper:
            patterns.append('table_creation')
        
        if 'CREATE VIEW' in content_upper:
            patterns.append('views')
        
        if 'CREATE INDEX' in content_upper:
            patterns.append('indexes')
        
        if 'CREATE TRIGGER' in content_upper:
            patterns.append('triggers')
        
        if 'CREATE PROCEDURE' in content_upper or 'CREATE FUNCTION' in content_upper:
            patterns.append('stored_procedures')
        
        # DML patterns
        if 'SELECT' in content_upper:
            patterns.append('data_selection')
        
        if 'INSERT' in content_upper:
            patterns.append('data_insertion')
        
        if 'UPDATE' in content_upper:
            patterns.append('data_modification')
        
        if 'DELETE' in content_upper:
            patterns.append('data_deletion')
        
        # Advanced patterns
        if 'JOIN' in content_upper:
            patterns.append('table_joins')
        
        if 'UNION' in content_upper:
            patterns.append('set_operations')
        
        if 'CASE WHEN' in content_upper:
            patterns.append('conditional_logic')
        
        if 'WITH' in content_upper and 'AS' in content_upper:
            patterns.append('common_table_expressions')
        
        if 'WINDOW' in content_upper or 'OVER(' in content_upper:
            patterns.append('window_functions')
        
        if 'CURSOR' in content_upper:
            patterns.append('cursors')
        
        if 'TRANSACTION' in content_upper or 'COMMIT' in content_upper or 'ROLLBACK' in content_upper:
            patterns.append('transactions')
        
        # Database-specific patterns
        if 'DELIMITER' in content_upper:
            patterns.append('mysql_specific')
        
        if '\\' in content and ('\\i' in content or '\\d' in content):
            patterns.append('postgresql_specific')
        
        if 'GO' in content_upper:
            patterns.append('sqlserver_specific')
        
        return list(set(patterns))
    
    def _parse_sql_arguments(self, args_str: str) -> List[Dict[str, Any]]:
        """Parse SQL function/procedure arguments."""
        args = []
        if not args_str.strip():
            return args
        
        # Split arguments
        arg_parts = [arg.strip() for arg in args_str.split(',')]
        
        for arg in arg_parts:
            if not arg:
                continue
            
            # Parse argument with type and direction
            arg_info = {
                'name': arg,
                'type': None,
                'direction': 'IN',  # Default direction
                'default': None
            }
            
            # Check for parameter direction (IN, OUT, INOUT)
            if arg.upper().startswith(('IN ', 'OUT ', 'INOUT ')):
                parts = arg.split(None, 1)
                arg_info['direction'] = parts[0].upper()
                arg = parts[1] if len(parts) > 1 else ''
            
            # Check for default value
            if 'DEFAULT' in arg.upper():
                arg_parts = arg.split('DEFAULT', 1)
                arg = arg_parts[0].strip()
                arg_info['default'] = arg_parts[1].strip()
            
            # Parse name and type
            parts = arg.split()
            if len(parts) >= 2:
                arg_info['name'] = parts[0]
                arg_info['type'] = ' '.join(parts[1:])
            else:
                arg_info['name'] = arg
            
            args.append(arg_info)
        
        return args
    
    def _extract_table_columns(self, lines: List[str], table_start: int) -> List[Dict[str, Any]]:
        """Extract columns from a table definition."""
        columns = []
        in_table = False
        paren_count = 0
        
        for i in range(table_start - 1, len(lines)):
            line = lines[i].strip()
            
            if not in_table and '(' in line:
                in_table = True
                paren_count = line.count('(') - line.count(')')
                continue
            
            if in_table:
                paren_count += line.count('(') - line.count(')')
                
                # Column definition pattern
                col_match = re.search(r'(\w+)\s+([A-Z][A-Z0-9_()]*)', line, re.IGNORECASE)
                if col_match and not line.upper().strip().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    
                    # Check for constraints
                    is_primary = 'PRIMARY KEY' in line.upper()
                    is_not_null = 'NOT NULL' in line.upper()
                    is_unique = 'UNIQUE' in line.upper()
                    
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'is_primary_key': is_primary,
                        'is_not_null': is_not_null,
                        'is_unique': is_unique,
                        'line_number': i + 1
                    })
                
                if paren_count <= 0:
                    break
        
        return columns
    
    def _extract_view_query(self, lines: List[str], view_start: int) -> str:
        """Extract the query from a view definition."""
        query_lines = []
        found_as = False
        
        for i in range(view_start - 1, len(lines)):
            line = lines[i].strip()
            
            if not found_as and 'AS' in line.upper():
                found_as = True
                # Include the part after AS
                as_index = line.upper().find('AS')
                query_lines.append(line[as_index + 2:].strip())
                continue
            
            if found_as:
                query_lines.append(line)
                
                # Stop at semicolon or next statement
                if line.endswith(';') or line.upper().startswith(('CREATE', 'DROP', 'ALTER')):
                    break
        
        return ' '.join(query_lines).strip()
    
    def _extract_trigger_details(self, lines: List[str], trigger_start: int) -> Dict[str, Any]:
        """Extract trigger timing and event details."""
        details = {
            'timing': None,
            'event': None,
            'table': None
        }
        
        # Look for trigger details in the same line or next few lines
        for i in range(trigger_start - 1, min(len(lines), trigger_start + 3)):
            line = lines[i].strip().upper()
            
            # Extract timing
            if 'BEFORE' in line:
                details['timing'] = 'BEFORE'
            elif 'AFTER' in line:
                details['timing'] = 'AFTER'
            elif 'INSTEAD OF' in line:
                details['timing'] = 'INSTEAD OF'
            
            # Extract event
            if 'INSERT' in line:
                details['event'] = 'INSERT'
            elif 'UPDATE' in line:
                details['event'] = 'UPDATE'
            elif 'DELETE' in line:
                details['event'] = 'DELETE'
            
            # Extract table
            on_match = re.search(r'ON\s+(\w+)', line)
            if on_match:
                details['table'] = on_match.group(1)
        
        return details
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate complexity for SQL based on statements and joins."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        content_upper = content.upper()
        
        # SQL complexity factors
        tables = len(re.findall(r'CREATE\s+TABLE', content_upper))
        joins = len(re.findall(r'\bJOIN\b', content_upper))
        subqueries = len(re.findall(r'\(\s*SELECT', content_upper))
        procedures = len(re.findall(r'CREATE\s+PROCEDURE', content_upper))
        triggers = len(re.findall(r'CREATE\s+TRIGGER', content_upper))
        
        complexity_score = (tables * 1.0 + joins * 0.5 + subqueries * 1.5 + 
                          procedures * 2.0 + triggers * 1.5)
        
        # Normalize by content length
        if non_empty_lines:
            complexity_score = complexity_score / len(non_empty_lines) * 10
        
        return min(complexity_score, 10.0)
    
    def count_lines_of_code(self, content: str) -> int:
        """Count meaningful content lines in SQL."""
        lines = content.split('\n')
        content_lines = 0
        
        for line in lines:
            stripped = line.strip()
            # Count non-empty lines that aren't just comments
            if stripped and not stripped.startswith('--') and not stripped.startswith('/*'):
                content_lines += 1
        
        return content_lines
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a SQL comment."""
        return line.strip().startswith('--') or line.strip().startswith('/*')
