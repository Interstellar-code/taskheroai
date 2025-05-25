#!/usr/bin/env python3
"""
Test script for the Smart Indexing System.

This script demonstrates how the smart indexing system works and
shows the improvements over the traditional indexing approach.
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.code.smart_indexer import SmartIndexer
from colorama import Fore, Style, init

# Initialize colorama for Windows
init(autoreset=True)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{title.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{Fore.CYAN}📋 {title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")


def demonstrate_smart_indexing():
    """Demonstrate the smart indexing system."""
    
    print_header("TaskHero AI - Smart Indexing System Demo")
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"{Fore.CYAN}Working directory: {current_dir}{Style.RESET_ALL}")
    
    # Initialize smart indexer
    print_section("1. Initializing Smart Indexer")
    smart_indexer = SmartIndexer(current_dir)
    print(f"{Fore.GREEN}✅ Smart indexer initialized for project: {smart_indexer.project_name}{Style.RESET_ALL}")
    
    # Check current status
    print_section("2. Checking Current Indexing Status")
    status = smart_indexer.get_indexing_status()
    
    print(f"{Fore.CYAN}Overall Status: {status['overall_status'].upper()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Message: {status['message']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Index exists: {status['index_exists']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Metadata files: {status['metadata_files']}{Style.RESET_ALL}")
    
    # Show analysis details
    analysis = status['analysis']
    print(f"\n{Fore.YELLOW}📊 Analysis Details:{Style.RESET_ALL}")
    print(f"  • Recent indexing: {analysis['has_recent_indexing']}")
    print(f"  • Indexing complete: {analysis['indexing_complete']}")
    print(f"  • Log files found: {analysis['log_files_found']}")
    
    if analysis['last_indexing_time']:
        time_str = analysis['last_indexing_time'].strftime("%Y-%m-%d %H:%M:%S")
        print(f"  • Last indexing: {time_str}")
    
    # Show recommendations
    if analysis['recommendations']:
        print(f"\n{Fore.YELLOW}💡 Recommendations:{Style.RESET_ALL}")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
    
    # Check recent logs
    print_section("3. Analyzing Recent Logs")
    recent_logs = smart_indexer.get_recent_indexing_logs()
    
    if recent_logs:
        print(f"{Fore.GREEN}Found {len(recent_logs)} recent log files:{Style.RESET_ALL}")
        for i, log in enumerate(recent_logs[:5], 1):  # Show first 5
            log_name = os.path.basename(log['file'])
            time_str = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            size_kb = log['size'] / 1024
            print(f"  {i}. {log_name} ({time_str}, {size_kb:.1f}KB)")
    else:
        print(f"{Fore.YELLOW}No recent log files found.{Style.RESET_ALL}")
    
    # Demonstrate smart file detection
    print_section("4. Smart File Detection")
    files_to_index, analysis_info = smart_indexer.get_files_needing_indexing()
    
    scan_type = analysis_info.get('scan_type', 'unknown')
    print(f"{Fore.CYAN}Scan type: {scan_type}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Files needing indexing: {len(files_to_index)}{Style.RESET_ALL}")
    
    if files_to_index:
        print(f"\n{Fore.YELLOW}Sample files to index:{Style.RESET_ALL}")
        for file_path in files_to_index[:10]:  # Show first 10
            rel_path = os.path.relpath(file_path, current_dir)
            print(f"  • {rel_path}")
        
        if len(files_to_index) > 10:
            print(f"  ... and {len(files_to_index) - 10} more files")
    else:
        print(f"{Fore.GREEN}✅ All files are up to date!{Style.RESET_ALL}")
    
    # Ask user if they want to perform indexing
    print_section("5. Smart Indexing Decision")
    
    if files_to_index:
        print(f"{Fore.YELLOW}Would you like to perform smart indexing?{Style.RESET_ALL}")
        print(f"  1. Yes - Perform smart indexing")
        print(f"  2. Force - Force complete re-indexing")
        print(f"  3. No - Skip indexing")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Select option (1-3): {Style.RESET_ALL}").strip()
                
                if choice == '1':
                    perform_smart_indexing(smart_indexer, force=False)
                    break
                elif choice == '2':
                    perform_smart_indexing(smart_indexer, force=True)
                    break
                elif choice == '3':
                    print(f"{Fore.CYAN}Indexing skipped.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1, 2, or 3.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Indexing cancelled.{Style.RESET_ALL}")
                break
    else:
        print(f"{Fore.GREEN}✅ No indexing needed - all files are up to date!{Style.RESET_ALL}")
    
    # Show final status
    print_section("6. Final Status")
    final_status = smart_indexer.get_indexing_status()
    print(f"{Fore.GREEN}Final status: {final_status['overall_status'].upper()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Total indexed files: {final_status['metadata_files']}{Style.RESET_ALL}")
    
    # Cleanup demo
    print_section("7. Log Cleanup Demo")
    deleted_count = smart_indexer.cleanup_old_logs(keep_days=7)
    if deleted_count > 0:
        print(f"{Fore.CYAN}🗑️  Cleaned up {deleted_count} old log files{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}No old log files to clean up{Style.RESET_ALL}")
    
    print_header("Smart Indexing Demo Complete!")


def perform_smart_indexing(smart_indexer: SmartIndexer, force: bool = False):
    """Perform smart indexing and show results."""
    
    action = "Force re-indexing" if force else "Smart indexing"
    print(f"\n{Fore.GREEN}⚡ Performing {action.lower()}...{Style.RESET_ALL}")
    
    start_time = time.time()
    result = smart_indexer.smart_index(force_reindex=force)
    
    print(f"\n{Fore.CYAN}📊 Indexing Results:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*30}{Style.RESET_ALL}")
    
    if result['status'] == 'no_action_needed':
        print(f"{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Analysis time: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
    elif result['status'] == 'completed':
        print(f"{Fore.GREEN}🎉 {action} completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Files indexed: {result['files_indexed']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Files processed: {result['files_to_process']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Processing time: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
        
        if 'log_file' in result:
            log_name = os.path.basename(result['log_file'])
            print(f"{Fore.CYAN}📄 Log file: {log_name}{Style.RESET_ALL}")
        
        # Show scan type
        scan_type = result['analysis'].get('scan_type', 'unknown')
        print(f"{Fore.CYAN}🔍 Scan type: {scan_type}{Style.RESET_ALL}")
        
        # Calculate performance metrics
        if result['files_indexed'] > 0:
            rate = result['files_indexed'] / result['processing_time']
            print(f"{Fore.CYAN}⚡ Processing rate: {rate:.1f} files/second{Style.RESET_ALL}")
            
    elif result['status'] == 'failed':
        print(f"{Fore.RED}❌ {action} failed: {result['error']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Time before failure: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")


def main():
    """Main function."""
    try:
        demonstrate_smart_indexing()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Demo interrupted. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Demo error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 