'''
to run script:

Windows:

- Command Prompt: 
set KMP_DUPLICATE_LIB_OK=TRUE 
python project_2\database_llm.py

- PowerShell:
$env:KMP_DUPLICATE_LIB_OK="TRUE"; python project_2\database_llm.py

macOS/Linux: KMP_DUPLICATE_LIB_OK=TRUE python project_2/database_llm.py
'''

import time
import os
import sys

import llm_manager
import query_extraction
import ssh_handler

# Path to the LLM model
model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"

# iLab configuration
hostname = "ilab.cs.rutgers.edu"
# Path to the script on iLab - adjust this to where you've placed it on the iLab system
ilab_script_path = "~/project_2/ilab_script.py"  

# Flag to enable extra credit functionality (using stdin instead of args)
use_stdin = True  # Set to False to use command-line args instead

def main():
    # Load the database schema
    context = llm_manager.load_schema()

    # Initialize the LLM
    try:
        print("Initializing the LLM...")
        llm = llm_manager.initalize_llm(model_name)
        print("LLM initialized successfully.")
    except Exception as e:
        print(f"Error initializing the LLM: {e}")
        sys.exit(1)

    # Get SSH credentials once at the beginning
    print("\nPlease enter your iLab credentials:")
    try:
        host, user, pwd = ssh_handler.get_ssh_credentials()
        
        # Test the connection to make sure credentials work
        print(f"\nTesting connection to {host}...")
        if use_stdin:
            test_result = ssh_handler.execute_query_stdin(host, user, pwd, "SELECT 1", ilab_script_path)
        else:
            test_result = ssh_handler.execute_query(host, user, pwd, "SELECT 1", ilab_script_path)
            
        if test_result is None:
            print("Failed to connect to iLab. Please check your credentials and try again.")
            sys.exit(1)
            
        print(f"Connection to {host} successful!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error connecting to iLab: {e}")
        sys.exit(1)
    
    print("\nConnected to iLab. You can now ask questions about the database.")
    print("Type 'exit' to quit the program.\n")

    # Main interaction loop
    while True:
        timestamp = time.strftime('%I:%M:%S %p %m/%d/%y', time.localtime(time.time()))

        try:
            # Get the question from the user
            question = input("\nEnter your question: ")

            if question.lower() == "exit":
                print("Exiting...")
                break

            print("Processing your question...")

            # Build the prompt for the LLM
            prompt = llm_manager.build_prompt(context, question)

            # Query the LLM
            response = llm_manager.query_llm(llm, prompt)

            # Log the interaction
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            with open(os.path.join(log_dir, 'llm_output.txt'), 'a') as f:
                f.write("\n\n==================== LOG ENTRY START ====================\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Question: {question}\n\n")
                f.write("--- LLM Response Start ---\n")
                f.write(f"{response}\n")
                f.write("--- LLM Response End ---\n\n")
                f.write("==================== LOG ENTRY END ======================\n\n")

            # Extract the SQL query from the LLM response
            try:
                query = query_extraction.extract_query_from_text(response)
                print(f"\nGenerated SQL Query:\n{query}\n")
            except ValueError as e:
                print(f"Error: {e}")
                print("The LLM didn't generate a SQL query. Please try rephrasing your question.")
                continue
            except (AttributeError, IndexError) as e:
                print(f"Error: Could not extract SQL query from LLM response.")
                print("The LLM might not have generated a valid SQL query.")
                print("Please try rephrasing your question.")
                continue
            except Exception as e:
                print(f"Error extracting query: {e}")
                print("Please try rephrasing your question.")
                continue

            # Execute the query on iLab
            print("Executing query on the database...")
            try:
                if use_stdin:
                    # Use stdin method (extra credit)
                    result = ssh_handler.execute_query_stdin(host, user, pwd, query, ilab_script_path)
                else:
                    # Use command-line argument method
                    result = ssh_handler.execute_query(host, user, pwd, query, ilab_script_path)
                
                if result:
                    print("\nQuery Results:")
                    print(result)
                else:
                    print("No results returned from the database. There might be an error with the query or connection.")
            except Exception as e:
                print(f"Error executing query: {e}")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Type 'exit' to quit the program.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()