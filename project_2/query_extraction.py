import re

def extract_query_from_text(text):
    """
    Extract SQL query from LLM output.
    
    This function looks for SQL code blocks in markdown format:
    ```sql
    SELECT * FROM table
    ```
    
    If none is found, it tries other patterns like SQL: prefixes.
    
    Args:
        text (str): The LLM response text
        
    Returns:
        str: The extracted SQL query
        
    Raises:
        ValueError: If no SQL query could be extracted
    """
    # Try to find SQL in code blocks with ```sql
    pattern = r"\`\`\`sql\s*([\s\S]*?)\s*\`\`\`"
    match = re.search(pattern, text)
    
    if match:
        return match.group(1).strip()
    
    # If no code blocks found, try to find SQL: prefix
    pattern = r"SQL:\s*([\s\S]*?)(?:\n\n|\Z)"
    match = re.search(pattern, text)
    
    if match:
        return match.group(1).strip()
    
    # If still no match, look for SELECT statements
    pattern = r"(SELECT[\s\S]*?;)"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # If we got here, no SQL query was found
    raise ValueError("Could not extract SQL query from LLM response.")


