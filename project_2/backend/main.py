from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import time
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load .env file from the backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Add the project_2 directory to Python path
project_2_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_2_path)

# Import your existing modules
import llm_manager
import query_extraction
import ssh_handler
from error_extraction import extract_error_from_result

# Database LLM instance as a global variable
db_llm = None

# Lifespan manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_llm
    try:
        # Initialize without testing connection at startup
        db_llm = DatabaseLLM(test_connection=False)
        print("DatabaseLLM initialized successfully.")
    except Exception as e:
        print(f"Error initializing DatabaseLLM: {e}")
        raise
    
    yield  # App running
    
    # Shutdown - close all SSH connections
    print("Shutting down application, cleaning up resources...")
    ssh_handler.close_all_connections()

# Create FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class DatabaseLLM:
    def __init__(self, test_connection=True):
        # Initialize SSH credentials
        self.user, self.pwd = ssh_handler.get_ssh_credentials()
        print(f"Using credentials - User: {self.user}, Password: {'*' * len(self.pwd) if self.pwd else 'None'}")
        self.hostname = "ilab.cs.rutgers.edu"
        self.wd_path = "~/cs336/project_2"
        self.use_stdin = True
        self.connection_tested = False
        
        # Change to project_2 directory to load schema
        original_dir = os.getcwd()
        os.chdir(project_2_path)
        try:
            self.context = llm_manager.load_schema()
        finally:
            os.chdir(original_dir)
            
        # Only test connection if requested (we'll do this lazily now)
        if test_connection:
            self.test_connection()
    
    def test_connection(self):
        """Test the connection to iLab, returning True if successful, False otherwise"""
        try:
            print("Testing connection to iLab database...")
            print(f"Connection details: {self.hostname}, {self.user}, Path: {self.wd_path}")
            test_result = ssh_handler.execute_query_stdin(
                self.hostname, self.user, self.pwd, 
                "SELECT 1", self.wd_path, self.user, self.pwd
            )
            self.connection_tested = True
            if test_result is None:
                print("Failed to connect to iLab database. Check your credentials.")
                return False
            print("Successfully connected to iLab database.")
            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False

    def process_query(self, question: str):
        # Test connection if not already tested
        if not self.connection_tested:
            print("Connection not tested yet, testing now...")
            connection_success = self.test_connection()
            if not connection_success:
                return {
                    "sql_query": "",
                    "relational_algebra": "",
                    "llm_output": "",
                    "results": "",
                    "error": "Failed to connect to iLab database. Please check your credentials."
                }
        
        try:
            # Log start time
            start_time = time.time()
            print(f"Processing query: '{question}'")
            
            # Generate query breakdown
            print("Generating relational algebra using Phi-3.5-mini...")
            breakdown_prompt = llm_manager.build_breakdown_prompt(self.context, question)
            breakdown_llm = llm_manager.get_breakdown_llm()
            breakdown = llm_manager.query_llm(breakdown_llm, breakdown_prompt)
            
            algebra_time = time.time()
            print(f"Relational algebra generated in {algebra_time - start_time:.2f} seconds")
            print(f"Relational Algebra: {breakdown}")

            # Generate SQL
            print("Generating SQL query using sqlcoder-7b-2...")
            sql_prompt = llm_manager.build_sql_from_breakdown_prompt(breakdown, self.context, question)
            sql_llm = llm_manager.get_sql_llm()
            response = llm_manager.query_llm(sql_llm, sql_prompt)
            
            sql_time = time.time()
            print(f"SQL query generated in {sql_time - algebra_time:.2f} seconds")

            # Extract SQL query
            query = query_extraction.extract_query_from_text(response)
            print(f"Extracted SQL query: {query}")

            # Execute query
            print("Executing query on iLab database...")
            result = ssh_handler.execute_query_stdin(
                self.hostname, self.user, self.pwd,
                query, self.wd_path, self.user, self.pwd
            )
            
            end_time = time.time()
            print(f"Query executed in {end_time - sql_time:.2f} seconds")
            print(f"Total processing time: {end_time - start_time:.2f} seconds")

            return {
                "sql_query": query,
                "relational_algebra": breakdown,
                "llm_output": response,
                "results": result,
                "error": None
            }

        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "sql_query": "",
                "relational_algebra": "",
                "llm_output": "",
                "results": "",
                "error": str(e)
            }

@app.post("/api/query")
async def process_query(request: QueryRequest):
    try:
        if not db_llm:
            raise HTTPException(status_code=500, detail="Database LLM not initialized")
        
        # Process the query using your existing system
        result = db_llm.process_query(request.query)
        
        # Check if there was a connection error
        if result.get("error") and "Failed to connect" in result.get("error"):
            raise HTTPException(status_code=503, detail=result.get("error"))
        
        return {
            "original_query": request.query,
            "sql_query": result.get("sql_query", ""),
            "relational_algebra": result.get("relational_algebra", ""),
            "llm_output": result.get("llm_output", ""),
            "results": result.get("results", ""),
            "error": result.get("error", None)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=300)