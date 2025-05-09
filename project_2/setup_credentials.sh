#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CS336 Database Credentials Setup ====${NC}"
echo -e "${BLUE}This script will help you set up your database credentials for the project.${NC}"

# Get the directory where the script is located (project_2)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define the paths for the .env files
PROJECT_ENV_FILE="$SCRIPT_DIR/.env"
BACKEND_ENV_FILE="$SCRIPT_DIR/backend/.env"

# Function to prompt for credentials
prompt_for_credentials() {
    read -p "Enter your iLab NetID: " netid
    read -s -p "Enter your iLab Password: " password
    echo # Newline after password input
    read -p "Enter your Database Name (usually your NetID): " db_name
    read -p "Enter your Database User (usually your NetID): " db_user
}

# Function to create .env file
create_env_file() {
    local env_file_path=$1
    echo "Creating $env_file_path..."
    echo "NETID=$netid" > "$env_file_path"
    echo "PASSWORD=$password" >> "$env_file_path"
    echo "DB_NAME=$db_name" >> "$env_file_path"
    echo "DB_USER=$db_user" >> "$env_file_path"
    echo "$env_file_path created successfully."
}

# Main logic
echo "Setting up credentials..."

# Check if .env file exists in project_2 directory
if [ -f "$PROJECT_ENV_FILE" ]; then
  echo -e "${GREEN}Found existing .env file. Do you want to update it? (y/n)${NC}"
  read -r update_env
  if [[ "$update_env" != "y" && "$update_env" != "Y" ]]; then
    echo -e "${BLUE}Keeping existing credentials.${NC}"
    # Still copy to backend
    echo -e "${GREEN}Copying existing credentials to backend directory...${NC}"
    mkdir -p "$SCRIPT_DIR/backend"
    cp "$PROJECT_ENV_FILE" "$BACKEND_ENV_FILE"
    chmod 600 "$BACKEND_ENV_FILE"
    exit 0
  fi
fi

# Prompt for credentials
prompt_for_credentials

# Create .env file in project_2 directory
create_env_file "$PROJECT_ENV_FILE"

# Create .env file in project_2/backend directory
# Ensure backend directory exists
mkdir -p "$SCRIPT_DIR/backend"
create_env_file "$BACKEND_ENV_FILE"

echo -e "${GREEN}Credentials saved to $PROJECT_ENV_FILE and $BACKEND_ENV_FILE${NC}"
echo -e "${GREEN}You can now run ./run_ec_project.sh${NC}"