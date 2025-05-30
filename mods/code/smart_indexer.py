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
                    analysis['recommendations'].append("Recent indexing completed less than 1 hour ago - checking for any new files")
                elif hours_ago < 6:
                    analysis['recommendations'].append("Recent indexing completed - checking for new/modified files")
                else:
                    analysis['recommendations'].append("Indexing completed several hours ago - checking for incremental updates")
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

        # If we have recent complete indexing, check for missing and outdated files
        if analysis['indexing_complete'] and analysis['has_recent_indexing']:
            hours_ago = (datetime.now() - analysis['last_indexing_time']).total_seconds() / 3600

            if hours_ago < 1:
                logger.info("Recent indexing completed less than 1 hour ago - checking for changes only")
                files_to_index = self._get_files_needing_update()
                analysis['scan_type'] = 'incremental_recent'
            elif hours_ago < 6:
                logger.info("Recent indexing found - performing incremental check")
                files_to_index = self._get_files_needing_update()
                analysis['scan_type'] = 'incremental_check'
            else:
                logger.info("Indexing is several hours old - performing full check")
                files_to_index = self._get_files_needing_update()
                analysis['scan_type'] = 'full_check'
        elif has_existing_index and metadata_count > 0:
            # We have existing index data but no recent logs - check for missing and outdated files
            logger.info(f"Existing index found with {metadata_count} files but no recent logs - checking for missing and outdated files")
            files_to_index = self._get_files_needing_update()
            analysis['scan_type'] = 'incremental_existing'
        else:
            logger.info("No existing index found - performing full scan")
            files_to_index = self.indexer._get_all_indexable_files()
            analysis['scan_type'] = 'full_new'

        return files_to_index, analysis

    def _get_files_needing_update(self) -> List[str]:
        """
        Get list of files that need indexing (both missing and outdated).

        This method combines the logic from get_outdated_files() and is_index_complete()
        to find all files that need to be indexed or re-indexed. It also cleans up
        deleted files from the index.

        Returns:
            List of file paths that need indexing
        """
        try:
            # Get the complete index status which includes both missing and outdated files
            index_status = self.indexer.is_index_complete()

            # Clean up deleted files if any are found
            if index_status.get('deleted_count', 0) > 0:
                logger.info(f"Found {index_status['deleted_count']} deleted files in index - cleaning up")
                deleted_count = self.indexer.cleanup_deleted_files()
                logger.info(f"Cleaned up {deleted_count} deleted files from index")

                # Re-check index status after cleanup
                index_status = self.indexer.is_index_complete()

            # If index is complete after cleanup, no files need updating
            if index_status.get('complete', False):
                return []

            # Get all files that need updating (both missing and outdated)
            files_needing_update = []

            # Get outdated files (files that exist in index but are out of date)
            # Skip cleanup since we already did it above
            try:
                outdated_files = self.indexer.get_outdated_files(cleanup_deleted=False)
                files_needing_update.extend(outdated_files)
            except Exception as e:
                logger.warning(f"Error getting outdated files: {e}")

            # Get missing files by comparing all indexable files with what's already indexed
            try:
                all_indexable = self.indexer._get_all_indexable_files()
                indexed_files = set(self.indexer.metadata_cache.keys())

                # Normalize paths for comparison
                indexed_normalized = {os.path.normpath(p).lower() for p in indexed_files}

                for file_path in all_indexable:
                    file_normalized = os.path.normpath(file_path).lower()
                    if file_normalized not in indexed_normalized:
                        # This file is missing from the index
                        if file_path not in files_needing_update:
                            files_needing_update.append(file_path)

            except Exception as e:
                logger.warning(f"Error finding missing files: {e}")
                # Fallback to just outdated files if we can't determine missing files
                pass

            logger.info(f"Found {len(files_needing_update)} files needing indexing (missing + outdated)")
            return files_needing_update

        except Exception as e:
            logger.error(f"Error getting files needing update: {e}")
            # Fallback to get_outdated_files if there's an error
            try:
                return self.indexer.get_outdated_files()
            except Exception:
                return []

    def smart_index(self, force_reindex: bool = False, progress_callback=None) -> Dict[str, Any]:
        """
        Perform smart indexing based on log analysis.

        Args:
            force_reindex: If True, force complete re-indexing
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with indexing results
        """
        import time
        from colorama import Fore, Style

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
            # Enhanced visual feedback
            print(f"\n{Fore.CYAN}🚀 Step 4: Processing {len(files_to_index)} files...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

            # Show AI provider info
            try:
                from .indexer import _get_ai_provider_info
                ai_info = _get_ai_provider_info()
                print(f"{Fore.MAGENTA}🤖 AI Providers: {ai_info['description_full']}, {ai_info['embedding_full']}{Style.RESET_ALL}")
            except Exception:
                print(f"{Fore.MAGENTA}🤖 AI Providers: Initializing...{Style.RESET_ALL}")

            print(f"{Fore.YELLOW}📊 Processing Strategy: {analysis.get('scan_type', 'unknown').replace('_', ' ').title()}{Style.RESET_ALL}")
            print()

            # Log the smart indexing decision
            indexing_logger._write_log(f"Smart indexing started - scan type: {analysis.get('scan_type', 'unknown')}", "INFO")
            indexing_logger._write_log(f"Files to process: {len(files_to_index)}", "INFO")

            # Create enhanced progress callback
            indexed_count = 0
            failed_count = 0
            last_update_time = time.time()
            current_file = ""

            def enhanced_progress_callback(file_path=None):
                nonlocal indexed_count, failed_count, last_update_time, current_file

                if file_path:
                    current_file = os.path.basename(file_path)

                indexed_count += 1
                current_time = time.time()

                # Calculate metrics
                percent = int((indexed_count / len(files_to_index)) * 100)
                elapsed = current_time - start_time

                if elapsed > 0:
                    rate = indexed_count / elapsed
                    eta = (len(files_to_index) - indexed_count) / rate if rate > 0 else 0

                    # Update every file or every 1 second
                    if indexed_count % 1 == 0 or (current_time - last_update_time) >= 1.0:
                        # Show current file being processed
                        file_display = f" | {current_file[:25]}" if current_file else ""
                        print(f"\r{Fore.YELLOW}📈 Progress: {percent:3d}% ({indexed_count:3d}/{len(files_to_index)}) | Rate: {rate:4.1f} files/sec | ETA: {eta:3.0f}s{file_display}{Style.RESET_ALL}", end="", flush=True)
                        last_update_time = current_time
                else:
                    print(f"\r{Fore.YELLOW}📈 Progress: {percent:3d}% ({indexed_count:3d}/{len(files_to_index)}){Style.RESET_ALL}", end="", flush=True)

                # Log progress periodically
                if indexed_count % 25 == 0:
                    indexing_logger.log_progress(indexed_count, len(files_to_index))

                return False

            # Perform the actual indexing with enhanced progress
            if force_reindex:
                indexed_files = self.indexer.force_reindex_all(cancel_check_callback=enhanced_progress_callback)
            else:
                indexed_files = self.indexer.index_directory(cancel_check_callback=enhanced_progress_callback)

            # Clear progress line and show completion
            print(f"\r{' ' * 80}\r", end="")  # Clear the line
            print(f"{Fore.GREEN}✅ Indexing completed successfully!{Style.RESET_ALL}")

            # Show final statistics
            processing_time = time.time() - start_time
            rate = len(indexed_files) / processing_time if processing_time > 0 else 0

            print(f"{Fore.CYAN}📊 Final Statistics:{Style.RESET_ALL}")
            print(f"  • Files processed: {Fore.GREEN}{len(indexed_files)}{Style.RESET_ALL}")
            print(f"  • Processing time: {Fore.CYAN}{processing_time:.2f} seconds{Style.RESET_ALL}")
            print(f"  • Average rate: {Fore.CYAN}{rate:.1f} files/second{Style.RESET_ALL}")

            # Finalize logging
            indexing_logger.finalize()

            return {
                'status': 'completed',
                'files_indexed': len(indexed_files),
                'files_to_process': len(files_to_index),
                'analysis': analysis,
                'processing_time': processing_time,
                'log_file': indexing_logger.log_file,
                'json_file': indexing_logger.json_file
            }

        except Exception as e:
            print(f"\r{' ' * 80}\r", end="")  # Clear progress line
            print(f"{Fore.RED}❌ Smart indexing failed: {str(e)}{Style.RESET_ALL}")

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
            # Check if we can determine missing and outdated files to give a better status
            try:
                # Use the same logic as is_index_complete() to get accurate counts
                index_status = self.indexer.is_index_complete()
                missing_count = index_status.get('missing_count', 0)
                outdated_count = index_status.get('outdated_count', 0)
                deleted_count = index_status.get('deleted_count', 0)
                total_issues = missing_count + outdated_count + deleted_count

                if total_issues == 0:
                    status['overall_status'] = 'up_to_date'
                    status['message'] = f"Index is up to date ({status['metadata_files']} files indexed, no recent logs)"
                elif total_issues <= 5:
                    status['overall_status'] = 'mostly_current'
                    issue_parts = []
                    if missing_count > 0:
                        issue_parts.append(f"{missing_count} missing")
                    if outdated_count > 0:
                        issue_parts.append(f"{outdated_count} outdated")
                    if deleted_count > 0:
                        issue_parts.append(f"{deleted_count} deleted")

                    if issue_parts:
                        status['message'] = f"Index is mostly current ({status['metadata_files']} files indexed, {', '.join(issue_parts)})"
                    else:
                        status['message'] = f"Index is mostly current ({status['metadata_files']} files indexed)"
                else:
                    status['overall_status'] = 'incomplete'
                    issue_parts = []
                    if missing_count > 0:
                        issue_parts.append(f"{missing_count} missing")
                    if outdated_count > 0:
                        issue_parts.append(f"{outdated_count} outdated")
                    if deleted_count > 0:
                        issue_parts.append(f"{deleted_count} deleted")

                    if issue_parts:
                        status['message'] = f"Index is incomplete ({status['metadata_files']} files indexed, {', '.join(issue_parts)})"
                    else:
                        status['message'] = f"Index exists but may be incomplete ({status['metadata_files']} files indexed)"

                # Store the detailed counts for other methods to use
                status['missing_count'] = missing_count
                status['outdated_count'] = outdated_count
                status['deleted_count'] = deleted_count
                status['total_issues'] = total_issues

            except Exception as e:
                logger.warning(f"Error checking index completeness for status: {e}")
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