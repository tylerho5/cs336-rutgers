import contextlib
import os
from pathlib import Path

from llama_cpp import Llama

# toggle for prompting style for testing
structured_prompting = True

def load_schema():
    '''
    load database schema from cut-down project_1 sql file
    '''
    
    context = ""

    with open("project_2/schema_context.txt", "r") as f:
        context = f.read()

    return context

def build_prompt(context, question):
    '''
    build prompt for LLM
    has option to either use structured formatting or regular sentences
    '''

    # Two different styles of prompting for testing purposes
    # not sure if structured is better
    if structured_prompting:
        prompt = f"""
            Query:
            {question}

            Database Schema:
            {context}

            Instructions:
            1. Analyze the question carefully to identify the entities and attributes needed.
            2. IMPORTANT: Always use fully qualified column names (table.column) for ALL columns.
            3. When joining tables:
               - Identify whether you need junction tables for many-to-many relationships
               - Always use the correct join keys as specified in the schema
               - Use meaningful table aliases consistently throughout the query
            4. Follow proper SQL patterns:
               - Use explicit JOIN syntax with proper ON conditions
               - Match column and table names EXACTLY as they appear in the schema
               - GROUP BY all non-aggregated columns in SELECT statements
               - Use appropriate aliases for calculated columns
            5. Check the schema carefully before writing your query:
               - Verify all tables and columns exist exactly as specified
               - Identify primary and foreign key relationships
               - Note any junction tables needed for many-to-many relationships
            6. Construct a single PostgreSQL query that answers the question precisely.
            7. Output only the SQL query enclosed in ```sql markdown tags.

            Common Errors to Avoid:
            1. NEVER use unqualified column names when joining multiple tables
            2. NEVER try to directly join tables that require junction tables - check the schema
            3. NEVER reference columns that don't exist in the schema (verify each column name carefully)
            4. ALWAYS include all necessary JOINs when accessing related tables
            5. ALWAYS check for and use junction tables for many-to-many relationships
            6. ALWAYS use the exact table and column names as they appear in the schema
            7. Be careful with aggregate functions (COUNT, SUM, etc.) - include GROUP BY for all non-aggregated columns
            8. Avoid ambiguous column references - always qualify with table name or alias
            """
    
    else: 
        prompt = f"""
            You are an expert PostgreSQL assistant. You will be given a database schema and a question.
            Your task is to generate a single, valid PostgreSQL query that answers the question based *only* on the provided schema.
            Carefully verify that all table names and column names used in your query exist exactly as defined in the schema below. Do not use any tables or columns not explicitly mentioned.

            Query:
            {question}

            Database Schema:
            {context}

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
