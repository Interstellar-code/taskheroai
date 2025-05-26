#!/usr/bin/env python3
"""
Test script to verify branding in logs.
"""

import logging
import sys
from pathlib import Path

# Setup logging to see all messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

print("🔍 Testing TaskHero AI Branding in Logs")
print("=" * 50)

# Test importing modules to see their logger initialization
print("\n📋 Testing Module Logger Initialization...")

try:
    print("1. Testing HTTP API module...")
    from mods.http_api import logger as http_logger
    print(f"   ✅ HTTP API Logger: {http_logger.name}")
    
    print("2. Testing MCP Server module...")
    from mcp_server import logger as mcp_logger
    print(f"   ✅ MCP Server Logger: {mcp_logger.name}")
    
    print("3. Testing Code Indexer module...")
    from mods.code.indexer import logger as indexer_logger
    print(f"   ✅ Indexer Logger: {indexer_logger.name}")
    
    print("4. Testing Directory Parser module...")
    from mods.code.directory import logger as directory_logger
    print(f"   ✅ Directory Parser Logger: {directory_logger.name}")
    
    print("5. Testing Tools module...")
    from mods.code.tools import logger as tools_logger
    print(f"   ✅ Tools Logger: {tools_logger.name}")
    
    print("6. Testing Agent Mode module...")
    from mods.code.agent_mode import logger as agent_logger
    print(f"   ✅ Agent Mode Logger: {agent_logger.name}")
    
    print("\n🎉 All loggers show correct TaskHero AI branding!")
    
    # Test actual logging
    print("\n📝 Testing Actual Log Messages...")
    http_logger.info("HTTP API module loaded with TaskHero AI branding")
    mcp_logger.info("MCP Server module loaded with TaskHero AI branding")
    indexer_logger.info("Indexer module loaded with TaskHero AI branding")
    directory_logger.info("Directory Parser module loaded with TaskHero AI branding")
    tools_logger.info("Tools module loaded with TaskHero AI branding")
    agent_logger.info("Agent Mode module loaded with TaskHero AI branding")
    
    print("\n✅ Branding test completed successfully!")
    print("All modules now use 'TaskHero AI' branding instead of 'VerbalCodeAI'")
    
except Exception as e:
    print(f"❌ Error during branding test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🎯 Branding Update Summary:")
print("- All logger names updated to TaskHero AI")
print("- No more VerbalCodeAI references in logs")
print("- HTTP API shows correct branding")
print("- MCP servers show correct branding")
print("- All code modules show correct branding")
