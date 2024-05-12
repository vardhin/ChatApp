import paramiko

def send_message(ssh_client, message):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f"echo '{message}'")
        print("Message sent successfully!")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__ == "__main__":
    host = 'your_server_ip'  # SSH server IP address
    port = 2222  # Custom SSH port
    username = 'your_username'  # SSH username
    password = 'your_password'  # SSH password

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, port=port, username=username, password=password)

        message = input("Enter your message: ")
        send_message(ssh_client, message)

        ssh_client.close()
    except Exception as e:
        print(f"[-] Error: {e}")
