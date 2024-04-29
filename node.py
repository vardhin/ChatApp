from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic

class ChatProtocol(basic.LineReceiver):
    """
    Protocol for handling communication between the server and clients.
    """

    def __init__(self, factory):
        """
        Initialize the protocol with a reference to its factory.

        Args:
            factory (ChatFactory): The factory creating this protocol instance.
        """
        self.factory = factory
        self.client_id = id(self)  # Assign a unique client ID to each client
        
    def get_id(self):
        return self.client_id

    def connectionMade(self):
        """
        Called when a new client connection is established.
        Prints client and server information, assigns a client ID, and adds the client to the list of connected clients.
        """
        peer = self.transport.getPeer()
        print(f"Client connected from {peer.host}:{peer.port} (ID: {self.client_id})")
        print(f"Server running on {self.factory.server_ip}:{self.factory.server_port}")
        self.factory.clients.append(self)
        self.sendLine(f"Welcome! Your client ID is {self.client_id}".encode('utf-8'))

    def connectionLost(self, reason):
        """
        Called when a client disconnects from the server.
        Prints a message indicating client disconnection and removes the client from the list of connected clients.
        """
        print(f"Client disconnected (ID: {self.client_id})")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        """
        Called when a line of data is received from a client.
        Prints the received message and broadcasts it to all other connected clients.
        """
        line = line.decode('utf-8')  # Decode bytes to string
        if line.startswith("/disconnect"):
            self.disconnectClient()
        elif line.startswith("/exit"):
            reactor.stop()  # Stop the server
        elif line.startswith("/send"):
            client_id = int(input("Enter client Id: "))
            message = input("Text: ")
            self.sendToClient(client_id, message)
        elif line.startswith("/help"):
            self.showHelp()
        elif line.startswith("/broadcast"):
            self.broadcastMessage(line)
        else:
            print(f"Received message: {line}")
            for client in self.factory.clients:
                if client != self:
                    client.sendLine(line.encode('utf-8'))

    def sendToClient(self, client_id, message):
        """
        Send a message to a specific client.

        Args:
            client_id (int): The ID of the client to send the message to.
            message (str): The message to send.
        """
        for client in self.factory.clients:
            if client.client_id == client_id:
                client.sendLine(message.encode('utf-8'))
                return
        self.sendLine(f"Client with ID {client_id} not found.".encode('utf-8'))

    def showHelp(self):
        """
        Show a list of all available commands to the user.
        """
        help_message = "Available commands:\n"
        help_message += "/disconnect: Disconnect from the server\n"
        help_message += "/exit: Stop the server\n"
        help_message += "/send <client_id>: Send a message to a specific client\n"
        help_message += "/broadcast <message>: Send a message to all connected clients\n"
        help_message += "/help: Show this help message\n"
        self.sendLine(help_message.encode('utf-8'))

    def broadcastMessage(self, line):
        """
        Broadcast a message to all connected clients.

        Args:
            line (str): The command line containing the /broadcast command and message.
        """
        message = line[len("/broadcast"):].strip()  # Extract the message from the command
        for client in self.factory.clients:
            client.sendLine(message.encode('utf-8'))
    
    def disconnectClient(self):
        """
        Disconnect the client from the server.
        """
        self.transport.loseConnection()

class ChatFactory(protocol.Factory):
    """
    Factory for creating instances of the ChatProtocol class.
    """

    def __init__(self, server_ip, server_port):
        """
        Initialize the factory with an empty list of clients and server IP and port.

        Args:
            server_ip (str): The IP address of the server.
            server_port (int): The port number of the server.
        """
        self.clients = []
        self.server_ip = server_ip
        self.server_port = server_port

    def buildProtocol(self, addr):
        """
        Called when a new connection is made to the server.
        Creates and returns a new instance of the ChatProtocol class.

        Args:
            addr: The address of the connecting client.

        Returns:
            ChatProtocol: A new instance of the ChatProtocol class.
        """
        return ChatProtocol(self)

class ChatConsoleProtocol(protocol.Protocol):
    """
    Protocol for handling command inputs from the console.
    """

    def __init__(self, factory):
        """
        Initialize the ChatConsoleProtocol with a reference to the factory.

        Args:
            factory (ChatFactory): The factory creating this protocol instance.
        """
        self.factory = factory
        self.connected_ips = set()  # Store connected IPs to avoid duplicate connections
    
    def connectionMade(self):
        self.transport.write(b">>> ")  # Write prompt symbol when connection is made

    def dataReceived(self, data):
        """
        Called when data is received from the console.
        Parses the command and executes it.

        Args:
            data (bytes): The data received from the console.
        """
        command = data.strip().decode("utf-8")  # Decode bytes to string and remove leading/trailing whitespace
        if command == "/exit":
            reactor.stop()  # Stop the server
        elif command.startswith("/send"):
            self.prepareMessage(command)
        elif command.startswith("/connect"):
            self.connectToServer(command)
        elif command.startswith("/help"):
            self.showLocalHelp()
        elif command.startswith("/disconnect"):
            self.disconnectServer()
        else:
            print("Unknown command. Type '/help' to see the list of valid commands.")
        self.transport.write(b">>> ")  # Write prompt symbol again after handling command

    def prepareMessage(self, command):
        """
        Prepare to send a message.

        Args:
            command (str): The command entered by the user.
        """
        parts = command.split(" ", 2)
        if len(parts) == 3:
            ip = parts[1]
            message = parts[2]
            self.sendMessage(ip, message)
        else:
            print("Invalid command usage. Use /send <ip> <message>")

    def sendMessage(self, ip, message):
        """
        Send a message to a specific IP address.

        Args:
            ip (str): The IP address of the client to send the message to.
            message (str): The message to send.
        """
        for client in self.factory.clients:
            if client.transport.getPeer().host == ip:
                client.sendLine(message.encode('utf-8'))
                return
        print(f"Client with IP {ip} not found.")

    def connectToServer(self, command):
        """
        Connect to another server.

        Args:
            command (str): The command entered by the user.
        """
        parts = command.split(" ", 2)
        if len(parts) == 3:
            ip = parts[1]
            port = int(parts[2])
            if ip not in self.connected_ips:
                self.connected_ips.add(ip)
                print(f"Connecting to {ip}:{port}...")
                reactor.connectTCP(ip, port, ChatClientFactory())
            else:
                print("Already connected to this server.")
        else:
            print("Invalid command usage. Use /connect <ip> <port>")

    def showLocalHelp(self):
        """
        Show a list of commands available in the local console.
        """
        help_message = "Local commands:\n"
        help_message += "/exit: Stop the server\n"
        help_message += "/send <ip> <message>: Send a message to a specific IP\n"
        help_message += "/connect <ip> <port>: Connect to another server\n"
        help_message += "/help: Show this help message\n"
        help_message += "/broadcast <message>: Send a message to all connected clients\n"
        help_message += "/disconnect: Disconnect from the server\n"
        print(help_message)
    
    def disconnectServer(self):
        """
        Disconnect from the server.
        """
        reactor.stop()

class ChatClientProtocol(protocol.Protocol):
    """
    Protocol for handling communication between client and server.
    """

    def connectionMade(self):
        print("Connected to server")

    def dataReceived(self, data):
        """
        Called when data is received from the server.
        """
        print(f"Received message: {data.decode('utf-8')}")

    def connectionLost(self, reason):
        print("Connection lost")

class ChatClientFactory(protocol.ClientFactory):
    """
    Factory for creating instances of the ChatClientProtocol class.
    """

    def buildProtocol(self, addr):
        """
        Called when a new connection is made to the client.
        Returns a new instance of the ChatClientProtocol class.
        """
        return ChatClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        """
        Called when a client connection attempt fails.
        """
        print("Connection failed")

def main():
    """
    Entry point of the program.
    Prompts the user to enter the port number and starts the chat server on that port.
    """
    server_ip = input("Enter server IP: ")  # Change this to your server's IP address
    server_port = int(input("Enter the port number (Use 9000 for testing): "))  # Prompt the user to enter the port number

    factory = ChatFactory(server_ip, server_port)
    reactor.listenTCP(server_port, factory)
    print(f"Chat server started on {server_ip}:{server_port}")

    # Start the command interface
    stdio.StandardIO(ChatConsoleProtocol(factory))  # Pass only the factory instance

    reactor.run()

if __name__ == "__main__":
    main()
