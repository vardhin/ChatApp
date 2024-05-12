import paramiko

def create_reverse_tunnel(remote_host, remote_port, ssh_username, ssh_password, local_port):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(remote_host, username=ssh_username, password=ssh_password)
        transport = ssh.get_transport()
        remote_tunnel = transport.open_reverse_forward_tunnel(('', local_port), ('localhost', remote_port))
        print(f"Reverse tunnel established: {remote_host}:{remote_port} -> localhost:{local_port}")
        return remote_tunnel
    except Exception as e:
        print(f"Failed to establish reverse tunnel: {e}")
        return None

def send_message_through_tunnel(tunnel, message):
    try:
        tunnel.send(message)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Failed to send message through tunnel: {e}")

def menu():
    print("1. Create Reverse Tunnel")
    print("2. Send Message")
    print("3. Exit")

if __name__ == "__main__":
    # Configuration
    remote_host = 'your_friend_ip_address'  # Your friend's server IP address
    remote_port = 22  # SSH port on your friend's server
    ssh_username = 'your_username'  # SSH username on your friend's server
    ssh_password = 'your_password'  # SSH password on your friend's server
    local_port = 5555  # Local port to establish reverse tunnel

    while True:
        menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            tunnel = create_reverse_tunnel(remote_host, remote_port, ssh_username, ssh_password, local_port)
            if tunnel:
                print("Reverse tunnel created successfully!")
            else:
                print("Failed to establish reverse tunnel.")
        elif choice == '2':
            message = input("Enter your message: ")
            if 'tunnel' in locals():
                send_message_through_tunnel(tunnel, message)
            else:
                print("Please create a reverse tunnel first.")
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
