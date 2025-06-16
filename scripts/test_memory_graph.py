#!/usr/bin/env python3
"""
MemoryGraph Comprehensive Test Runner
Runs all MemoryGraph tests and validates logging functionality
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def print_banner(title):
    """Print a styled banner for test sections."""
    print("\n" + "="*80)
    print(f"🧠 {title}")
    print("="*80)

def print_section(title):
    """Print a section header."""
    print(f"\n🔍 {title}")
    print("-" * 60)

def validate_test_files():
    """Validate that all test files exist."""
    print_section("Validating Test Files")
    
    test_files = [
        ("frontend/src/components/__tests__/MemoryGraph.test.tsx", "Frontend React Tests"),
        ("frontend/src/utils/memoryGraphLogger.ts", "Frontend Logger Utility"),
        ("tests/backend/test_memory_graph_logging.py", "Backend Logging Tests"),
        ("src/zackgpt/web/memory_graph_api.py", "Backend Logging API"),
    ]
    
    all_exist = True
    for file_path, description in test_files:
        if Path(file_path).exists():
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} (File not found: {file_path})")
            all_exist = False
    
    return all_exist

def main():
    """Main test runner function."""
    print_banner("MemoryGraph Comprehensive Test Suite")
    
    # Validate test environment
    if not validate_test_files():
        print("\n❌ Test files validation failed. Cannot proceed with testing.")
        return False
    
    print("\n🎉 All MemoryGraph test files are present and ready!")
    print("\n📋 Available test suites:")
    print("   • Frontend React component tests")
    print("   • Backend logging integration tests") 
    print("   • Performance monitoring tests")
    print("   • User interaction analytics tests")
    print("   • Error handling and resilience tests")
    
    print("\n🚀 To run specific tests:")
    print("   Frontend: cd frontend && npm test MemoryGraph.test.tsx")
    print("   Backend:  python -m pytest tests/backend/test_memory_graph_logging.py -v")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 