"""
Indexing Logger for TaskHero AI.

Provides detailed logging and tracking of indexing operations.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class IndexingLogger:
    """Logger for detailed indexing operations tracking."""
    
    def __init__(self, project_root: str, logs_dir: str = "logs"):
        """
        Initialize the indexing logger.
        
        Args:
            project_root: Root directory of the project being indexed
            logs_dir: Directory where logs should be stored
        """
        self.project_root = project_root
        self.logs_dir = logs_dir
        self.project_name = os.path.basename(project_root)
        
        # Ensure logs directory exists
        os.makedirs(logs_dir, exist_ok=True)
        
        # Generate log file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(logs_dir, f"indexing_{self.project_name}_{timestamp}.log")
        self.json_file = os.path.join(logs_dir, f"indexing_{self.project_name}_{timestamp}.json")
        
        # Initialize log data
        self.log_data = {
            "project_name": self.project_name,
            "project_root": project_root,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "indexed_files": [],
            "ignored_files": [],
            "failed_files": [],
            "statistics": {
                "total_files_found": 0,
                "files_to_index": 0,
                "files_indexed": 0,
                "files_ignored": 0,
                "files_failed": 0,
                "total_size": 0,
                "processing_time": 0
            },
            "directory_analysis": {},
            "file_types": {}
        }
        
        self.start_time = datetime.now()
        self._write_log("📊 Starting indexing process", "INFO")
        
    def log_pre_analysis(self, analysis: Dict[str, Any]) -> None:
        """Log pre-indexing directory analysis."""
        self.log_data["directory_analysis"] = analysis
        self._write_log("🔍 Pre-indexing analysis completed", "INFO")
        self._write_log(f"  • Total files found: {analysis.get('total_files', 0)}", "INFO")
        self._write_log(f"  • Files to index: {analysis.get('files_to_index', 0)}", "INFO")
        self._write_log(f"  • Files to ignore: {analysis.get('files_to_ignore', 0)}", "INFO")
        
        # Log directory breakdown
        directories = analysis.get('directories', {})
        for dir_path, info in directories.items():
            file_count = info.get('file_count', 0)
            if file_count > 0:
                self._write_log(f"  📁 {dir_path}: {file_count} files", "INFO")
    
    def log_file_indexed(self, file_path: str, file_size: int, processing_time: float = 0) -> None:
        """Log successfully indexed file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        file_info = {
            "path": rel_path,
            "absolute_path": file_path,
            "size": file_size,
            "extension": file_ext,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        self.log_data["indexed_files"].append(file_info)
        self.log_data["statistics"]["files_indexed"] += 1
        self.log_data["statistics"]["total_size"] += file_size
        
        # Track file types
        if file_ext:
            self.log_data["file_types"][file_ext] = self.log_data["file_types"].get(file_ext, 0) + 1
        
        self._write_log(f"✅ Indexed: {rel_path} ({self._format_size(file_size)})", "SUCCESS")
    
    def log_file_ignored(self, file_path: str, reason: str = "gitignore") -> None:
        """Log ignored file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        ignore_info = {
            "path": rel_path,
            "absolute_path": file_path,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_data["ignored_files"].append(ignore_info)
        self.log_data["statistics"]["files_ignored"] += 1
        
        self._write_log(f"⏭️ Ignored: {rel_path} ({reason})", "IGNORED")
    
    def log_file_failed(self, file_path: str, error: str) -> None:
        """Log failed file processing."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        fail_info = {
            "path": rel_path,
            "absolute_path": file_path,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_data["failed_files"].append(fail_info)
        self.log_data["statistics"]["files_failed"] += 1
        
        self._write_log(f"❌ Failed: {rel_path} - {error}", "ERROR")
    
    def log_progress(self, current: int, total: int) -> None:
        """Log indexing progress."""
        if total > 0:
            percent = (current / total) * 100
            self._write_log(f"📈 Progress: {current}/{total} ({percent:.1f}%)", "PROGRESS")
    
    def finalize(self) -> str:
        """Finalize logging and return log file path."""
        end_time = datetime.now()
        processing_time = (end_time - self.start_time).total_seconds()
        
        self.log_data["status"] = "completed"
        self.log_data["end_timestamp"] = end_time.isoformat()
        self.log_data["statistics"]["processing_time"] = processing_time
        
        # Write summary
        stats = self.log_data["statistics"]
        self._write_log("🎉 Indexing completed!", "INFO")
        self._write_log(f"📊 Final Statistics:", "INFO")
        self._write_log(f"  • Files indexed: {stats['files_indexed']}", "INFO")
        self._write_log(f"  • Files ignored: {stats['files_ignored']}", "INFO")
        self._write_log(f"  • Files failed: {stats['files_failed']}", "INFO")
        self._write_log(f"  • Total size processed: {self._format_size(stats['total_size'])}", "INFO")
        self._write_log(f"  • Processing time: {processing_time:.2f} seconds", "INFO")
        
        # Write final JSON log
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
        
        return self.log_file
    
    def _write_log(self, message: str, level: str = "INFO") -> None:
        """Write message to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get current log summary."""
        return {
            "log_file": self.log_file,
            "json_file": self.json_file,
            "statistics": self.log_data["statistics"].copy(),
            "file_types": self.log_data["file_types"].copy()
        }


class PreIndexingAnalyzer:
    """Analyzer for pre-indexing directory analysis."""
    
    def __init__(self, root_path: str, gitignore_path: Optional[str] = None):
        """
        Initialize the pre-indexing analyzer.
        
        Args:
            root_path: Root directory to analyze
            gitignore_path: Path to .gitignore file
        """
        self.root_path = root_path
        self.gitignore_path = gitignore_path
        
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze directory structure before indexing.
        
        Returns:
            Dictionary with analysis results
        """
        from .directory import DirectoryParser
        
        # Initialize parser with gitignore
        parser = DirectoryParser(self.root_path, self.gitignore_path)
        root_entry = parser.parse()
        
        analysis = {
            "total_files": 0,
            "files_to_index": 0,
            "files_to_ignore": 0,
            "total_size": 0,
            "directories": {},
            "file_types": {},
            "large_files": [],  # Files > 1MB
            "gitignore_patterns": []
        }
        
        # Get gitignore patterns
        if self.gitignore_path and os.path.exists(self.gitignore_path):
            try:
                with open(self.gitignore_path, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    analysis["gitignore_patterns"] = patterns[:10]  # Show first 10
            except Exception:
                pass
        
        # Analyze directory structure
        self._analyze_entry(root_entry, parser, analysis, "")
        
        return analysis
    
    def _analyze_entry(self, entry, parser, analysis: Dict[str, Any], rel_path: str) -> None:
        """Recursively analyze directory entry."""
        from .indexer import FileIndexer
        
        if entry.is_file():
            analysis["total_files"] += 1
            
            # Check if file would be indexed
            dummy_indexer = FileIndexer(self.root_path)
            should_index = dummy_indexer._should_index_file(entry)
            is_ignored = parser._is_ignored(entry.path, False)
            
            if should_index and not is_ignored:
                analysis["files_to_index"] += 1
                analysis["total_size"] += entry.size
                
                # Track file types
                file_ext = os.path.splitext(entry.name)[1].lower()
                if file_ext:
                    analysis["file_types"][file_ext] = analysis["file_types"].get(file_ext, 0) + 1
                
                # Track large files
                if entry.size > 1024 * 1024:  # > 1MB
                    analysis["large_files"].append({
                        "path": rel_path,
                        "size": entry.size
                    })
            else:
                analysis["files_to_ignore"] += 1
        
        # Process children and track directory stats
        dir_file_count = 0
        for child in entry.children:
            child_rel_path = os.path.join(rel_path, child.name) if rel_path else child.name
            self._analyze_entry(child, parser, analysis, child_rel_path)
            
            if child.is_file():
                dir_file_count += 1
        
        # Store directory information
        if entry.is_folder() and dir_file_count > 0:
            analysis["directories"][rel_path if rel_path else "."] = {
                "file_count": dir_file_count,
                "total_files": dir_file_count  # Could be expanded to include subdirectories
            } 