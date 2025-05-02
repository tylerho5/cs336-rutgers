import contextlib
import os
from pathlib import Path

from llama_cpp import Llama

structured_prompting = True

def load_schema():
    '''
    load database schema from cut-down project_1 sql file
    '''
    
    context = ""

    with open("project_2/schema_context.sql", "r") as f:
        context = f.read()

    return context

def build_prompt(context, question):
    '''
    build prompt for LLM
    '''

    if structured_prompting:
        prompt = f"""
        Input Schema: 
        {context}

        Input Question:
        {question}

        Instructions:
        1. Analyze the question.
        2. Identify necessary tables and columns strictly from the Input Schema provided above. Verify names match exactly.
        3. Construct one PostgreSQL query to answer the question.
        4. Output only the generated SQL query.
        5. Enclose the query in ```sql markdown tags.
        """
    
    else: 
        prompt = f"""
            You are an expert PostgreSQL assistant. You will be given a database schema and a question.
            Your task is to generate a single, valid PostgreSQL query that answers the question based *only* on the provided schema.
            Carefully verify that all table names and column names used in your query exist exactly as defined in the schema below. Do not use any tables or columns not explicitly mentioned.

            Schema:
            {context}

            Question:
            {question}

            Provide *only* the SQL query, enclosed in ```sql markdown tags. Do not include any explanations or introductory text.
            SQL:
            """

    return prompt

def query_llm(llm, prompt):
    '''
    query the LLM with the given prompt
    '''

    # use create_chat_completion for instruction-tuned models
    try: 
        output = llm.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500
        )
        
    except Exception as e:
        print(f"Error querying LLM: {e}")
        quit()
    
    return output['choices'][0]['message']['content']

def initalize_llm(model_name):
    '''
    Initialize the local LLM model
    '''

    # construct the absolute path to the model file relative to this script
    script_dir = Path(__file__).parent
    model_file_path = script_dir / 'model' / model_name

    # suppress stderr during Llama initialization
    with open(os.devnull, 'w') as f, contextlib.redirect_stderr(f):
        try:
            llm = Llama(
                model_path=str(model_file_path), # may not need to cast to str
                n_gpu_layers=-1,
                seed=1337,
                n_ctx=4096,
                verbose=False  # keep this to disable other logs
            )

        except Exception as e:
            print(f"Error loading LLM: {e}")
            print("Consider checking model path...")
            quit()

    return llm
