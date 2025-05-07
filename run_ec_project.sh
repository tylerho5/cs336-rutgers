#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CS336 Natural Language Database Interface ====${NC}"

# Check for required files
if [ ! -f "./project_2/.env" ]; then
  echo -e "${RED}Error: Database credentials not found.${NC}"
  echo -e "${BLUE}Would you like to set up your credentials now? (y/n)${NC}"
  read -r setup_creds
  if [[ "$setup_creds" == "y" || "$setup_creds" == "Y" ]]; then
    ./setup_credentials.sh
  else
    echo -e "${RED}Credentials are required to run the application.${NC}"
    echo -e "${BLUE}You can set them up later by running:${NC} ./setup_credentials.sh"
    exit 1
  fi
fi

# Copy credentials to backend directory for better access
echo -e "${GREEN}Copying credentials to backend directory...${NC}"
cp project_2/.env backend/.env
chmod 600 backend/.env

echo -e "${BLUE}Starting the backend and frontend services...${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to kill process running on a specific port
kill_process_on_port() {
  local port=$1
  if command_exists lsof; then
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
      echo -e "${BLUE}Killing existing process on port $port (PID: $pid)${NC}"
      kill -9 $pid 2>/dev/null || true
      sleep 1
    fi
  fi
}

# Check for required commands
if ! command_exists python3 ; then
  echo -e "${RED}Error: python3 is required but not installed.${NC}"
  exit 1
fi

if ! command_exists npm ; then
  echo -e "${RED}Error: npm is required but not installed.${NC}"
  exit 1
fi

# Kill any existing processes on our ports
echo -e "${BLUE}Checking for existing processes...${NC}"
kill_process_on_port 8000
kill_process_on_port 3000

# Path setup
BACKEND_DIR="./backend"
FRONTEND_DIR="./ec-frontend-nextjs"
VENV_PATH="./project_2/CS336P2"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
  echo -e "${RED}Error: Backend directory not found at $BACKEND_DIR${NC}"
  exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
  echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
  exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
  echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
  exit 1
fi

# Start backend
echo -e "${GREEN}Starting backend service...${NC}"
cd "$BACKEND_DIR" || exit
source "../$VENV_PATH/bin/activate"
# Add PYTHONUNBUFFERED to see all output immediately
PYTHONUNBUFFERED=1 KMP_DUPLICATE_LIB_OK=TRUE python3 main.py &
BACKEND_PID=$!
echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"

# Wait a moment for backend to initialize
sleep 2
echo -e "${GREEN}Backend is running at http://localhost:8000${NC}"

# Back to root
cd ..

# Start frontend
echo -e "${GREEN}Starting frontend service...${NC}"
cd "$FRONTEND_DIR" || exit
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
echo -e "${GREEN}Frontend is running at http://localhost:3000${NC}"

echo -e "${BLUE}Both services are now running.${NC}"
echo -e "${BLUE}Visit http://localhost:3000 in your browser to use the application.${NC}"
echo -e "${BLUE}Press Ctrl+C to stop both services.${NC}"

# Trap cleanup
cleanup() {
  echo -e "${BLUE}Stopping services...${NC}"
  kill $BACKEND_PID
  kill $FRONTEND_PID
  echo -e "${BLUE}All services stopped.${NC}"
  exit 0
}

trap cleanup INT

# Keep the script running
wait 