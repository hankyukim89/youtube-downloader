#!/usr/bin/env python3
"""
YouTube Downloader - Entry Point
Double-click to launch the application
"""
import sys
import os
from pathlib import Path

# Ensure the package is in the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Run the application
from src.ui.app import main

if __name__ == "__main__":
    main()
