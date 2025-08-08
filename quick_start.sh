#!/bin/bash

# ADGM Corporate Agent Pro - Quick Start Script
# This script sets up and runs the ADGM Corporate Agent application

echo "⚖️  ADGM Corporate Agent Pro - Quick Start"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.11+ is required but not installed"
        echo "Please install Python 3.11+ from https://python.org/downloads/"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip found"
    else
        print_error "pip is required but not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Check API key
check_api_key() {
    print_status "Checking API key configuration..."
    if [ -z "$GEMINI_API_KEY" ]; then
        print_warning "GEMINI_API_KEY environment variable not set"
        echo "Please set your Gemini API key:"
        echo "export GEMINI_API_KEY='your-api-key-here'"
        echo ""
        echo "Or create a .env file with:"
        echo "echo 'GEMINI_API_KEY=your-api-key-here' > .env"
        echo ""
        read -p "Do you want to continue without API key? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "API key found"
    fi
}

# Run the application
run_app() {
    print_status "Starting ADGM Corporate Agent Pro..."
    echo ""
    echo "🌐 Application will be available at: http://localhost:5000"
    echo "📺 Demo Video: https://youtu.be/YU6zeUOyqEI"
    echo ""
    echo "Press Ctrl+C to stop the application"
    echo ""
    
    streamlit run app.py --server.port 5000 --server.address 0.0.0.0
}

# Main execution
main() {
    echo ""
    print_status "Starting ADGM Corporate Agent Pro setup..."
    echo ""
    
    # Run checks and setup
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    check_api_key
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    
    # Run the application
    run_app
}

# Run main function
main "$@"
