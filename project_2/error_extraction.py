import re

def extract_error_from_result(result):
    """Extract the error message from the command output."""
    if result is None:
        return "No results returned from the database."
    
    # Try to locate error messages in the result
    if "error" in result.lower():
        # Look for lines containing common error patterns
        error_lines = []
        hint_lines = []
        for line in result.split('\n'):
            # Extract hints specifically
            if 'hint:' in line.lower():
                hint_lines.append(line.strip())
            # Extract error messages
            elif any(pattern in line.lower() for pattern in ['error', 'exception', 'failed', 'line ']):
                error_lines.append(line.strip())
        
        # Combine error and hint messages
        error_message = '\n'.join(error_lines)
        if hint_lines:
            error_message += '\n\nHints:\n' + '\n'.join(hint_lines)
        
        if error_message:
            return error_message
    
    return "Unknown error occurred while executing the query."

# Removed extract_relevant_schema function 