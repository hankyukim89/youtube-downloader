#!/bin/bash
# Move to the script's directory
cd "$(dirname "$0")"

echo "----------------------------------------"
echo "   YouTube Downloader - Mac Launcher    "
echo "----------------------------------------"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install it from https://python.org"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/Update requirements
echo "Checking requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the app
echo "Launching YouTube Downloader..."
python3 run.py

# Deactivate venv on exit
deactivate
echo "----------------------------------------"
echo "   Application closed.                 "
echo "----------------------------------------"
