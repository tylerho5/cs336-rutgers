import re

def extract_query_from_text(text):
    """
    extract SQL query from llm output
    """

    pattern = r"```sql\s*([\s\S]*?)\s*```"

    match = re.search(pattern, text)

    return match[1]
