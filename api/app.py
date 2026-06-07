# api/app.py
import sys
from pathlib import Path

# Add the parent directory to the Python path so imports work
file_path = Path(__file__).resolve()
sys.path.append(str(file_path.parent.parent))

from app import create_app

# Create the app instance for Vercel
app = create_app()

# This is the handler that Vercel will use
application = app