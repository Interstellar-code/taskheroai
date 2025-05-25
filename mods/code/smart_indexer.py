"""
Smart Indexing System for TaskHero AI.

This module provides intelligent indexing that uses log files to determine
if files have been recently indexed, avoiding unnecessary re-scanning.
"""

import os
import json
import time
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

from .indexer import FileIndexer
from .indexing_logger import IndexingLogger

logger = logging.getLogger("VerbalCodeAI.SmartIndexer")


class SmartIndexer:
    """
    Smart indexing system that uses log files to optimize indexing decisions.
    
    Features:
    - Checks recent indexing logs to avoid unnecessary scans
    - Tracks file modification times from logs
    - Provides intelligent indexing recommendations
    - Supports incremental indexing based on log analysis
    """
    
    def __init__(self, root_path: str, logs_dir: str = "logs", cache_duration_hours: int = 24):
        """
        Initialize the smart indexer.
        
        Args:
            root_path: Root directory to index
            logs_dir: Directory containing indexing logs
            cache_duration_hours: How long to consider logs valid (default: 24 hours)
        """
        self.root_path = os.path.abspath(root_path)
        self.logs_dir = logs_dir
        self.cache_duration_hours = cache_duration_hours
        self.project_name = os.path.basename(self.root_path)
        
        # Ensure logs directory exists
        os.makedirs(logs_dir, exist_ok=True)
        
        # Initialize indexer (will be created when needed)
        self._indexer: Optional[FileIndexer] = None
        
        # Cache for log analysis
        self._log_cache: Dict[str, Any] = {}
        self._last_log_scan: Optional[datetime] = None
        
    @property
    def indexer(self) -> FileIndexer:
        """Get or create the FileIndexer instance."""
        if self._indexer is None:
            self._indexer = FileIndexer(self.root_path)
        return self._indexer
    
    def get_recent_indexing_logs(self) -> List[Dict[str, Any]]:
        """
        Get recent indexing logs within the cache duration.
        
        Returns:
            List of log metadata sorted by timestamp (newest first)
        """
        cutoff_time = datetime.now() - timedelta(hours=self.cache_duration_hours)
        
        # Look for indexing log files
        log_pattern = os.path.join(self.logs_dir, f"indexing_{self.project_name}_*.log")
        json_pattern = os.path.join(self.logs_dir, f"indexing_{self.project_name}_*.json")
        
        logs = []
        
        # Check text logs
        for log_file in glob.glob(log_pattern):
            try:
                stat = os.stat(log_file)
                file_time = datetime.fromtimestamp(stat.st_mtime)
                
                if file_time > cutoff_time:
                    logs.append({
                        'file': log_file,
                        'type': 'text',
                        'timestamp': file_time,
                        'size': stat.st_size
                    })
            except Exception as e:
                logger.warning(f"Error reading log file {log_file}: {e}")
        
        # Check JSON logs
        for json_file in glob.glob(json_pattern):
            try:
                stat = os.stat(json_file)
                file_time = datetime.fromtimestamp(stat.st_mtime)
                
                if file_time > cutoff_time:
                    # Try to read JSON content for more details
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            logs.append({
                                'file': json_file,
                                'type': 'json',
                                'timestamp': file_time,
                                'size': stat.st_size,
                                'data': data
                            })
                    except Exception as e:
                        logger.warning(f"Error reading JSON content from {json_file}: {e}")
                        logs.append({
                            'file': json_file,
                            'type': 'json',
                            'timestamp': file_time,
                            'size': stat.st_size
                        })
            except Exception as e:
                logger.warning(f"Error reading JSON log file {json_file}: {e}")
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs
    
    def analyze_recent_indexing(self) -> Dict[str, Any]:
        """
        Analyze recent indexing logs to determine current state.
        
        Returns:
            Dictionary with analysis results including:
            - has_recent_indexing: bool
            - last_indexing_time: datetime or None
            - files_indexed: int
            - indexing_complete: bool
            - recommendations: List[str]
        """
        recent_logs = self.get_recent_indexing_logs()
        
        analysis = {
            'has_recent_indexing': False,
            'last_indexing_time': None,
            'files_indexed': 0,
            'indexing_complete': False,
            'recommendations': [],
            'log_files_found': len(recent_logs)
        }
        
        if not recent_logs:
            analysis['recommendations'].append("No recent indexing logs found - full indexing recommended")
            return analysis
        
        # Analyze the most recent log
        latest_log = recent_logs[0]
        analysis['has_recent_indexing'] = True
        analysis['last_indexing_time'] = latest_log['timestamp']
        
        # If we have JSON data, extract detailed information
        if latest_log['type'] == 'json' and 'data' in latest_log:
            data = latest_log['data']
            
            # Check if indexing was completed successfully
            if data.get('status') == 'completed':
                analysis['indexing_complete'] = True
                analysis['files_indexed'] = data.get('statistics', {}).get('files_indexed', 0)
                
                # Check how recent the indexing was
                hours_ago = (datetime.now() - latest_log['timestamp']).total_seconds() / 3600
                
                if hours_ago < 1:
                    analysis['recommendations'].append("Recent indexing completed less than 1 hour ago - no action needed")
                elif hours_ago < 6:
                    analysis['recommendations'].append("Recent indexing completed - check for new/modified files only")
                else:
                    analysis['recommendations'].append("Indexing completed several hours ago - consider incremental update")
            else:
                analysis['recommendations'].append("Previous indexing may not have completed successfully - consider re-indexing")
        # If we have JSON file but no data loaded, try to read it directly
        elif latest_log['type'] == 'json':
            try:
                with open(latest_log['file'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if data.get('status') == 'completed':
                    analysis['indexing_complete'] = True
                    analysis['files_indexed'] = data.get('statistics', {}).get('files_indexed', 0)
                    
                    # Check how recent the indexing was
                    hours_ago = (datetime.now() - latest_log['timestamp']).total_seconds() / 3600
                    
                    if hours_ago < 1:
                        analysis['recommendations'].append("Recent indexing completed less than 1 hour ago - no action needed")
                    elif hours_ago < 6:
                        analysis['recommendations'].append("Recent indexing completed - check for new/modified files only")
                    else:
                        analysis['recommendations'].append("Indexing completed several hours ago - consider incremental update")
                else:
                    analysis['recommendations'].append("Previous indexing may not have completed successfully - consider re-indexing")
            except Exception as e:
                logger.warning(f"Error reading JSON log file: {e}")
                analysis['recommendations'].append("Could not read indexing log - consider re-indexing")
        else:
            # Analyze text log for completion indicators
            try:
                with open(latest_log['file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if "Indexing Complete" in content or "indexing process completed" in content:
                        analysis['indexing_complete'] = True
                        analysis['recommendations'].append("Recent indexing appears complete - check for new files only")
                    else:
                        analysis['recommendations'].append("Recent indexing may be incomplete - consider re-indexing")
            except Exception as e:
                logger.warning(f"Error reading log content: {e}")
                analysis['recommendations'].append("Could not verify indexing completion - consider re-indexing")
        
        return analysis
    
    def get_files_needing_indexing(self, force_scan: bool = False) -> Tuple[List[str], Dict[str, Any]]:
        """
        Get list of files that need indexing based on smart analysis.
        
        Args:
            force_scan: If True, force a full directory scan regardless of logs
            
        Returns:
            Tuple of (files_to_index, analysis_info)
        """
        analysis = self.analyze_recent_indexing()
        
        if force_scan:
            logger.info("Force scan requested - performing full directory scan")
            files_to_index = self.indexer._get_all_indexable_files()
            analysis['scan_type'] = 'full_forced'
            return files_to_index, analysis
        
        # Check if we have existing index data (even without recent logs)
        index_dir = os.path.join(self.root_path, '.index')
        metadata_dir = os.path.join(index_dir, 'metadata')
        has_existing_index = os.path.exists(metadata_dir)
        
        if has_existing_index:
            try:
                metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith('.json')]
                metadata_count = len(metadata_files)
            except Exception:
                metadata_count = 0
        else:
            metadata_count = 0
        
        # If we have recent complete indexing, check for outdated files only
        if analysis['indexing_complete'] and analysis['has_recent_indexing']:
            hours_ago = (datetime.now() - analysis['last_indexing_time']).total_seconds() / 3600
            
            if hours_ago < 1:
                logger.info("Recent indexing completed less than 1 hour ago - checking for changes only")
                files_to_index = self.indexer.get_outdated_files()
                analysis['scan_type'] = 'incremental_recent'
            elif hours_ago < 6:
                logger.info("Recent indexing found - performing incremental check")
                files_to_index = self.indexer.get_outdated_files()
                analysis['scan_type'] = 'incremental_check'
            else:
                logger.info("Indexing is several hours old - performing full check")
                files_to_index = self.indexer.get_outdated_files()
                analysis['scan_type'] = 'full_check'
        elif has_existing_index and metadata_count > 0:
            # We have existing index data but no recent logs - check for outdated files
            logger.info(f"Existing index found with {metadata_count} files but no recent logs - checking for outdated files")
            files_to_index = self.indexer.get_outdated_files()
            analysis['scan_type'] = 'incremental_existing'
        else:
            logger.info("No existing index found - performing full scan")
            files_to_index = self.indexer._get_all_indexable_files()
            analysis['scan_type'] = 'full_new'
        
        return files_to_index, analysis
    
    def smart_index(self, force_reindex: bool = False, progress_callback=None) -> Dict[str, Any]:
        """
        Perform smart indexing based on log analysis.
        
        Args:
            force_reindex: If True, force complete re-indexing
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with indexing results
        """
        start_time = time.time()
        
        # Get files that need indexing
        files_to_index, analysis = self.get_files_needing_indexing(force_scan=force_reindex)
        
        if not files_to_index:
            return {
                'status': 'no_action_needed',
                'message': 'All files are up to date',
                'analysis': analysis,
                'processing_time': time.time() - start_time
            }
        
        # Create indexing logger
        indexing_logger = IndexingLogger(self.root_path, self.logs_dir)
        
        try:
            # Log the smart indexing decision
            indexing_logger._write_log(f"Smart indexing started - scan type: {analysis.get('scan_type', 'unknown')}", "INFO")
            indexing_logger._write_log(f"Files to process: {len(files_to_index)}", "INFO")
            
            # Perform the actual indexing
            if force_reindex:
                indexed_files = self.indexer.force_reindex_all()
            else:
                indexed_files = self.indexer.index_directory()
            
            # Finalize logging
            indexing_logger.finalize()
            
            return {
                'status': 'completed',
                'files_indexed': len(indexed_files),
                'files_to_process': len(files_to_index),
                'analysis': analysis,
                'processing_time': time.time() - start_time,
                'log_file': indexing_logger.log_file,
                'json_file': indexing_logger.json_file
            }
            
        except Exception as e:
            indexing_logger._write_log(f"Smart indexing failed: {str(e)}", "ERROR")
            indexing_logger.finalize()
            
            return {
                'status': 'failed',
                'error': str(e),
                'analysis': analysis,
                'processing_time': time.time() - start_time
            }
    
    def get_indexing_status(self) -> Dict[str, Any]:
        """
        Get current indexing status without performing any indexing.
        
        Returns:
            Dictionary with current status information
        """
        analysis = self.analyze_recent_indexing()
        
        # Check if index directory exists and has content
        index_dir = os.path.join(self.root_path, '.index')
        metadata_dir = os.path.join(index_dir, 'metadata')
        
        status = {
            'index_exists': os.path.exists(index_dir),
            'metadata_exists': os.path.exists(metadata_dir),
            'metadata_files': 0,
            'analysis': analysis
        }
        
        if status['metadata_exists']:
            try:
                metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith('.json')]
                status['metadata_files'] = len(metadata_files)
            except Exception as e:
                logger.warning(f"Error counting metadata files: {e}")
        
        # Determine overall status
        if analysis['indexing_complete'] and status['metadata_files'] > 0:
            hours_ago = (datetime.now() - analysis['last_indexing_time']).total_seconds() / 3600
            if hours_ago < 1:
                status['overall_status'] = 'up_to_date'
                status['message'] = f"Index is up to date ({status['metadata_files']} files indexed)"
            elif hours_ago < 6:
                status['overall_status'] = 'recent'
                status['message'] = f"Index is recent ({status['metadata_files']} files, {hours_ago:.1f}h ago)"
            else:
                status['overall_status'] = 'outdated'
                status['message'] = f"Index may be outdated ({status['metadata_files']} files, {hours_ago:.1f}h ago)"
        elif status['metadata_files'] > 0:
            # Check if we can determine outdated files to give a better status
            try:
                outdated_count = len(self.indexer.get_outdated_files())
                if outdated_count == 0:
                    status['overall_status'] = 'up_to_date'
                    status['message'] = f"Index is up to date ({status['metadata_files']} files indexed, no recent logs)"
                elif outdated_count <= 5:
                    status['overall_status'] = 'mostly_current'
                    status['message'] = f"Index is mostly current ({status['metadata_files']} files indexed, {outdated_count} files need updating)"
                else:
                    status['overall_status'] = 'incomplete'
                    status['message'] = f"Index exists but may be incomplete ({status['metadata_files']} files indexed, {outdated_count} files need updating)"
            except Exception as e:
                logger.warning(f"Error checking outdated files for status: {e}")
                status['overall_status'] = 'incomplete'
                status['message'] = f"Index exists but status unclear ({status['metadata_files']} files)"
        else:
            status['overall_status'] = 'missing'
            status['message'] = "No index found - full indexing needed"
        
        return status
    
    def cleanup_old_logs(self, keep_days: int = 7) -> int:
        """
        Clean up old indexing log files.
        
        Args:
            keep_days: Number of days of logs to keep
            
        Returns:
            Number of files deleted
        """
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        # Clean up text logs
        log_pattern = os.path.join(self.logs_dir, f"indexing_{self.project_name}_*.log")
        for log_file in glob.glob(log_pattern):
            try:
                stat = os.stat(log_file)
                file_time = datetime.fromtimestamp(stat.st_mtime)
                
                if file_time < cutoff_time:
                    os.remove(log_file)
                    deleted_count += 1
                    logger.info(f"Deleted old log file: {log_file}")
            except Exception as e:
                logger.warning(f"Error deleting log file {log_file}: {e}")
        
        # Clean up JSON logs
        json_pattern = os.path.join(self.logs_dir, f"indexing_{self.project_name}_*.json")
        for json_file in glob.glob(json_pattern):
            try:
                stat = os.stat(json_file)
                file_time = datetime.fromtimestamp(stat.st_mtime)
                
                if file_time < cutoff_time:
                    os.remove(json_file)
                    deleted_count += 1
                    logger.info(f"Deleted old JSON log file: {json_file}")
            except Exception as e:
                logger.warning(f"Error deleting JSON log file {json_file}: {e}")
        
        return deleted_count 