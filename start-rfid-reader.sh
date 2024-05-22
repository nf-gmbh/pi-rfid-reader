#!/bin/bash

# Define the directory
APP_DIR="/opt/pi-rfid-reader"

# Navigate to the application directory
cd "$APP_DIR" || exit

# Check if .venv directory exists, if not create it
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Navigate to the source folder (assuming source folder is within APP_DIR)
cd src || exit

# Run the application
python app_reader.py --log /var/log/pi-rfid-reader/app.log --port 8080 --timeout 5
