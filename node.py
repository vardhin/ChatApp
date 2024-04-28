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
            client_id = int(input("Enter client Id: "))
            message = input("Text: ")
            self.sendToClient(client_id, message)
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

    def __init__(self, factory, chat_protocol):
        """
        Initialize the ChatConsoleProtocol with a reference to the factory and ChatProtocol instance.

        Args:
            factory (ChatFactory): The factory creating this protocol instance.
            chat_protocol (ChatProtocol): The instance of ChatProtocol associated with the client.
        """
        self.factory = factory
        self.chat_protocol = chat_protocol  # Store reference to ChatProtocol instance
        self.sending_message = False
        self.pending_client_id = None
    
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
        if self.sending_message:
            self.handleMessageInput(command)
        elif command.startswith("/connect"):
            self.connectToServer(command)
        elif command == "/exit":
            reactor.stop()  # Stop the server
        elif command.startswith("/send"):
            self.prepareMessage(command)
        elif command.startswith("/get_id"):
            self.showClientId()
        else:
            print("Unknown command. Type '/exit' to stop the server.")
        self.transport.write(b">>> ")  # Write prompt symbol again after handling command

    def prepareMessage(self, command):
        """
        Prepare to send a message.

        Args:
            command (str): The command entered by the user.
        """
        parts = command.split(" ", 2)
        if len(parts) == 3:
            self.pending_client_id = int(parts[1])
            self.sending_message = True
            print("Enter message:")
        else:
            print("Invalid command usage. Use /send <client_id> <message>")

    def handleMessageInput(self, message):
        """
        Handle input for the message content.

        Args:
            message (str): The message entered by the user.
        """
        if self.pending_client_id is not None:
            self.sendToClient(self.pending_client_id, message)
            self.pending_client_id = None
            self.sending_message = False
        else:
            print("Error: No pending client ID")

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
            reactor.connectTCP(ip, port, ChatClientFactory())
        else:
            print("Invalid command usage. Use /connect <ip> <port>")

    def showClientId(self):
        """
        Show the client ID.
        """
        client_id = self.chat_protocol.get_id()
        print(f"Your client ID is: {client_id}")

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
        print(f"Client with ID {client_id} not found.")

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
