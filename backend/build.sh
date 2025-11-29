#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# FFmpeg is pre-installed on Render
echo "Build completed successfully!"
