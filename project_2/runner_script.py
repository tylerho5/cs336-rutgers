import os
import platform
import subprocess
import sys
 
# set script path relative to the root directory
script_path = os.path.join("project_2", "database_llm.py")

# check if script exists
if not os.path.exists(script_path):
    print(f"Error: Script not found at '{script_path}'.")
    quit()

# prep environment variables
env = os.environ.copy()
env["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# prep Processing your question
command = [sys.executable, script_path]

current_platform = platform.system()

try:
    process = subprocess.run(command, env=env, check=True, text=True)

except Exception as e:
    print(f"Error occurred: {e}")