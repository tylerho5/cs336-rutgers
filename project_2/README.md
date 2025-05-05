# CS336 Project 2: Natural Language Database Interface

This project implements an advanced natural language interface to a PostgreSQL database using a local LLM (Phi-3.5-mini). Users can ask questions in plain English, and the system will generate SQL queries, execute them on the database, and return formatted results. The implementation features an intelligent error correction system that can automatically fix SQL errors through an LLM feedback loop, comprehensive schema understanding including junction table relationships, and a versatile design that works with any database schema through a simple configuration file.

## Team Members and Contributions

| Name | NetID | Contributions |
|------|-------|---------------|
| [Name 1] | [NetID 1] | [Description of contributions] |
| [Name 2] | [NetID 2] | [Description of contributions] |
| [Name 3] | [NetID 3] | [Description of contributions] |

## What Was Challenging

* Ensuring the LLM generates valid SQL queries consistently for a complex database schema
* Handling the mapping between natural language entities and database schema constructs
* Implementing a robust error detection and correction system for SQL queries
* Working with junction tables and properly communicating their use to the LLM
* Configuring the SSH tunnel to work reliably with database credentials
* Fine-tuning prompts to improve SQL accuracy without making them overly specific
* Setting up a proper environment for running the local LLM with appropriate parameters

## What Was Interesting

* Seeing how a relatively small LLM model (Phi-3.5-mini) can generate complex SQL queries
* Developing an error feedback loop that allows the LLM to correct its own mistakes
* Learning how prompt engineering significantly impacts query generation quality
* Creating a system that provides specific guidance based on error type analysis
* Exploring the balance between generic prompting and schema-specific guidance
* Understanding how junction tables are used in SQL and communicating this to the LLM
* Building a complete end-to-end system that connects natural language to database results

## Key Features

### Error Feedback Loop
Our system implements an advanced error feedback loop that can automatically fix SQL errors:

1. When a generated SQL query fails, the system:
   - Extracts the specific error message from the database
   - Identifies the relevant tables from the query for context
   - Provides targeted guidance based on the error type (column not found, join issues, etc.)
   - Asks the LLM to fix the query with specific instructions
   - Tries the corrected query

2. The system will attempt up to 3 correction cycles before giving up, providing helpful error messages to the user.

3. Error-specific guidance is provided for common SQL errors:
   - Column does not exist errors
   - Missing JOIN conditions
   - Ambiguous column references
   - Missing GROUP BY columns
   - Syntax errors
   - Table name errors

### Versatile Database Design

A key design principle of this project is its ability to work with **any** database schema with minimal modification. The system is completely generic and adaptable:

- **Schema-agnostic design**: Nothing in the code is hardcoded to the specific HMDA mortgage database
- **Centralized schema definition**: All database knowledge is contained in a single `schema_context.txt` file
- **Plug-and-play adaptability**: To use with a different database, simply replace the schema context file
- **Generic error correction**: All error guidance uses generic table/column examples, not specific to any schema
- **Universal SQL patterns**: The system focuses on general SQL concepts like junction tables and lookups

This versatile approach means the natural language interface can be quickly adapted to any PostgreSQL database without changing the core code. This makes it a reusable tool rather than a single-purpose project.


### Improved Context Management
The system includes:
- A clear, structured schema representation that highlights relationships
- Special handling for junction tables and many-to-many relationships
- Smart extraction of relevant schema portions for error correction

### Other Enhancements
- Comprehensive logging of queries, errors, and correction attempts
- Clear user feedback during error resolution
- Improved SSH handling with better error messages

## Extra Credit

**YES** - We implemented the extra credit feature to make the ilab_script.py accept input from stdin when no command-line arguments are provided, and adjusted the SSH tunnel to pass queries via stdin as well. This is controlled by the `use_stdin` flag in database_llm.py, which is set to True by default.

## How to Run the Project

### Prerequisites

1. Install required packages:
   ```
   conda env create -f environment.yml
   conda activate cs336-project2
   ```

2. Download the LLM model:
   - Download the Phi-3.5-mini-instruct-Q4_K_M.gguf model from Hugging Face
   - Place it in the `project_2/model/` directory

### Running the Program

On Windows:
```
set KMP_DUPLICATE_LIB_OK=TRUE 
python project_2\database_llm.py
```

On macOS/Linux:
```
KMP_DUPLICATE_LIB_OK=TRUE python project_2/database_llm.py
```

## Example Queries

Here are some example questions you can ask the system:

1. "How many mortgages have a loan value greater than the applicant income?"
2. "What is the average income of owner occupied applications?"
3. "What is the most common loan denial reason?" 