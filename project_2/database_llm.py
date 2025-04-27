import time

import ilab_script
import llm_manager
import query_extraction
import ssh_handler


model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"

def main():
    # load the database schema
    context = llm_manager.load_schema()

    # initialize the llm
    llm = llm_manager.initalize_llm(model_name)

    while True:

        timestamp = time.strftime('%I:%M:%S %p %m/%d/%y', time.localtime(time.time()))

        # get the question from the user
        question = input("Enter your question: ")
        question = question.strip()

        if question.lower() == "exit":
            print("Exiting...")
            break

        # build the prompt for the llm
        prompt = llm_manager.build_prompt(context, question)

        # prompt the llm
        response = llm_manager.query_llm(llm, prompt)
        response = response.strip()

        with open('llm_output.txt', 'a') as f:
            f.write("\n\n==================== LOG ENTRY START ====================\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Question: {question}\n\n")
            f.write("--- LLM Response Start ---\n")
            f.write(f"{response}\n")
            f.write("--- LLM Response End ---\n\n")
            f.write("==================== LOG ENTRY END ======================\n\n")

        query = query_extraction.extract_query_from_text(response)

        print(f"Generated response: \n{query}\n")

if __name__ == "__main__":
    main()