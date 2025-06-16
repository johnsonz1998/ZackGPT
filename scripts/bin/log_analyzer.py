#!/usr/bin/env python3
"""
ZackGPT Log Analyzer - MongoDB-based analytics
Symlink to the main tools version
"""
import sys
import os

# Import from the main tools directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from log_analyzer import main

if __name__ == "__main__":
    main() 