from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic

class ChatProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        peer = self.transport.getPeer()
        print(f"Client connected from {peer.host}:{peer.port}")
        print(f"Server running on {self.factory.server_ip}:{self.factory.server_port}")
        self.factory.clients[peer.host] = self
        self.sendLine(b"Welcome to the chat server!")

    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print(f"Client disconnected from {peer.host}:{peer.port}")
        del self.factory.clients[peer.host]

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if line.startswith("/disconnect"):
            self.disconnectClient()
        elif line.startswith("/exit"):
            reactor.stop()
        elif line.startswith("/send"):
            self.sendToClient(line)
        elif line.startswith("/broadcast"):
            self.broadcastMessage(line)
        elif line.startswith("/help"):
            self.showHelp()
        elif line.startswith("/connect"):
            self.connectToServer(line)
        else:
            print(f"Received message: {line}")
            self.broadcast(line)

    def sendToClient(self, line):
        parts = line.split(" ", 2)
        if len(parts) == 3:
            dest_ip, message = parts[1:]
            client = self.factory.clients.get(dest_ip)
            if client:
                client.sendLine(message.encode('utf-8'))
            else:
                self.sendLine(f"Client with IP {dest_ip} not found.".encode('utf-8'))
        else:
            self.sendLine("Invalid command usage. Use /send <IP> <message>".encode('utf-8'))

    def showHelp(self):
        help_message = """Available commands:
/disconnect: Disconnect from the server
/exit: Stop the server
/send <IP>: Send a message to a specific client
/broadcast <message>: Send a message to all connected clients
/help: Show this help message
/connect <IP> <port>: Connect to a server"""
        self.sendLine(help_message.encode('utf-8'))

    def broadcastMessage(self, line):
        message = line[len("/broadcast"):].strip()  # Extract the message from the command
        self.broadcast(message.encode('utf-8'))

    def broadcast(self, message):
        message_str = message.decode('utf-8')  # Convert bytes to string
        for client in self.factory.clients.values():
            client.sendLine(message_str.encode('utf-8'))  # Send the string message

    def disconnectClient(self):
        self.transport.loseConnection()

    def connectToServer(self, line):
        parts = line.split(" ")
        if len(parts) == 3:
            ip, port = parts[1], int(parts[2])
            reactor.connectTCP(ip, port, ChatClientFactory())
        else:
            self.sendLine("Invalid command usage. Use /connect <IP> <port>".encode('utf-8'))

class ChatFactory(protocol.Factory):
    def __init__(self, server_ip, server_port):
        self.clients = {}
        self.server_ip = server_ip
        self.server_port = server_port

    def buildProtocol(self, addr):
        return ChatProtocol(self)

class ChatConsoleProtocol(ChatProtocol, protocol.Protocol):
    def connectionMade(self):
        self.transport.write(b">>> ")  # Write prompt symbol when connection is made

    def dataReceived(self, data):
        command = data.strip().decode("utf-8")  # Decode bytes to string and remove leading/trailing whitespace
        if command == "/exit":
            reactor.stop()  # Stop the server
        elif command.startswith("/send"):
            self.prepareMessage(command)
        elif command.startswith("/help"):
            super().showHelp()
        elif command.startswith("/broadcast"):
            self.broadcastMessage(command)
        elif command.startswith("/connect"):
            super().connectToServer(command)
        else:
            print("Unknown command. Type '/help' to see the list of valid commands.")
        self.transport.write(b">>> ")  # Write prompt symbol again after handling command

    def prepareMessage(self, command):
        parts = command.split(" ", 2)
        if len(parts) == 3:
            dest_ip, message = parts[1:]
            client = self.factory.clients.get(dest_ip)
            if client:
                client.sendLine(message.encode('utf-8'))
            else:
                print(f"Client with IP {dest_ip} not found.")
        else:
            print("Invalid command usage. Use /send <IP> <message>")

class ChatClientProtocol(protocol.Protocol):
    def connectionMade(self):
        print("Connected to server")

    def dataReceived(self, data):
        print(f"Received message: {data.decode('utf-8')}")

    def connectionLost(self, reason):
        print("Connection lost")

class ChatClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return ChatClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")

def main():
    server_ip = input("Enter server IP: ")  
    server_port = int(input("Enter the port number (Use 9000 for testing): "))  

    factory = ChatFactory(server_ip, server_port)
    reactor.listenTCP(server_port, factory)
    print(f"Chat server started on {server_ip}:{server_port}")

    stdio.StandardIO(ChatConsoleProtocol(factory))  

    reactor.run()

if __name__ == "__main__":
    main()
