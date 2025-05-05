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
        User Question: {question}

        Schema:
        {context}

        Instructions:
        Create a step-by-step English plan for a PostgreSQL query based on the User Question and Schema.
        Focus on: Tables, JOINs (with keys), SELECT columns (table.col), WHERE filters, GROUP BY/aggregations, ORDER BY.
        Output only the plan, no SQL, no explanations. Be as concise as possible.

        Plan:
    """
    return prompt

def build_sql_from_breakdown_prompt(breakdown, context, question):
    '''
    build prompt for LLM to generate SQL from a breakdown/plan
    '''
    prompt = f"""
        Original Question: {question}

        Query Plan:
        {breakdown}

        Schema:
        {context}

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

def build_correction_prompt(question, query, error_msg, relevant_schema, breakdown): # Added breakdown parameter
    '''
    Build a concise prompt for LLM to correct a SQL query error, using the original breakdown.
    '''

    specific_guidance = ""
    if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: Column Not Found.
            Possible Causes:
            1. Typo in column name (check schema).
            2. Column exists in a different table than specified (check JOINs and aliases).
            3. Trying to access a descriptive field (e.g., `race_name`) from a junction table (e.g., `ApplicantRace`) instead of the lookup table (e.g., `Race`). You MUST join to the lookup table.
            4. Missing table alias or incorrect alias used.
            Check the original Query Plan/Breakdown for intended logic.
        """
    # Missing JOIN condition
    elif "cross join" in error_msg.lower() or "missing join condition" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: Missing JOIN Condition.
            Possible Causes:
            1. A JOIN clause is missing its ON condition.
            2. Incorrect syntax in the ON condition.
            Check the original Query Plan/Breakdown for intended JOINs.
        """
    # Ambiguous column reference
    elif "ambiguous" in error_msg.lower() and "column" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: Ambiguous Column Reference.
            Possible Causes:
            1. A column name exists in multiple tables in the FROM/JOIN clauses, and it wasn't qualified with a table alias (e.g., `alias.column`).
            2. An alias was forgotten or used inconsistently.
            Always use table aliases and qualify all columns when multiple tables are joined.
        """
    # Missing GROUP BY columns
    elif "must appear in the group by clause" in error_msg.lower() or "not in group by" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: GROUP BY Error.
            Possible Causes:
            1. The SELECT list contains non-aggregated columns that are not listed in the GROUP BY clause.
            2. The GROUP BY clause is missing entirely when using aggregate functions (COUNT, SUM, AVG, etc.).
            All non-aggregated columns in SELECT must be in GROUP BY.
        """
    # Syntax error
    elif "syntax error" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: SQL Syntax Error.
            Possible Causes:
            1. Typo in keywords (SELECT, FROM, WHERE, JOIN, ON, GROUP, BY, ORDER).
            2. Missing or extra commas, parentheses, or quotes.
            3. Incorrect use of aliases.
            Review the query structure carefully, comparing against standard SQL syntax and the original Query Plan/Breakdown.
        """
    # Table does not exist
    elif "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: Table Not Found ('relation does not exist').
            Possible Causes:
            1. Typo in table name (check schema, case-sensitive).
            2. Using an alias as if it were a table name in a JOIN condition.
            3. Table truly does not exist in the provided schema.
            Check the original Query Plan/Breakdown and the schema.
        """

    prompt = f"""
        Fix the SQL query based on the error, original plan, and schema. Pay special attention to the hint in the error message if there is one.

        Original question: {question}

        Original Plan:
        {breakdown}

        Failed SQL query:
        ```sql
        {query}
        ```

        Error message:
        {error_msg}

        {specific_guidance}

        Relevant schema:
        {relevant_schema}

        Instructions:
        1. Analyze the Error and Hint.
        2. Compare Failed SQL to the Original Plan and Schema.
        3. Fix ONLY the error, keeping the logic consistent with the Plan.
        4. Ensure correct table/column names (case-sensitive) and aliases.
        5. Output ONLY the corrected SQL query in ```sql markdown tags.

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
