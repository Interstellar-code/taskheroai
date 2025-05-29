"""Migration script for upgrading existing embeddings to enhanced metadata format.

This module provides functionality to migrate existing embedding files from
version 1 (basic metadata) to version 2 (enhanced metadata) while maintaining
backward compatibility.
"""

import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .indexer import FileIndexer

logger = logging.getLogger("TaskHeroAI.Migration")


class EmbeddingMigration:
    """Handles migration of existing embeddings to enhanced metadata format."""

    def __init__(self, embeddings_dir: Path, backup_dir: Optional[Path] = None):
        """Initialize the migration handler.

        Args:
            embeddings_dir: Directory containing embedding files to migrate
            backup_dir: Directory to store backups (defaults to embeddings_dir/backup)
        """
        self.embeddings_dir = Path(embeddings_dir)
        self.backup_dir = backup_dir or (self.embeddings_dir / "backup")
        self.migration_log = []

    def migrate_embeddings(self, project_root: str) -> Dict[str, Any]:
        """Migrate existing embeddings to enhanced format.

        Args:
            project_root: Root directory of the project for re-analysis

        Returns:
            Dictionary with migration results and statistics
        """
        results = {
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
            'backup_created': False,
            'migration_log': [],
            'start_time': time.time()
        }

        logger.info("Starting embedding migration to enhanced metadata format")

        try:
            # Create backup
            if self._create_backup():
                results['backup_created'] = True
                logger.info(f"Backup created at {self.backup_dir}")
            else:
                logger.warning("Failed to create backup - proceeding with migration")

            # Initialize indexer for re-analysis
            indexer = FileIndexer(project_root)

            # Process each embedding file
            embedding_files = list(self.embeddings_dir.glob("*.json"))
            logger.info(f"Found {len(embedding_files)} embedding files to migrate")

            for embedding_file in embedding_files:
                try:
                    if self._migrate_single_file(embedding_file, indexer):
                        results['migrated'] += 1
                        self.migration_log.append(f"✅ Migrated: {embedding_file.name}")
                    else:
                        results['skipped'] += 1
                        self.migration_log.append(f"⏭️ Skipped: {embedding_file.name}")

                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"❌ Error migrating {embedding_file.name}: {e}"
                    logger.error(error_msg)
                    self.migration_log.append(error_msg)

            results['end_time'] = time.time()
            results['duration'] = results['end_time'] - results['start_time']
            results['migration_log'] = self.migration_log

            # Save migration report
            self._save_migration_report(results)

            logger.info(f"Migration completed: {results['migrated']} migrated, "
                       f"{results['skipped']} skipped, {results['errors']} errors")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            results['migration_error'] = str(e)

        return results

    def _create_backup(self) -> bool:
        """Create backup of existing embeddings directory.

        Returns:
            True if backup was created successfully
        """
        try:
            if not self.embeddings_dir.exists():
                logger.warning("Embeddings directory does not exist - no backup needed")
                return True

            # Create backup directory with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"embeddings_backup_{timestamp}"

            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy all embedding files
            for file_path in self.embeddings_dir.glob("*.json"):
                shutil.copy2(file_path, backup_path / file_path.name)

            logger.info(f"Created backup with {len(list(backup_path.glob('*.json')))} files")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def _migrate_single_file(self, embedding_file: Path, indexer: FileIndexer) -> bool:
        """Migrate a single embedding file to enhanced format.

        Args:
            embedding_file: Path to the embedding file to migrate
            indexer: FileIndexer instance for re-analysis

        Returns:
            True if migration was successful
        """
        try:
            # Load existing embedding data
            with open(embedding_file, 'r', encoding='utf-8') as f:
                embedding_data = json.load(f)

            # Check if already migrated
            metadata = embedding_data.get('metadata', {})
            if metadata.get('enhanced_metadata', False):
                logger.debug(f"File {embedding_file.name} already has enhanced metadata")
                return False

            # Get file path from embedding data
            file_path = embedding_data.get('path')
            if not file_path:
                logger.warning(f"No file path found in {embedding_file.name}")
                return False

            # Check if source file still exists
            source_file = Path(indexer.root_path) / file_path
            if not source_file.exists():
                logger.warning(f"Source file no longer exists: {file_path}")
                # Keep existing data but mark as migrated
                metadata['enhanced_metadata'] = True
                metadata['version'] = 2
                metadata['migration_note'] = 'Source file not found - kept existing data'
                embedding_data['metadata'] = metadata

                with open(embedding_file, 'w', encoding='utf-8') as f:
                    json.dump(embedding_data, f, indent=2)
                return True

            # Re-analyze file with enhanced metadata
            try:
                with open(source_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                enhanced_info, code_analysis, relationships = indexer._analyze_enhanced_metadata(
                    str(source_file), content
                )

                # Update metadata with enhanced information
                metadata.update({
                    'version': 2,
                    'enhanced_metadata': True,
                    'migration_timestamp': time.time(),
                    'enhanced_info': indexer._serialize_enhanced_info(enhanced_info) if enhanced_info else None,
                    'code_analysis': indexer._serialize_code_analysis(code_analysis) if code_analysis else None,
                    'relationships': indexer._serialize_relationships(relationships) if relationships else None
                })

                embedding_data['metadata'] = metadata

                # Save updated embedding data
                with open(embedding_file, 'w', encoding='utf-8') as f:
                    json.dump(embedding_data, f, indent=2)

                logger.debug(f"Successfully migrated {embedding_file.name}")
                return True

            except Exception as e:
                logger.error(f"Failed to re-analyze {file_path}: {e}")
                # Fallback: mark as migrated without enhanced data
                metadata['enhanced_metadata'] = True
                metadata['version'] = 2
                metadata['migration_error'] = str(e)
                embedding_data['metadata'] = metadata

                with open(embedding_file, 'w', encoding='utf-8') as f:
                    json.dump(embedding_data, f, indent=2)
                return True

        except Exception as e:
            logger.error(f"Failed to migrate {embedding_file.name}: {e}")
            return False

    def _save_migration_report(self, results: Dict[str, Any]) -> None:
        """Save migration report to file.

        Args:
            results: Migration results dictionary
        """
        try:
            report_path = self.embeddings_dir / "migration_report.json"

            report = {
                'migration_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'results': results,
                'migration_log': self.migration_log
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Migration report saved to {report_path}")

        except Exception as e:
            logger.error(f"Failed to save migration report: {e}")

    def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful.

        Returns:
            Dictionary with verification results
        """
        verification_results = {
            'total_files': 0,
            'enhanced_files': 0,
            'legacy_files': 0,
            'corrupted_files': 0,
            'verification_errors': []
        }

        try:
            embedding_files = list(self.embeddings_dir.glob("*.json"))
            verification_results['total_files'] = len(embedding_files)

            for embedding_file in embedding_files:
                try:
                    with open(embedding_file, 'r', encoding='utf-8') as f:
                        embedding_data = json.load(f)

                    metadata = embedding_data.get('metadata', {})
                    if metadata.get('enhanced_metadata', False):
                        verification_results['enhanced_files'] += 1
                    else:
                        verification_results['legacy_files'] += 1

                except json.JSONDecodeError:
                    verification_results['corrupted_files'] += 1
                    verification_results['verification_errors'].append(
                        f"Corrupted JSON: {embedding_file.name}"
                    )
                except Exception as e:
                    verification_results['verification_errors'].append(
                        f"Error reading {embedding_file.name}: {e}"
                    )

            logger.info(f"Migration verification: {verification_results['enhanced_files']}"
                       f"/{verification_results['total_files']} files have enhanced metadata")

        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            verification_results['verification_error'] = str(e)

        return verification_results


def run_migration(project_root: str, embeddings_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run migration for a project.

    Args:
        project_root: Root directory of the project
        embeddings_dir: Directory containing embeddings (defaults to project_root/.index/embeddings)

    Returns:
        Migration results dictionary
    """
    if embeddings_dir is None:
        embeddings_dir = os.path.join(project_root, ".index", "embeddings")

    migration = EmbeddingMigration(Path(embeddings_dir))
    return migration.migrate_embeddings(project_root)
