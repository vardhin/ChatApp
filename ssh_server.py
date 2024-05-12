import paramiko
import threading

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Add your authentication logic here
        # For demonstration purposes, we'll authenticate any user with any password
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def run(self, client_address):
        transport = paramiko.Transport(client_address)
        transport.add_server_key(paramiko.RSAKey.generate(1024))
        transport.set_subsystem_handler('', paramiko.DummyChannel)
        server = SSHServer()
        transport.start_server(server=server)

        server.event.wait()

        transport.close()

if __name__ == "__main__":
    host_key = paramiko.RSAKey.generate(1024)
    server = '0.0.0.0'  # Listen on all interfaces
    port = 2222  # Custom SSH port

    print(f"[*] Listening for connections on {server}:{port}...")

    try:
        ssh_server = SSHServer()
        ssh_server.run((server, port))
    except Exception as e:
        print(f"[-] Error: {e}")
