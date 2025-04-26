import llm_manager
import ssh_handler
import ilab_script

model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"

def main():
    # Load the database schema
    context = llm_manager.load_schema()

    # Initialize the LLM
    llm = llm_manager.initalize_llm(model_name)

    # Get the question from the user
    question = input("Enter your question: ")

    # Build the prompt for the LLM
    prompt = llm_manager.build_prompt(context, question)

    # Query the LLM
    sql_query = llm_manager.query_llm(llm, prompt)

    print(f"Generated SQL Query: {sql_query}")

if __name__ == "__main__":
    main()