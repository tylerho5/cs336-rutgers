import contextlib
import os
from pathlib import Path

from llama_cpp import Llama

def load_schema():
    '''
    load database schema from cut-down project_1 sql file
    '''
    
    context = ""

    with open("project_2/schema_context.sql", "r") as f:
        context = f.read()

    return context

def build_prompt(context, question):
    '''
    build prompt for LLM
    '''

    prompt = f"""
    You are a SQL expert. You will be given a SQL database schema and a question.
    Your task is to generate a SQL query that answers the question based on the schema.
    The schema is as follows:
    {context}
    The question is as follows:
    {question}
    Your response should only include the SQL query, without any additional text or explanation.
    """

    return prompt

def query_llm(llm, prompt):
    '''
    query the LLM with the given prompt
    '''

    # use create_chat_completion for instruction-tuned models
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200
    )
    
    return output['choices'][0]['message']['content']

def initalize_llm(model_name):
    '''
    Initialize the local LLM model
    '''

    # construct the absolute path to the model file relative to this script
    script_dir = Path(__file__).parent
    model_file_path = script_dir / 'model' / model_name

    # Suppress stderr during Llama initialization
    with open(os.devnull, 'w') as f, contextlib.redirect_stderr(f):
        llm = Llama(
            model_path=str(model_file_path), # may not need to cast to str
            n_gpu_layers=-1,
            seed=1337,
            n_ctx=3072,
            verbose=False  # keep this to disable other logs
        )

    return llm