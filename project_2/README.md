# CS336 Project 2: Natural Language Database Interface

This project implements an advanced natural language interface to a PostgreSQL database using a local LLM (Phi-3.5-mini & sqlcoder-7b-2). Users can ask questions in plain English, and the system will generate SQL queries, execute them on the database, and return formatted results.

## Video

The link below is for a video with a demonstration of installing and running the project with a brief explanation of the architecture of the whole program.

https://youtu.be/Ap7C1AZB4dM


## Team Members and Contributions
| Name | NetID | Contributions |
|------|-------|---------------|
| Rohan Sharma | rs2563 | Two model pipeline implementation; error checking loop; SSH tunneling; logging llm interaction |
| Daneliz Urena | dlu8 | Regex expression development to refine RA and SQL query extraction; error extraction |
| Tyler Ho | tjh195 | Initial Phi model implementatio; database connection; query extraction; logging llm interaction |
| Robin Del Rosario | rhd41 | Prompt optimization; documentation |

## What Was Challenging
* Using a small LLM (Phi-3.5-mini) to generate complex SQL queries
* Getting consistent, valid SQL queries from the LLM for a complex schema
* Implementing robust error detection and correction feedback loop
* Configuring SSH tunneling with secure credential management
* Optimizing prompts for improved SQL accuracy

## What Was Interesting

* Creating a self-correcting system that handles its own errors
* How prompt engineering significantly impacts query quality
* Building an end-to-end system connecting natural language to database results

## Key Features

### Dual LLM Architecture
Our system uniquely leverages two different LLMs, each optimized for specific tasks:
- **Phi-3.5-mini** (2GB): Handles the initial relational algebra breakdown of natural language queries
- **defog/sqlcoder-7b-2** (4GB): Specializes in SQL generation from the algebra expression

Only one model is loaded at a time to stay under the 4GB VRAM requirement, with efficient model swapping handled by our LLM manager. This dual-model approach provides better results than using a single model for both tasks.

### Relational Algebra Breakdown
We implemented a two-stage query processing pipeline:
1. First, natural language is converted to a formal relational algebra expression (π, σ, ⋈, γ, etc.)
2. This algebra expression serves as an intermediate representation that bridges natural language and SQL
3. The structured algebra makes complex queries more consistent and reliable

This approach significantly improves query accuracy by breaking down complex natural language understanding into discrete, well-defined steps.

### Error Feedback Loop with Specific Guidance
Our error correction system goes beyond basic retry mechanisms:
1. When SQL errors occur, we analyze the specific error type (column not found, missing JOIN, etc.)
2. We generate targeted guidance with explicit examples for that particular error type
3. The system provides specialized handling for junction tables (e.g., DenialReasons)
4. The error correction prompt includes the original relational algebra to maintain query intent

This targeted approach results in much higher success rates for error correction compared to generic retries.

## Extra Credit
**YES** - We implemented the extra credit feature to allow the ilab_script.py to accept input from stdin when no command-line arguments are provided, and adjusted the SSH tunnel to pass queries via stdin as well.

## Setup and Running

### Setup
```bash
git clone https://github.com/tylerho5/cs336-rutgers.git
cd ./cs336-rutgers/project_2
python3 -m venv CS336P2
source CS336P2/bin/activate
pip install -r dependencies/requirements.txt
mkdir -p model
curl -L -o model/sqlcoder-7b-q5_k_m.gguf "https://huggingface.co/defog/sqlcoder-7b-2/resolve/main/sqlcoder-7b-q5_k_m.gguf?download=true"
curl -L -o model/Phi-3.5-mini-instruct-Q4_K_M.gguf "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf?download=true"
```

### Running the Program

```bash
KMP_DUPLICATE_LIB_OK=TRUE python3 database_llm.py
```

OR

```bash
python project_2/runner_script.py
```

### Environment Configuration
Create a `.env` file with the following to avoid retyping constantly:
```
NETID=ILAB_NETID
PASSWORD=ILAB_NETID_PASSWORD
DB_NAME=DB_NAME_USUALLY_JUST_NET_ID
DB_USER=DB_USERNAME_USUALLY_JUST_NET_ID
``` 

## AI/LLM Usage
We used ChatGPT and Gemini to explain how to work with the packages we used: paramiko, psycopg2, llama-cpp-python, contextlib, subprocess, etc.

We also used ChatGPT to help refine our regex expressions for capturing the relational algebra and SQL statements from the LLM output.

We did not realize that we needed to save the chat transcripts from this project and they have unfortunately mostly been deleted.

Here are a couple chat transcripts that were not removed:

https://chatgpt.com/share/68197f64-6290-8001-8ed8-0cc012ba753d

https://chatgpt.com/share/68197f46-93a8-8001-9f3c-6e67bfa84f33

https://aistudio.google.com/app/prompts/1m3SFrwMr9rhi_4HoWxN5Lv_iU5DdXgvd