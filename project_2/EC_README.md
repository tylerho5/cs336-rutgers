# CS336 Natural Language Database Interface - Extra Credit Project

This project enhances the original Natural Language Database Interface (Project 2) with a modern web interface. Users can ask questions about the database in plain English, and the system generates SQL queries, executes them, and displays the results in an interactive format.

## Video Demo

Video demonstrating the frontend, showing several queries as well as interacting with the tables.

## Project Structure

```
.
├── project_2/              # Original LLM database interface & Extra Credit UI Project
│   ├── backend/            # FastAPI backend API (EC)
│   ├── ec-frontend-nextjs/ # Next.js frontend (EC)
│   ├── CS336P2/            # Python virtual environment
│   ├── model/              # LLM models
│   ├── setup_credentials.sh # Script to set up database credentials (EC)
│   ├── run_ec_project.sh   # Script to run both backend and frontend (EC)
│   └── ...                 # Other project files for Project 2
├── LICENSE
└── environment.yml
```

## Features Implemented

- **Basic Working Frontend**: Input box for natural language queries and results display
- **Interactive Tables**: Sortable columns with clean formatting
- **Detailed Output View**: Separate tabs for:
  - SQL query and relational algebra
  - LLM processing output
  - Query results
- **Modern UI**: Clean, responsive design with intuitive navigation
- **Exporting Results**: Included the functionality to export tables generated to .csv file
- **Error Handling**: User-friendly error messages

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **LLMs**: Phi-3.5-mini (2GB), sqlcoder-7b-2 (4GB)
- **Database**: PostgreSQL (accessed via SSH tunneling)

## Setup and Running

### Prerequisites

- Python 3.8+
- Node.js 18.18.0+ (v20.0.0 or higher recommended, as required by Next.js)
- NPM
- Access to Rutgers iLab


**The set up instructions from the initial Project 2 README should be followed first before trying to run run_ec_project.sh**

### 1. Set Up Credentials

First, you need to set up your database credentials:

```bash
# Run the credentials setup script 
./project_2/setup_credentials.sh
```

This will create a `.env` file in the `project_2` directory and `project_2/backend` directory with your iLab and database credentials.

### 2. Quick Start

The easiest way to run the application is using the provided shell script:

```bash
# Make the script executable (if needed)
chmod +x ./project_2/run_ec_project.sh

# Run the application
./project_2/run_ec_project.sh
```

This will:
1. Check if credentials are set up (and prompt you to set them up if needed)
2. Start the FastAPI backend server on port 8000
3. Start the Next.js development server on port 3000
4. Open your browser to http://localhost:3000

### 3. Manual Setup

If you prefer to run the services manually:

#### Backend Setup

```bash
# Navigate to project_2 directory first
cd project_2

# Navigate to backend directory
cd backend

# Activate the virtual environment (from project_2/backend, path is ../CS336P2)
source ../CS336P2/bin/activate  

# Start the FastAPI server
KMP_DUPLICATE_LIB_OK=TRUE python3 main.py

# Navigate back to the root if needed
# cd ../..
```

#### Frontend Setup

```bash
# Navigate to project_2 directory first
cd project_2

# Navigate to frontend directory
cd ec-frontend-nextjs

# Install dependencies
npm install

# Start the development server
npm run dev

# Navigate back to the root if needed
# cd ../..
```

The application will be available at http://localhost:3000

### 4. Stopping the Application

To stop both the backend and frontend services that were started with `./project_2/run_ec_project.sh`, press `Ctrl+C` in the terminal where the script is running.

## How It Works

1. **User Input**: The user enters a natural language question
2. **Backend Processing**:
   - The question is sent to the FastAPI backend
   - The backend uses Phi-3.5-mini to convert the question to relational algebra
   - sqlcoder-7b-2 then converts the relational algebra to a SQL query
   - The query is executed on the Rutgers database via SSH
3. **Results Display**:
   - The results are displayed in an interactive table
   - Users can sort by clicking on column headers
   - Additional tabs show the SQL query, relational algebra, and LLM output

## Troubleshooting

If you encounter any issues:

1. **Connection Errors**: Make sure your iLab credentials are correct in the `.env` file
2. **Backend Not Starting**: Check that you have all required Python packages installed
3. **Frontend Not Connecting**: Ensure the backend is running on port 8000
4. **LLM Loading Errors**: Verify that the models are in the correct location in project_2/model/

### Handling Timeouts

The LLM processing and query execution can sometimes take a long time, especially for complex queries. The system is configured with the following timeouts:

- **Frontend request timeout**: 5 minutes (300 seconds)
- **Backend keep-alive timeout**: 5 minutes (300 seconds)

If you see timeout errors:

1. **AbortError/Request Timeout**: This means the query took longer than the 5-minute timeout. For very complex queries, consider:
   - Breaking the query into simpler questions
   - For LLM-intensive queries, restart the server to free up memory
   - Check server console output to see which step is taking the most time

2. **"Failed to fetch"**: This typically means the backend server isn't running or cannot be reached. Try:
   - Ensure the backend server is still running
   - Restart both backend and frontend services with `./project_2/run_ec_project.sh`
   - Check the terminal output for any error messages

3. **Database Connection Issues**: If you see "Authentication failed" or "Failed to connect to iLab database":
   - Run `./project_2/setup_credentials.sh` to update your credentials
   - Ensure you have access to the Rutgers iLab server
   - Check if your iLab password has expired

### Terminal Output

Helpful log messages are printed to the terminal where you ran `./project_2/run_ec_project.sh`. If you're experiencing issues, check this output for clues. It shows:

- The step-by-step processing of each query
- Timing information for each phase
- Any connection or processing errors

