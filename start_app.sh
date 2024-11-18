#!/bin/bash

# Navigate to the project directory
cd ~/Desktop/print || exit

# Activate the virtual environment
source venv/bin/activate

# Install dependencies (optional, runs every time)
pip install -r requirements.txt

# Navigate to the application folder
cd brochureapp || exit

# Start the Gunicorn server
gunicorn -w 2 -b 0.0.0.0:8000 app:app

