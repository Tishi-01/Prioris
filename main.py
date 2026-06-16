"""
Prioris - Task Manager
======================
An Eisenhower Matrix-based task manager with WiFi-aware
and weather-aware suggested tasks.

Run this file to start the application.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import PriorisApp


def main():
    app = PriorisApp()
    app.run()


if __name__ == "__main__":
    main()
