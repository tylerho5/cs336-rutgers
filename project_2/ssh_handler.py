import getpass
import paramiko
import os
import time
from dotenv import load_dotenv

# Global connection cache
_ssh_connections = {}

def get_ssh_credentials():
    '''
    gets user and pwd from .env file or falls back to user input
    '''
    # First try to load from backend directory
    backend_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
    if os.path.exists(backend_env):
        load_dotenv(backend_env)
        print(f"Loading credentials from {backend_env}")
    else:
        # Load environment variables from .env file in project_2 directory
        load_dotenv()
        print("Loading credentials from project_2/.env")
    
    # Get credentials from environment variables
    user = os.getenv('NETID', '')
    pwd = os.getenv('PASSWORD', '')

    # Debug output (mask password)
    if user:
        print(f"Found NETID in environment: {user}")
    if pwd:
        print(f"Found PASSWORD in environment: {'*' * len(pwd)}")

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

def get_ssh_connection(host, user, pwd, max_retries=3):
    """Get or create an SSH connection with retry logic"""
    global _ssh_connections
    
    # Connection key based on host and user
    conn_key = f"{user}@{host}"
    
    # Check if we have an existing connection
    if conn_key in _ssh_connections:
        client = _ssh_connections[conn_key]
        # Test if connection is still active
        try:
            # Transport will be active if the connection is alive
            if client.get_transport() and client.get_transport().is_active():
                print(f"Reusing existing SSH connection to {host}")
                return client
            else:
                print(f"Existing connection is no longer active, creating new one")
                # Close the inactive connection
                try:
                    client.close()
                except:
                    pass
                # Remove from cache
                del _ssh_connections[conn_key]
        except Exception as e:
            print(f"Error checking connection: {e}")
            # Force recreate the connection
            try:
                client.close()
            except:
                pass
            del _ssh_connections[conn_key]
    
    # Retry logic for creating a new connection
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            print(f"Connecting to {host} as {user} (attempt {retries + 1}/{max_retries})...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Increase timeout for slow connections
            client.connect(host, username=user, password=pwd, timeout=15)
            
            print(f"Successfully connected to {host}")
            
            # Store in cache
            _ssh_connections[conn_key] = client
            return client
        except Exception as e:
            last_error = e
            print(f"Connection attempt {retries + 1} failed: {e}")
            retries += 1
            if retries < max_retries:
                # Wait before retrying with increasing backoff
                wait_time = 2 * retries
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
    
    # If we get here, all retries failed
    raise Exception(f"Failed to connect to {host} after {max_retries} attempts: {last_error}")

def execute_query(host, user, pwd, query, wd_path, db_user, db_pwd):
    '''
    connects to iLab and runs iLab script, passing query
    Sets DB_USER and DB_PASSWORD environment variables for the script.
    '''
    ilab_script_path = wd_path + "/ilab_script.py"
    venv_path = wd_path + "/venv"

    try:
        # Get an SSH connection (from pool or create new)
        client = get_ssh_connection(host, user, pwd)

        # Escape single quotes in password just in case
        db_pwd_escaped = db_pwd.replace("'", "'\\''")
        # Set environment variables before executing the script
        command = f"cd {wd_path}; source venv/bin/activate; export DB_USER='{db_user}'; export DB_PASSWORD='{db_pwd_escaped}'; python3 {ilab_script_path} '{query}'"

        print(f"Executing command on {host}...")
        
        # Execute with retry logic
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
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

                print(f"Command executed successfully on {host}")
                return output
                
            except paramiko.SSHException as e:
                print(f"SSH error on attempt {attempt}: {e}")
                if attempt < max_attempts:
                    print(f"Retrying... ({attempt}/{max_attempts})")
                    # Recreate connection
                    client.close()
                    client = get_ssh_connection(host, user, pwd)
                else:
                    raise
    
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
        # We don't close the connection here to allow reuse
        pass

def execute_query_stdin(host, user, pwd, query, wd_path, db_user, db_pwd):
    '''
    connects to iLab and runs iLab script, passing query via stdin (for extra credit)
    Sets DB_USER and DB_PASSWORD environment variables for the script.
    '''
    ilab_script_path = wd_path + "/ilab_script.py"
    venv_path = wd_path + "/venv"

    try:
        # Get an SSH connection (from pool or create new)
        client = get_ssh_connection(host, user, pwd)

        # Escape single quotes in password just in case
        db_pwd_escaped = db_pwd.replace("'", "'\\''")
        # Set environment variables before executing the script
        command = f"cd {wd_path}; source venv/bin/activate; export DB_USER='{db_user}'; export DB_PASSWORD='{db_pwd_escaped}'; python3 {ilab_script_path}"

        print(f"Executing command on {host} with query via stdin...")
        
        # Execute with retry logic
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
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

                print(f"Command executed successfully on {host}")
                return output
                
            except paramiko.SSHException as e:
                print(f"SSH error on attempt {attempt}: {e}")
                if attempt < max_attempts:
                    print(f"Retrying... ({attempt}/{max_attempts})")
                    # Recreate connection
                    client.close()
                    client = get_ssh_connection(host, user, pwd)
                else:
                    raise
    
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
        # We don't close the connection here to allow reuse
        pass

def close_all_connections():
    """Close all SSH connections in the pool"""
    global _ssh_connections
    
    print(f"Closing {len(_ssh_connections)} SSH connections...")
    for key, client in _ssh_connections.items():
        try:
            print(f"Closing connection: {key}")
            client.close()
        except Exception as e:
            print(f"Error closing connection {key}: {e}")
    
    _ssh_connections.clear()
    print("All SSH connections closed")
