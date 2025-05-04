import re

def extract_error_from_result(result):
    """Extract the error message from the command output."""
    if result is None:
        return "No results returned from the database."
    
    # Try to locate error messages in the result
    if "error" in result.lower():
        # Look for lines containing common error patterns
        error_lines = []
        for line in result.split('\n'):
            if any(pattern in line.lower() for pattern in ['error', 'exception', 'failed', 'hint:', 'line ']):
                error_lines.append(line)
        
        if error_lines:
            return '\n'.join(error_lines)
    
    return "Unknown error occurred while executing the query."

def extract_relevant_schema(query, full_schema):
    """Extract only the schema portions relevant to the query with relationships highlighted."""
    # Extract table names from the query
    table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    tables = re.findall(table_pattern, query, re.IGNORECASE)
    
    # Also look for table aliases
    alias_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)'
    aliases = re.findall(alias_pattern, query, re.IGNORECASE)
    
    # Combine tables from both patterns
    all_tables = set(tables)
    table_aliases = {}
    for table, alias in aliases:
        all_tables.add(table)
        table_aliases[alias] = table
    
    # For junction tables, add their related lookup tables
    related_tables = set()
    for table in all_tables.copy():
        # Check if it might be a junction table (ends with 's')
        if table.endswith('s') and table[:-1] in full_schema:
            related_tables.add(table[:-1])
        # Check for common patterns in our schema
        if table == 'DenialReasons':
            related_tables.add('DenialReason')
        elif table == 'ApplicantRace':
            related_tables.add('Race')
        elif table == 'CoApplicantRace':
            related_tables.add('Race')
    
    all_tables.update(related_tables)
    
    # Also look for column names in the query that might indicate tables
    col_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.[a-zA-Z_][a-zA-Z0-9_]*\b'
    col_tables = re.findall(col_pattern, query, re.IGNORECASE)
    
    # Add actual table names for any aliases found
    for alias in col_tables:
        if alias in table_aliases:
            all_tables.add(table_aliases[alias])
    
    # Get schema lines related to these tables
    relevant_lines = []
    schema_sections = {}
    current_section = ""
    
    # First, find and extract all relevant sections
    for line in full_schema.split('\n'):
        # Check if this line starts a new table definition
        table_match = re.search(r'\*\*([a-zA-Z_][a-zA-Z0-9_]*)', line)
        if table_match:
            current_section = table_match.group(1)
            if current_section in all_tables:
                schema_sections[current_section] = []
                schema_sections[current_section].append(line)
        elif current_section in all_tables:
            schema_sections[current_section].append(line)
    
    # If no specific tables were found, return the full schema
    if not schema_sections:
        return full_schema
    
    # Create an enhanced output with relationship notes
    enhanced_output = ["Schema for tables involved in the query:"]
    
    # Add junction table relationship notes
    if "DenialReasons" in schema_sections and "DenialReason" in schema_sections:
        enhanced_output.append("\n===== IMPORTANT RELATIONSHIP =====")
        enhanced_output.append("DenialReasons is a JUNCTION table connecting LoanApplication to DenialReason.")
        enhanced_output.append("- DenialReasons contains: ID, reason_number, denial_reason_code")
        enhanced_output.append("- DenialReason contains: denial_reason_code, denial_reason_name")
        enhanced_output.append("To get denial_reason_name, you MUST join DenialReasons to DenialReason using denial_reason_code.")
        enhanced_output.append("===================================\n")
    
    if "ApplicantRace" in schema_sections and "Race" in schema_sections:
        enhanced_output.append("\n===== IMPORTANT RELATIONSHIP =====")
        enhanced_output.append("ApplicantRace is a JUNCTION table connecting LoanApplication to Race.")
        enhanced_output.append("- ApplicantRace contains: ID, race_number, race_code")
        enhanced_output.append("- Race contains: race_code, race_name")
        enhanced_output.append("To get race_name, you MUST join ApplicantRace to Race using race_code.")
        enhanced_output.append("===================================\n")
    
    # Add the schema sections
    for table, lines in schema_sections.items():
        enhanced_output.append("\n".join(lines))
        enhanced_output.append("")  # Blank line
    
    return "\n".join(enhanced_output) 