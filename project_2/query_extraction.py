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

def extract_relational_algebra(text):
    """
    Extract relational algebra expression from LLM output.
    
    This function looks for relational algebra expressions in the text.
    It expects expressions using standard relational algebra notation.
    
    Args:
        text (str): The LLM response text
        
    Returns:
        str: The extracted relational algebra expression
        
    Raises:
        ValueError: If no relational algebra expression could be extracted
    """
    # Common relational algebra operators
    operators = r'[πσ⋈∪∩\-γτρ]'
    
    # Pattern to match relational algebra expressions
    # This looks for expressions containing relational algebra operators
    # with proper nesting of parentheses and operators
    pattern = rf"""
        # Match the start of a relational algebra expression
        ^\s*{operators}.*?\(
        # Match any number of nested expressions or simple terms
        (?:
            [^()]*  # Non-parentheses characters
            |
            \( [^()]* \)  # Simple parenthesized expressions
        )*
        \)  # Closing parenthesis
    """
    
    # Compile with verbose flag and ignore case
    regex = re.compile(pattern, re.VERBOSE | re.IGNORECASE)
    
    # First try to find after "Relational Algebra Expression:" marker
    marker_pattern = r"Relational Algebra Expression:\s*([\s\S]*?)(?:\n\n|\Z)"
    marker_match = re.search(marker_pattern, text)
    
    if marker_match:
        # If found after marker, try to extract the expression
        potential_expr = marker_match.group(1).strip()
        match = regex.search(potential_expr)
        if match:
            return match.group(0).strip()
    
    # If no match found after marker, try the whole text
    match = regex.search(text)
    if match:
        return match.group(0).strip()
    
    # If we got here, no valid relational algebra expression was found
    raise ValueError("Could not extract valid relational algebra expression from LLM response.")
