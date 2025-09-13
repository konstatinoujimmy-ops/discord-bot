"""
Entry point for Bot-Hosting.net
Simple starter that imports and runs the main bot
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main bot
from main import main

if __name__ == "__main__":
    main()