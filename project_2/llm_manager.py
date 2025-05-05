import contextlib
import os
from pathlib import Path

from llama_cpp import Llama

def load_schema():
    '''
    load database schema from cut-down project_1 sql file
    '''
    
    context = ""

    with open("project_2/schema_context.txt", "r") as f:
        context = f.read()

    return context

def build_breakdown_prompt(context, question):
    """
    build a prompt for LLM to generate a query plan/breakdown
    """
    prompt = f"""
        Question: {question}
        Schema: {context}

        Instructions:
        Generate a concise PostgreSQL query plan in English based on the Question and Schema.
        Include: Tables, JOINs (keys), SELECT (table.col), WHERE, GROUP BY/aggregations, ORDER BY.
        Output ONLY the plan steps in English. Do NOT include any SQL code or explanations.

        Plan:
    """
    return prompt

def build_sql_from_breakdown_prompt(breakdown, context, question):
    '''
    build prompt for LLM to generate SQL from a breakdown/plan
    '''
    prompt = f"""
        Original Question: {question}

        Query Plan: {breakdown}

        Schema: {context}

        Instructions:
        1. Translate the Query Plan into a single, valid PostgreSQL query.
        2. Use fully qualified column names (alias.column) for ALL columns.
        3. Use meaningful table aliases.
        4. Follow the Plan's JOINs, filters, grouping, and ordering precisely.
        5. Match schema names EXACTLY (case-sensitive).
        6. If using aggregates, include non-aggregated SELECT columns in GROUP BY.
        7. Output ONLY the SQL query in ```sql markdown tags.

        SQL Query:
    """
    return prompt

def build_correction_prompt(question, query, raw_db_output, relevant_schema, breakdown): # Added breakdown parameter, changed error_msg to raw_db_output
    '''
    Build a concise prompt for LLM to correct a SQL query error, using the original breakdown.
    '''

    specific_guidance = ""
    # Check for keywords in the raw database output
    if "column" in raw_db_output.lower() and "does not exist" in raw_db_output.lower():
        specific_guidance = """
            Hint: Column Not Found. Check: Typo? Wrong table? Missing JOIN? Incorrect alias? Check HINT in error.
        """
    # Missing JOIN condition
    elif "cross join" in raw_db_output.lower() or "missing join condition" in raw_db_output.lower():
        specific_guidance = """
            Hint: Missing JOIN Condition. Check: JOIN clause missing ON? Incorrect ON syntax?
        """
    # Ambiguous column reference
    elif "ambiguous" in raw_db_output.lower() and "column" in raw_db_output.lower():
        specific_guidance = """
            Hint: Ambiguous Column. Check: Column in multiple tables? Qualify with alias (alias.column)?
        """
    # Missing GROUP BY columns
    elif "must appear in the group by clause" in raw_db_output.lower() or "not in group by" in raw_db_output.lower():
        specific_guidance = """
            Hint: GROUP BY Error. Check: Non-aggregated SELECT columns missing from GROUP BY?
        """
    # Syntax error
    elif "syntax error" in raw_db_output.lower():
        specific_guidance = """
            Hint: SQL Syntax Error. Check: Typos? Missing/extra commas/parentheses/quotes? Check HINT in error.
        """
    # Table does not exist
    elif "relation" in raw_db_output.lower() and "does not exist" in raw_db_output.lower():
        specific_guidance = """
            Hint: Table Not Found ('relation does not exist'). Check: Typo? Alias used as table name? Check schema.
        """

    prompt = f"""
        Fix the SQL query based on the full error output, original plan, and schema. Pay special attention to the error in the database error output if there is one.

        Original question: {question}

        Original Plan: {breakdown}

        Failed SQL query:
        ```sql
        {query}
        ```

        Full Database Error Output: {raw_db_output}

        {specific_guidance}

        Corrected SQL Query:
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
                    "role": "system",
                    "content": "You are an expert PostgreSQL assistant."
                },
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
