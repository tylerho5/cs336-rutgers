r'''
to run script:

Windows:

- Command Prompt: 
set KMP_DUPLICATE_LIB_OK=TRUE python project_2\database_llm.py

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
from error_extraction import extract_error_from_result

# path to llm model
# model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"
# model_name = "Phi-3.5-mini-instruct-Q8_0.gguf"
model_name = "sqlcoder-7b-q5_k_m.gguf"

# ilab configuration
hostname = "ilab.cs.rutgers.edu"

# adjust this to where ilab_script.py is placed on iLab instance
wd_path = "~/cs336/project_2"

# set to False to use command-line args instead of stdin
use_stdin = True  

# Maximum number of correction attempts
MAX_CORRECTION_ATTEMPTS = 3

def main():
    # get ssh credentials once at the beginning
    try:
        user, pwd = ssh_handler.get_ssh_credentials()
        
        # test the connection to make sure credentials work
        print(f"Testing connection to {hostname}...")
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

    # load the database schema
    context = llm_manager.load_schema()

    print("\nYou can now ask questions about the database.")
    print("Type 'exit' to quit the program.\n")

    # create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # main loop
    while True:
        timestamp = time.strftime('%I:%M:%S %p %m/%d/%y', time.localtime(time.time()))

        try:
            question = input("Enter your question: ")

            if question.lower() == "exit":
                print("Exiting...")
                break

            print("\nProcessing your question...")

            # --- Step 1: Generate Query Breakdown ---
            print("Generating query plan...")
            breakdown_prompt = llm_manager.build_breakdown_prompt(context, question)
            breakdown_llm = llm_manager.get_breakdown_llm()
            breakdown = llm_manager.query_llm(breakdown_llm, breakdown_prompt)
            print(f"\nRelational Algebra Expression:\n{breakdown}\n")

            # Log breakdown generation
            with open(os.path.join(log_dir, 'llm_output.txt'), 'a') as f:
                f.write("\n\n==================== LOG ENTRY START ====================\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Question: {question}\n\n")
                f.write("--- Breakdown Prompt ---\n")
                f.write(f"{breakdown_prompt}\n\n")
                f.write("--- LLM Breakdown Response ---\n")
                f.write(f"{breakdown}\n")
                # Separator before SQL generation log
                f.write("--------------------------------------------------------\n\n")

            # --- Step 2: Generate SQL from Breakdown ---
            print("Generating SQL query from plan...")
            sql_prompt = llm_manager.build_sql_from_breakdown_prompt(breakdown, context, question)
            sql_llm = llm_manager.get_sql_llm()
            response = llm_manager.query_llm(sql_llm, sql_prompt)

            # Log SQL generation response (append to the same log entry)
            with open(os.path.join(log_dir, 'llm_output.txt'), 'a') as f:
                f.write("--- SQL Generation Prompt ---\n")
                f.write(f"{sql_prompt}\n\n")
                f.write("--- LLM SQL Response Start ---\n")
                f.write(f"{response}\n")
                f.write("--- LLM SQL Response End ---\n\n")
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

            # execute the query on iLab with error feedback loop
            print("Executing query on the database...")
            
            # Track the number of correction attempts
            correction_attempts = 0
            current_query = query
            success = False
            
            while correction_attempts < MAX_CORRECTION_ATTEMPTS:
                try:
                    if use_stdin:
                        result = ssh_handler.execute_query_stdin(hostname, user, pwd, current_query, wd_path, user, pwd)
                    else:
                        result = ssh_handler.execute_query(hostname, user, pwd, current_query, wd_path, user, pwd)
                    
                    # Check if there's an error in the result
                    if result is None or "error" in result.lower():
                        correction_attempts += 1
                        
                        # On final attempt, give up and show error
                        if correction_attempts == MAX_CORRECTION_ATTEMPTS:
                            print(f"\nFailed to generate a valid SQL query after {MAX_CORRECTION_ATTEMPTS} attempts.")
                            print("Query result:")
                            print(result)
                            print("\nDespite error feedback looping the LLM was unable to generate a valid SQL query for your query statement, please validate your query statement or consider using a better LLM model.")
                            break
                            
                        print(f"Query encountered an error. Attempt {correction_attempts} of {MAX_CORRECTION_ATTEMPTS} to fix...")
                        
                        # Extract error message
                        error_msg = extract_error_from_result(result)
                        
                        # Get the full schema for error correction
                        full_schema = llm_manager.load_schema()

                        # Build correction prompt 
                        correction_prompt = llm_manager.build_correction_prompt(question, current_query, error_msg, full_schema, breakdown)
                        
                        # Get corrected query from LLM
                        print("Generating corrected query...")
                        correction_llm = llm_manager.get_sql_llm()
                        correction_response = llm_manager.query_llm(correction_llm, correction_prompt)
                        
                        # Log the correction attempt
                        with open(os.path.join(log_dir, 'query_corrections.txt'), 'a') as f:
                            f.write(f"\n\n==================== CORRECTION LOG START (Attempt {correction_attempts}) ====================\n")
                            f.write(f"Timestamp: {timestamp}\n")
                            f.write(f"Question: {question}\n\n")
                            f.write("--- Original Query ---\n")
                            f.write(f"{query}\n\n") # Log the *initial* query generated
                            f.write("--- Query Plan/Breakdown ---\n") # Log the breakdown used
                            f.write(f"{breakdown}\n\n")
                            f.write("--- Failed Query (Attempt {correction_attempts}) ---\n")
                            f.write(f"{current_query}\n\n")
                            f.write("--- Error Message ---\n")
                            f.write(f"{error_msg}\n\n")
                            f.write("--- Correction Prompt ---\n")
                            f.write(f"{correction_prompt}\n\n")
                            f.write("--- LLM Correction Response ---\n")
                            f.write(f"{correction_response}\n\n")
                            f.write(f"==================== CORRECTION LOG END (Attempt {correction_attempts}) ======================\n\n")

                        # Extract corrected query
                        try:
                            corrected_query = query_extraction.extract_query_from_text(correction_response)
                            print(f"\nCorrected SQL Query (Attempt {correction_attempts}):\n{corrected_query}\n")
                            
                            # Update the current query for the next attempt
                            current_query = corrected_query
                            
                        except Exception as e:
                            print(f"Error extracting corrected query: {e}")
                            print("Could not generate a corrected query. Please try rephrasing your question.")
                            break
                    else:
                        # Success! Display results and break the loop
                        print("\nQuery Results:")
                        print(result)
                        success = True
                        break
                        
                except Exception as e:
                    print(f"Error executing query: {e}")
                    break
            
            # If we made it through the loop without success, but didn't show the error yet
            if not success and correction_attempts > 0 and correction_attempts < MAX_CORRECTION_ATTEMPTS:
                print("\nNo results returned from the database. There might be an error with the query or connection.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Type 'exit' to quit the program.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()