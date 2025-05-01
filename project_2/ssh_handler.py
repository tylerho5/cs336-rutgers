import getpass
import paramiko

def get_ssh_credentials():
    '''
    gets user, host, and pwd (securely)
    '''

    host = input("Enter iLab hostname: ")

    user = input("Enter NetID: ")

    pwd = getpass.getpass(f"Enter pwd for {user}@{host}: ")

    return host, user, pwd

def execute_query(host, user, pwd, query, ilab_script_path):
    '''
    connects to iLab and runs iLab script, passing query
    '''

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=pwd, timeout=10)

        command = f"python3 {ilab_script_path} '{query}'"

        stdin, stdout, stderr = client.exec_command(command, timeout=60)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"Command error:\n{error}")

        return output
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Check user and password.")
        return None
    except paramiko.SSHException as sshException:
        print(f"Unable to establish connection: {sshException}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    finally:
        if client:
            client.close()

def execute_query_stdin(host, user, pwd, query, ilab_script_path):
    '''
    connects to iLab and runs iLab script, passing query via stdin (for extra credit)
    '''

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=pwd, timeout=10)

        command = f"python3 {ilab_script_path}"

        stdin, stdout, stderr = client.exec_command(command, timeout=60)
        
        # Write query to stdin and flush
        stdin.write(query)
        stdin.flush()
        stdin.channel.shutdown_write()  # Signal EOF
        
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"Command error:\n{error}")

        return output
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Check user and password.")
        return None
    except paramiko.SSHException as sshException:
        print(f"Unable to establish connection: {sshException}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    finally:
        if client:
            client.close()
