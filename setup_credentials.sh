#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CS336 Database Credentials Setup ====${NC}"
echo -e "${BLUE}This script will help you set up your database credentials for the project.${NC}"

# Check if .env file exists in project_2 directory
ENV_FILE="./project_2/.env"
BACKEND_ENV_FILE="./backend/.env"

if [ -f "$ENV_FILE" ]; then
  echo -e "${GREEN}Found existing .env file. Do you want to update it? (y/n)${NC}"
  read -r update_env
  if [[ "$update_env" != "y" && "$update_env" != "Y" ]]; then
    echo -e "${BLUE}Keeping existing credentials.${NC}"
    # Still copy to backend
    echo -e "${GREEN}Copying existing credentials to backend directory...${NC}"
    mkdir -p ./backend
    cp "$ENV_FILE" "$BACKEND_ENV_FILE"
    chmod 600 "$BACKEND_ENV_FILE"
    exit 0
  fi
fi

# Prompt for credentials
echo -e "${BLUE}Please enter your iLab credentials:${NC}"
echo -n "NetID: "
read -r netid

echo -n "Password: "
read -rs password
echo ""

echo -n "Database name (usually same as NetID): "
read -r db_name
if [ -z "$db_name" ]; then
  db_name=$netid
fi

echo -n "Database username (usually same as NetID): "
read -r db_user
if [ -z "$db_user" ]; then
  db_user=$netid
fi

# Create or update .env files
mkdir -p ./project_2
mkdir -p ./backend

# Project 2 .env file
echo "NETID=$netid" > "$ENV_FILE"
echo "PASSWORD=$password" >> "$ENV_FILE"
echo "DB_NAME=$db_name" >> "$ENV_FILE"
echo "DB_USER=$db_user" >> "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Backend .env file
echo "NETID=$netid" > "$BACKEND_ENV_FILE"
echo "PASSWORD=$password" >> "$BACKEND_ENV_FILE"
echo "DB_NAME=$db_name" >> "$BACKEND_ENV_FILE"
echo "DB_USER=$db_user" >> "$BACKEND_ENV_FILE"
chmod 600 "$BACKEND_ENV_FILE"

echo -e "${GREEN}Credentials saved to $ENV_FILE and $BACKEND_ENV_FILE${NC}"
echo -e "${GREEN}You can now run ./run_ec_project.sh${NC}" 