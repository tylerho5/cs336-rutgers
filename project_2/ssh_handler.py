import getpass
import paramiko
import os
from dotenv import load_dotenv

def get_ssh_credentials():
    '''
    gets user and pwd from .env file or falls back to user input
    '''
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    user = os.getenv('NETID', '')
    pwd = os.getenv('PASSWORD', '')

    # Return credentials from .env if both exist and are not empty
    if user and pwd:
        print("\nCredentials found in environment variables.")
        return user, pwd
    
    print("\nPlease enter your iLab credentials")
    # Fall back to interactive input if not found in .env or empty
    if not user:
        user = input("Enter NetID: ")
    
    if not pwd:
        pwd = getpass.getpass(f"Enter password for {user}@ilab.cs.rutgers.edu: ")

    return user, pwd

def execute_query(host, user, pwd, query, wd_path, db_user, db_pwd):
    '''
    connects to iLab and runs iLab script, passing query
    Sets DB_USER and DB_PASSWORD environment variables for the script.
    '''

    ilab_script_path = wd_path + "/ilab_script.py"

    venv_path = wd_path + "/venv"

    client = paramiko.SSHClient()
    # Use AutoAddPolicy for convenience if host keys change or are new
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 

    try:
        client.connect(host, username=user, password=pwd, timeout=10)

        # Escape single quotes in password just in case
        db_pwd_escaped = db_pwd.replace("'", "'\\''")
        # Set environment variables before executing the script
        command = f"cd {wd_path}; source venv/bin/activate; export DB_USER='{db_user}'; export DB_PASSWORD='{db_pwd_escaped}'; python3 {ilab_script_path} '{query}'"

        stdin, stdout, stderr = client.exec_command(command, timeout=300)
        
        # Wait for the command to complete and get the exit status
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        # Check exit status first
        if exit_status != 0:
            print(f"Remote command failed with exit status {exit_status}")
            if error:
                print(f"Command error output:\n{error}")
            # Return error rather than None for better error handling
            return f"Error executing query. Exit status: {exit_status}\nCommand error output:\n{error}"

        return output
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Check user and password.")
        return "Error: Authentication failed. Check your username and password."
    except paramiko.SSHException as sshException:
        print(f"Unable to establish connection: {sshException}")
        return f"Error: Unable to establish SSH connection: {sshException}"
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error: {e}"
    
    finally:
        if client:
            client.close()

def execute_query_stdin(host, user, pwd, query, wd_path, db_user, db_pwd):
    '''
    connects to iLab and runs iLab script, passing query via stdin (for extra credit)
    Sets DB_USER and DB_PASSWORD environment variables for the script.
    '''

    ilab_script_path = wd_path + "/ilab_script.py"

    venv_path = wd_path + "/venv"

    client = paramiko.SSHClient()
    # Use AutoAddPolicy for convenience if host keys change or are new
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=pwd, timeout=10)

        # Escape single quotes in password just in case
        db_pwd_escaped = db_pwd.replace("'", "'\\''")
        # Set environment variables before executing the script
        # Corrected command to execute the script file, not the directory
        command = f"cd {wd_path}; source venv/bin/activate; export DB_USER='{db_user}'; export DB_PASSWORD='{db_pwd_escaped}'; python3 {ilab_script_path}"

        stdin, stdout, stderr = client.exec_command(command, timeout=300)
        
        # Write query to stdin and flush
        stdin.write(query)
        stdin.flush()
        stdin.channel.shutdown_write()  # Signal EOF
        
        # Wait for the command to complete and get the exit status
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        # Check exit status first
        if exit_status != 0:
            print(f"Remote command failed with exit status {exit_status}")
            if error:
                print(f"Command error output:\n{error}")
            # Return error rather than None for better error handling
            return f"Error executing query. Exit status: {exit_status}\nCommand error output:\n{error}"

        return output
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Check user and password.")
        return "Error: Authentication failed. Check your username and password."
    except paramiko.SSHException as sshException:
        print(f"Unable to establish connection: {sshException}")
        return f"Error: Unable to establish SSH connection: {sshException}"
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error: {e}"
    
    finally:
        if client:
            client.close()
