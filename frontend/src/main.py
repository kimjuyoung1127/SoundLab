import sys
import os

# Add project root to sys.path to allow 'src' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.layout import render_app

if __name__ == "__main__":
    render_app()
