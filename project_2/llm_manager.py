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

def build_correction_prompt(question, query, error_msg, relevant_schema):
    '''
    build prompt for LLM to correct a SQL query that produced an error
    
    Args:
        question (str): Original user question
        query (str): Failed SQL query
        error_msg (str): Error message from database
        relevant_schema (str): Relevant portion of the schema
        
    Returns:
        str: Prompt for LLM to correct the query
    '''
    
    # Add specific guidance based on error patterns
    specific_guidance = ""
    
    # Column does not exist error
    if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
        specific_guidance = """
        This is a column name error. Check:
        1. The column might be in a different table than you think
        2. For many-to-many relationships, you must join to the lookup table to get descriptive fields
        3. Junction tables (with names ending in 's') typically only contain foreign keys, not descriptive names
        4. Lookup tables (without 's') contain the actual descriptive names
        
        Example fix for column name error:
        INCORRECT: SELECT J.description FROM JunctionTable J
        CORRECT:   SELECT L.description FROM JunctionTable J JOIN LookupTable L ON J.lookup_id = L.id
        """
    # Missing JOIN condition
    elif "cross join" in error_msg.lower() or "missing join condition" in error_msg.lower():
        specific_guidance = """
        This is a JOIN condition error. Check:
        1. Every JOIN must have an ON clause with proper conditions
        2. Make sure foreign keys match between tables
        3. Verify the join fields exist in both tables
        
        Example fix for missing JOIN condition:
        INCORRECT: SELECT * FROM TableA JOIN TableB
        CORRECT:   SELECT * FROM TableA A JOIN TableB B ON A.id = B.table_a_id
        """
    # Ambiguous column reference
    elif "ambiguous" in error_msg.lower() and "column" in error_msg.lower():
        specific_guidance = """
        This is an ambiguous column reference error. Check:
        1. Always qualify column names with table aliases when multiple tables are involved
        2. The same column name might exist in multiple joined tables
        
        Example fix for ambiguous column:
        INCORRECT: SELECT id, code FROM JunctionTable JOIN LookupTable
        CORRECT:   SELECT J.id, J.code FROM JunctionTable J JOIN LookupTable L ON J.code = L.code
        """
    # Missing GROUP BY columns
    elif "must appear in the group by clause" in error_msg.lower() or "not in group by" in error_msg.lower():
        specific_guidance = """
        This is a GROUP BY error. Check:
        1. All non-aggregated columns in the SELECT clause must also appear in the GROUP BY clause
        2. You can't mix aggregated and non-aggregated columns without using GROUP BY
        
        Example fix for GROUP BY:
        INCORRECT: SELECT category_name, COUNT(*) FROM Categories JOIN Items GROUP BY category_id
        CORRECT:   SELECT category_name, COUNT(*) FROM Categories JOIN Items GROUP BY category_name
        """
    # Syntax error
    elif "syntax error" in error_msg.lower():
        specific_guidance = """
        This is a syntax error. Check:
        1. Look for missing commas between columns
        2. Check for missing parentheses or mismatched quotes
        3. Verify SQL keywords are properly spaced
        4. Make sure table aliases are consistent throughout the query
        
        Example of common syntax fixes:
        INCORRECT: SELECT column1 column2 FROM table
        CORRECT:   SELECT column1, column2 FROM table
        
        INCORRECT: SELECT COUNT(*) as count items FROM table
        CORRECT:   SELECT COUNT(*) as count_items FROM table
        """
    # Table does not exist
    elif "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
        specific_guidance = """
        This is a table name error. Check:
        1. Verify the table name is spelled correctly
        2. Check the case of the table name (PostgreSQL is case-sensitive)
        3. Make sure you're not using an alias as if it were a table name
        4. Confirm the table name exists in the schema
        
        Example fix for table name:
        INCORRECT: SELECT * FROM items
        CORRECT:   SELECT * FROM Items
        """
    
    prompt = f"""
        I need to fix a SQL query that failed.
        
        Original question: {question}
        
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
        1. Analyze the error message carefully
        2. Identify the specific issue in the query
        3. Fix ONLY what's needed to address the error
        4. Remember:
           - Junction tables (often with names ending in 's') typically contain ONLY foreign keys, not descriptive fields
           - Lookup tables contain the descriptive fields (names, descriptions)
           - To get descriptive names from a many-to-many relationship, you MUST join both tables
        5. Use appropriate table aliases (e.g., meaningful short abbreviations)
        6. Ensure all column and table names match the schema exactly
        7. Provide the corrected query ONLY
        8. Enclose the fixed query in ```sql markdown tags
        
        REMEMBER: If you need a descriptive name, you MUST join to the lookup table.
        
        Please provide a corrected SQL query that resolves this error.
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
                    "content": "You are an expert PostgreSQL assistant. Your task is to generate or fix SQL queries based on database schemas. You provide only the SQL query without explanation unless specifically asked. Always ensure column and table names match the schema exactly."
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
