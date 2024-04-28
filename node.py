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
            self.transport.loseConnection()  # Disconnect the client
        elif line.startswith("/exit"):
            reactor.stop()  # Stop the server
        elif line.startswith("/send"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                ip = parts[1]
                message = parts[2]
                self.sendToClientByIP(ip, message)
            else:
                self.sendLine("Invalid command usage. Use /send <ip> <message>".encode('utf-8'))
        else:
            print(f"Received message: {line}")
            for client in self.factory.clients:
                if client != self:
                    client.sendLine(line.encode('utf-8'))

    def sendToClientByIP(self, ip, message):
        """
        Send a message to a specific client by their IP address.

        Args:
            ip (str): The IP address of the client to send the message to.
            message (str): The message to send.
        """
        for client in self.factory.clients:
            if client.transport.getPeer().host == ip:
                client.sendLine(message.encode('utf-8'))
                return
        self.sendLine(f"Client with IP {ip} not found.".encode('utf-8'))

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
        else:
            self.sendMessage(command)  # Treat any other input as a message to send to the server

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
            self.sendMessageToServer(ip, message)
        else:
            print("Invalid command usage. Use /send <ip> <message>")

    def sendMessageToServer(self, ip, message):
        """
        Send a message to the server.

        Args:
            ip (str): The IP address of the client to send the message to.
            message (str): The message to send.
        """
        self.factory.sendLine(f"/send {ip} {message}".encode('utf-8'))

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
            print(f"Connecting to {ip}:{port}...")
            reactor.connectTCP(ip, port, ChatClientFactory())  # Connect to the specified IP and port
        else:
            print("Invalid command usage. Use /connect <ip> <port>")

    def sendMessage(self, message):
        """
        Send a message to the server.

        Args:
            message (str): The message to send.
        """
        self.factory.sendLine(message.encode('utf-8'))

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
    stdio.StandardIO(ChatConsoleProtocol(factory))

    reactor.run()

if __name__ == "__main__":
    main()
