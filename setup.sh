#!/bin/bash

echo "Setting up ParalonCloud Image Tool..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your PARALONCLOUD_API_KEY"
    echo "Example:"
    echo "  PARALONCLOUD_API_KEY=your_api_key_here"
    echo ""
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the backend server, run:"
echo "  source venv/bin/activate"
echo "  python3 -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "To start the frontend (in another terminal), run:"
echo "  cd frontend"
echo "  npm install  # if you haven't already"
echo "  npm start"
