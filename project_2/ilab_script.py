"""
ilab_script.py

This script runs on iLab to execute SQL queries on the Rutgers database.
It takes a SQL query as a command-line argument or from stdin,
executes it, and formats the results using pandas.

Usage:
    python3 ilab_script.py "SELECT * FROM Agency"
    echo "SELECT * FROM Agency" | python3 ilab_script.py

Environment Variables:
    DB_USER: Your database username
    DB_PASSWORD: Your database password (if needed)
"""

import sys
import os
import pandas as pd
import psycopg2
from psycopg2 import sql
import dotenv 

# load environment variables from .env file
dotenv.load_dotenv()

# database connection params, grabbing from environment
DB_NAME = os.getenv("DB_USER", "postgres")
DB_USER = os.getenv("DB_USER", "default_user")  
# grabs pass, otherwise default is no pass
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = "postgres.cs.rutgers.edu"
DB_PORT = "5432"

def get_db_connection():
    '''
    connect to database on iLab
    '''
    
    # check if DB_USER loaded properly
    if DB_USER == "default_user" and os.getenv("DB_USER") is None:
        print("Error: DB_USER environment variable not set.", file=sys.stderr)
        print("Please create a .env file with DB_USER='your_username'", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Build connection parameters
        conn_params = {
            "dbname": DB_NAME,
            "user": DB_USER,
            "host": DB_HOST,
            "port": DB_PORT,
            "connect_timeout": 15 # Increase connection timeout to 15 seconds
        }
        
        # Add password only if it's not empty
        if DB_PASSWORD:
            conn_params["password"] = DB_PASSWORD
            
        # Connect to the database
        conn = psycopg2.connect(**conn_params)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)

def execute_query(query):
    """Execute the SQL query and return the results"""
    conn = None
    try:
        conn = get_db_connection()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Check if there are results to fetch
        if cursor.description is None:
            # No results (e.g., for INSERT, UPDATE statements)
            return None, None
            
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        return column_names, results
    except psycopg2.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        if conn:
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"Error executing query: {e}", file=sys.stderr)
        if conn:
            conn.close()
        sys.exit(1)

def format_results(column_names, results):
    """Format results as a pandas DataFrame"""
    try:
        # If no results or column names, return appropriate message
        if column_names is None or results is None:
            return "Query executed successfully, but no results were returned."
        
        if len(results) == 0:
            return "Query returned no data."
            
        # Create pandas DataFrame
        df = pd.DataFrame(results, columns=column_names)
        
        # Format and return the DataFrame as a string
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error formatting results: {e}", file=sys.stderr)
        return f"Error formatting results: {e}"

def main():
    """Main function to process arguments and execute query"""
    # Check if query is passed as argument or should be read from stdin
    if len(sys.argv) > 1:
        # Query is passed as an argument
        query = sys.argv[1]
    else:
        # Read query from stdin (for extra credit)
        try:
            query = sys.stdin.read().strip()
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Validate that we have a query
    if not query:
        print("Error: No SQL query provided", file=sys.stderr)
        print("Usage: python3 ilab_script.py \"SELECT * FROM Agency\"", file=sys.stderr)
        print("   or: echo \"SELECT * FROM Agency\" | python3 ilab_script.py", file=sys.stderr)
        sys.exit(1)
    
    # Make sure query is a SELECT query for safety
    if not query.strip().upper().startswith("SELECT"):
        print("Error: Only SELECT queries are allowed for security reasons", file=sys.stderr)
        sys.exit(1)
    
    # Execute the query
    column_names, results = execute_query(query)
    
    # Format and print the results
    formatted_results = format_results(column_names, results)
    print(formatted_results)

if __name__ == "__main__":
    main()
