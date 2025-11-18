#!/usr/bin/env python3
"""
OSRS Bot Management System

This is the main entry point for the OSRS bot management system.
It starts the web UI server that allows you to manage and control bots.

Usage:
    python main.py

The web interface will be available at:
    http://localhost:8010
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and start the UI server
from ui.main import app, initialize_app

def main():
    """Start the OSRS Bot Management UI"""
    print("=" * 60)
    print("🤖 OSRS Bot Management System")
    print("=" * 60)
    print()
    print("Initializing bot discovery and UI server...")
    
    # Initialize the application (discover bots, etc.)
    initialize_app()
    
    print()
    print("🚀 Starting web server...")
    print("📱 Web interface available at: http://localhost:8010")
    print("📋 Dashboard: http://localhost:8010")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Flask development server
        app.run(
            host='0.0.0.0', 
            port=8010, 
            debug=False,  # Set to False for production-like behavior
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down bot management system...")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())