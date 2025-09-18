#!/bin/bash

# Marketing KPIs Analytics Dashboard - Run Script
# This script helps you run the application with proper setup

echo "🚀 Starting Marketing KPIs Analytics Dashboard..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env 2>/dev/null || echo "Please create .env file manually"
fi

# Run the application
echo "🚀 Starting Streamlit application..."
echo "Open your browser to http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py

