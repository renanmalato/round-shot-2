#!/bin/bash
# Screenshot Rounder Launcher
# Automatically activates virtual environment and runs the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run the application
cd "$SCRIPT_DIR"
source venv/bin/activate

# Pass all arguments to the Python script
python3 screenshot_rounder.py "$@"