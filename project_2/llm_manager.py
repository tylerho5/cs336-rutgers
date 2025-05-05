import contextlib
import os
from pathlib import Path
import gc

from llama_cpp import Llama

# Model paths
BREAKDOWN_MODEL = "Phi-3.5-mini-instruct-Q4_K_M.gguf"
SQL_MODEL = "sqlcoder-7b-q5_k_m.gguf"

# Global variables to track loaded models
current_model = None
current_llm = None

def load_schema():
    '''
    load database schema from cut-down project_1 sql file
    '''
    
    context = ""

    with open("project_2/schema_context.sql", "r") as f:
        context = f.read()

    return context

def ensure_model_loaded(model_name):
    '''
    Ensure the specified model is loaded, unloading the current model if necessary.
    '''
    global current_model, current_llm
    
    # If the requested model is already loaded, return it
    if current_model == model_name and current_llm is not None:
        return current_llm
    
    # Unload current model if it exists
    if current_llm is not None:
        del current_llm
        current_llm = None
        current_model = None
        gc.collect()  # Force garbage collection
    
    # Load the new model
    script_dir = Path(__file__).parent
    model_file_path = script_dir / 'model' / model_name

    # suppress stderr during Llama initialization
    with open(os.devnull, 'w') as f, contextlib.redirect_stderr(f):
        try:
            llm = Llama(
                model_path=str(model_file_path),
                n_gpu_layers=-1,
                seed=1337,
                n_ctx=4096,
                verbose=False
            )
            current_llm = llm
            current_model = model_name
            return llm
        except Exception as e:
            print(f"Error loading LLM: {e}")
            print("Consider checking model path...")
            quit()

def build_breakdown_prompt(context, question):
    """
    build a prompt for LLM to generate relational algebra expressions
    """
    prompt = f"""
        Instructions:
        Create a step-by-step relational algebra expression for the query based on the User Question and Schema.
        Use standard relational algebra notation:
        - σ for selection (WHERE conditions)
        - π for projection (SELECT columns)
        - ⋈ for natural join
        - ⋈θ for theta join (with conditions)
        - ∪ for union
        - ∩ for intersection
        - - for set difference
        - γ for grouping/aggregation
        - τ for sorting
        - ρ for renaming

        Example format:
        π column1, column2 (σ condition (Table1 ⋈ Table2))

        Output only the relational algebra expression, no SQL, no explanations. Be as concise as possible.

        User Question: {question}

        Schema:
        {context}

        Relational Algebra:
    """
    return prompt

def build_sql_from_breakdown_prompt(breakdown, context, question):
    '''
    build prompt for LLM to generate SQL from a relational algebra expression
    '''
    specific_guidance = ""
    
    # Add special guidance for DenialReasons queries
    if "denial" in question.lower() or "denialreasons" in breakdown.lower():
        specific_guidance = """
            IMPORTANT - For DenialReasons queries:
            1. DenialReasons (drs) is a junction table - it does NOT have denial_reason_name
            2. DenialReason (dr) is the lookup table - it HAS denial_reason_name
            3. You MUST use these exact aliases and join:
               ```sql
               SELECT dr.denial_reason_name, COUNT(*) 
               FROM DenialReasons drs 
               JOIN DenialReason dr ON drs.denial_reason_code = dr.denial_reason_code
               GROUP BY dr.denial_reason_name
               ORDER BY COUNT(*) DESC
               ```
            4. NEVER try to get denial_reason_name from DenialReasons table
        """

    prompt = f"""
        Instructions:
        1. View the relational‑algebra expression as a roadmap to the tables, joins, filters, and columns you need. It is a guide, not a rulebook.
        2. Write one valid PostgreSQL query that answers the question. Add aggregates when the question requires them, even if they were not shown in the algebra.
        3. Use fully qualified column names (alias.column) everywhere and pick clear, short aliases.
        4. Match table and column names exactly (case‑sensitive).
        5. Output **only** the SQL, wrapped in ```sql markdown tags.

        {specific_guidance}

        Original Question: {question}

        Relational Algebra Expression:
        {breakdown}

        Schema:
        {context}

        SQL Query:
    """
    return prompt

def build_correction_prompt(question, query, error_msg, full_schema, breakdown):
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
            3. Trying to access a descriptive field (e.g., `denial_reason_name`) from a junction table (e.g., `DenialReasons`) instead of the lookup table (e.g., `DenialReason`). You MUST join to the lookup table.
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
            3. For junction tables (like DenialReasons), you need to join:
               - First table to junction table (e.g., LoanApplication.ID = DenialReasons.ID)
               - Junction table to lookup table (e.g., DenialReasons.denial_reason_code = DenialReason.denial_reason_code)
            Check the original Query Plan/Breakdown for intended JOINs.
        """
    # Ambiguous column reference
    elif "ambiguous" in error_msg.lower() and "column" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: Ambiguous Column Reference.
            Possible Causes:
            1. A column name exists in multiple tables in the FROM/JOIN clauses, and it wasn't qualified with a table alias (e.g., `alias.column`).
            2. An alias was forgotten or used inconsistently.
            3. When using junction tables, make sure to properly alias all tables and qualify column references.
            Always use table aliases and qualify all columns when multiple tables are joined.
        """
    # Missing GROUP BY columns
    elif "must appear in the group by clause" in error_msg.lower() or "not in group by" in error_msg.lower():
        specific_guidance = """
            Error Type Hint: GROUP BY Error.
            Possible Causes:
            1. The SELECT list contains non-aggregated columns that are not listed in the GROUP BY clause.
            2. The GROUP BY clause is missing entirely when using aggregate functions (COUNT, SUM, AVG, etc.).
            3. When working with junction tables, make sure to include the correct columns from the lookup table in GROUP BY.
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
            4. For junction tables, ensure proper JOIN syntax with ON conditions.
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
            4. For junction tables, make sure to include both the junction table and its lookup table.
            Check the original Query Plan/Breakdown and the schema.
        """

        
    # Add to error correction prompt if it's a DenialReasons query
    if "denial" in question.lower() or "denialreasons" in query.lower():
        specific_guidance += """
            IMPORTANT - For DenialReasons queries:
            1. DenialReasons (drs) is a junction table - it does NOT have denial_reason_name
            2. DenialReason (dr) is the lookup table - it HAS denial_reason_name
            3. You MUST use these exact aliases and join:
               ```sql
               SELECT dr.denial_reason_name, COUNT(*) 
               FROM DenialReasons drs 
               JOIN DenialReason dr ON drs.denial_reason_code = dr.denial_reason_code
               GROUP BY dr.denial_reason_name
               ORDER BY COUNT(*) DESC
               ```
            4. NEVER try to get denial_reason_name from DenialReasons table
        """

    prompt = f"""
        Fix the SQL query based on the error, original plan, and schema. Pay special attention to the hint in the error message if there is one.

        {specific_guidance}

        Instructions:
        1. Fix the SQL query based on the error message and hints.
        2. Compare Failed SQL to the Original Plan and Schema.
        3. Ensure all necessary tables are properly joined, especially for junction tables.
        4. Use proper table aliases and qualify all column references.
        5. Maintain the original query's intent as shown in the plan.
        6. Output only the corrected SQL query, no explanations.

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

        Full Database Schema:
        {full_schema}


        Corrected SQL query:
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

def get_breakdown_llm():
    '''
    Get the LLM instance for generating breakdowns
    '''
    return ensure_model_loaded(BREAKDOWN_MODEL)

def get_sql_llm():
    '''
    Get the LLM instance for generating SQL
    '''
    return ensure_model_loaded(SQL_MODEL)
