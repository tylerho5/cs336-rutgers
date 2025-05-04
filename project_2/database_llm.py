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
import error_extraction

# path to llm model
model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"

# ilab configuration
hostname = "ilab.cs.rutgers.edu"

# adjust this to where ilab_script.py is placed on iLab instance
wd_path = "~/cs336/project_2"

# set to False to use command-line args instead of stdin
use_stdin = True  

# Maximum number of correction attempts
MAX_CORRECTION_ATTEMPTS = 3

def main():
    # load the database schema
    context = llm_manager.load_schema()

    # initialize the llm
    try:
        print("\nInitializing the LLM...")
        llm = llm_manager.initalize_llm(model_name)
        print("LLM initialized successfully.")
    except Exception as e:
        print(f"Error initializing the LLM: {e}")
        sys.exit(1)

    # get ssh credentials once at the beginning
    print("\nPlease enter your iLab credentials")
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
    
    print("\nYou can now ask questions about the database.")
    print("Type 'exit' to quit the program.\n")

    # create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

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
                        error_msg = error_extraction.extract_error_from_result(result)
                        
                        # Get relevant schema subset based on tables in the query
                        relevant_schema = error_extraction.extract_relevant_schema(current_query, context)
                        
                        # Build correction prompt
                        correction_prompt = llm_manager.build_correction_prompt(question, current_query, error_msg, relevant_schema)
                        
                        # Get corrected query from LLM
                        print("Generating corrected query...")
                        correction_response = llm_manager.query_llm(llm, correction_prompt)
                        
                        # Log the correction attempt
                        with open(os.path.join(log_dir, 'query_corrections.txt'), 'a') as f:
                            f.write(f"\n\n==================== CORRECTION LOG START (Attempt {correction_attempts}) ====================\n")
                            f.write(f"Timestamp: {timestamp}\n")
                            f.write(f"Question: {question}\n\n")
                            f.write("--- Original Query ---\n")
                            f.write(f"{query}\n\n")
                            f.write("--- Current Query ---\n")
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