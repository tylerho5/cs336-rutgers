#!/bin/bash

# Get the directory where the script is located (project_2)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/ec-frontend-nextjs"
CREDENTIALS_FILE="$SCRIPT_DIR/.env" # Credentials for project_2 itself
BACKEND_CREDENTIALS_FILE="$BACKEND_DIR/.env" # Credentials for backend

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CS336 Natural Language Database Interface ====${NC}"

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Function to check Node.js version
check_node_version() {
    if ! command_exists node; then
        echo -e "${RED}Error: Node.js is not installed. Please install Node.js version 18.18.0 or higher.${NC}"
        exit 1
    fi

    NODE_VERSION=$(node -v)
    REQUIRED_MAJOR=18
    REQUIRED_MINOR=18
    # Recommended is 20, but 18.18.0+ is the minimum stated.

    # Extract major and minor version numbers (e.g., v18.18.0 -> 18, 18)
    CURRENT_MAJOR=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d'.' -f1)
    CURRENT_MINOR=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d'.' -f2)

    if [ "$CURRENT_MAJOR" -lt "$REQUIRED_MAJOR" ] || ( [ "$CURRENT_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$CURRENT_MINOR" -lt "$REQUIRED_MINOR" ] ); then
        echo -e "${RED}Error: Your Node.js version is $NODE_VERSION. Version 18.18.0 or higher is required.${NC}"
        echo -e "${BLUE}Please upgrade Node.js. v20.0.0 or higher is recommended for Next.js.${NC}"
        exit 1
    else
        echo -e "${GREEN}Node.js version $NODE_VERSION is sufficient.${NC}"
    fi
}

# Check for Node.js and npm, and Node version
check_node_version
if ! command_exists npm; then
    echo -e "${RED}Error: npm is not installed. Please install npm.${NC}"
    exit 1
fi

# Check if credentials are set up
if [ ! -f "$CREDENTIALS_FILE" ] || [ ! -f "$BACKEND_CREDENTIALS_FILE" ]; then
    echo "Credentials not found. Please run the setup script."
    "$SCRIPT_DIR/setup_credentials.sh"
    # Check again after running setup
    if [ ! -f "$CREDENTIALS_FILE" ] || [ ! -f "$BACKEND_CREDENTIALS_FILE" ]; then
        echo "Credential setup failed or was cancelled. Exiting."
        exit 1
    fi
fi

# Activate Python virtual environment (assuming it's in SCRIPT_DIR/CS336P2)
if [ -d "$SCRIPT_DIR/CS336P2/bin" ]; then
    echo "Activating Python virtual environment..."
    source "$SCRIPT_DIR/CS336P2/bin/activate"
else
    echo "Error: Python virtual environment CS336P2 not found in $SCRIPT_DIR."
    echo "Please ensure the virtual environment is set up correctly in project_2/CS336P2."
    exit 1
fi

# Start the backend (FastAPI)
echo "Starting backend server..."
cd "$BACKEND_DIR"
# Use KMP_DUPLICATE_LIB_OK=TRUE for potential MKL issues on some systems
KMP_DUPLICATE_LIB_OK=TRUE python3 main.py &
BACKEND_PID=$!
cd "$SCRIPT_DIR" # Go back to project_2 dir

# Start the frontend (Next.js)
echo "Starting frontend development server..."
cd "$FRONTEND_DIR"
echo "Ensuring frontend dependencies are installed..."
npm install # Ensure dependencies are installed in the correct location
echo "Attempting to start frontend dev server..."
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR" # Go back to project_2 dir

# Wait for servers to start and open in browser
echo "Waiting for servers to start..."
sleep 10 # Adjust as needed

# Open in browser (optional)
if command_exists xdg-open; then
    xdg-open http://localhost:3000
elif command_exists open; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser."
fi

# Wait for user to exit
echo "Backend (PID: $BACKEND_PID) and Frontend (PID: $FRONTEND_PID) are running."
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C and kill both processes
trap 'kill $BACKEND_PID $FRONTEND_PID; echo "Servers stopped."; exit' INT

# Keep script running until Ctrl+C
wait