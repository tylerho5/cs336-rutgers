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

# path to llm model
model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"

# ilab configuration
hostname = "ilab.cs.rutgers.edu"

# adjust this to where ilab_script.py is placed
wd_path = "~/cs336/project_2"

# set to False to use command-line args instead of stdin
use_stdin = True  

def main():
    # load the database schema
    context = llm_manager.load_schema()

    # initialize the llm
    try:
        print("Initializing the LLM...")
        llm = llm_manager.initalize_llm(model_name)
        print("LLM initialized successfully.")
    except Exception as e:
        print(f"Error initializing the LLM: {e}")
        sys.exit(1)

    # get ssh credentials once at the beginning
    print("\nPlease enter your iLab credentials:")
    try:
        user, pwd = ssh_handler.get_ssh_credentials()
        
        # test the connection to make sure credentials work
        print(f"\nTesting connection to {hostname}...")
        if use_stdin:
            test_result = ssh_handler.execute_query_stdin(hostname, user, pwd, "SELECT 1", wd_path, user, pwd)

        else:
            test_result = ssh_handler.execute_query(hostname, user, pwd, "SELECT 1", wd_path, user, pwd)
            
        if test_result is None:
            print("Failed to connect to iLab. Please check your credentials and try again.")
            sys.exit(1)
            
        print(f"Connection to {hostname} successful!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error connecting to iLab: {e}")
        sys.exit(1)
    
    print("\nConnected to iLab. You can now ask questions about the database.")
    print("Type 'exit' to quit the program.\n")

    # main loop
    while True:
        timestamp = time.strftime('%I:%M:%S %p %m/%d/%y', time.localtime(time.time()))

        try:
            question = input("\nEnter your question: ")

            if question.lower() == "exit":
                print("Exiting...")
                break

            print("Processing your question...")

            # build prompt for llm
            prompt = llm_manager.build_prompt(context, question)

            # pass prompt to llm
            response = llm_manager.query_llm(llm, prompt)

            # log response
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

            # extract SQL query from llm response
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

            # execute the query on iLab
            print("Executing query on the database...")
            try:
                if use_stdin:
                    result = ssh_handler.execute_query_stdin(hostname, user, pwd, query, wd_path, user, pwd)

                else:
                    result = ssh_handler.execute_query(hostname, user, pwd, query, wd_path, user, pwd)
                
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