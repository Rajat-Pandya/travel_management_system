"""
Main entry point for Travel Management System.
Integrates all modules and runs the application.
"""

import sys
import os

from tkinter import Tk

# Import modules
from database import init_database
from ui import ModernTravelApp


def run_app():
    """Initialize and run the Travel Management System application."""
    # Initialize database
    init_database()
    
    # Create main window
    root = Tk()
    
    # Create and run app
    app = ModernTravelApp(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    run_app()
