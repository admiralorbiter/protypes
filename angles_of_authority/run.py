#!/usr/bin/env python3
"""
Run script for Angles of Authority
Sets up environment and starts the game
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pygame
        print(f"✓ Pygame {pygame.version.ver} found")
    except ImportError:
        print("✗ Pygame not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame>=2.5.0"])
        print("✓ Pygame installed")
    
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__} found")
    except ImportError:
        print("✗ NumPy not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.24.0"])
        print("✓ NumPy installed")

def main():
    """Main run function"""
    print("Angles of Authority - Starting...")
    
    # Check dependencies
    check_dependencies()
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run main
    try:
        from main import main as game_main
        game_main()
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
