from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic
import getpass
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

def encrypt_message(public_key, message):
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_message(private_key, encrypted_message):
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    try:
        decrypted_message = cipher.decrypt(encrypted_message)
        return decrypted_message.decode()
    except ValueError as e:
        print("Error decrypting message:", e)
        return None

def gen_keys(seed):
    os.environ['PYTHONHASHSEED'] = seed
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key().decode('utf-8')
    public_key = rsa_key.publickey().export_key().decode('utf-8')
    return private_key, public_key

def get_password():
    password = getpass.getpass("Enter your password: ")
    return password

class ChatProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.private_key, self.public_key = gen_keys(get_password())
        print(f"Public key: {self.public_key}")
        print(f"Private key: {self.private_key}")

    def connectionMade(self):
        peer = self.transport.getPeer()
        print(f"Client connected from {peer.host}:{peer.port}")
        print(f"Server running on {self.factory.server_ip}:{self.factory.server_port}")
        self.factory.clients[peer.host] = self
        self.sendLine(b"Welcome to the chat server!")

    def connectionLost(self, reason):
        if hasattr(self.transport.getPeer(), "host"):
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
        elif line.startswith("/publickey"):
            self.showPublicKey()
        else:
            print(f"Received message: {line}")
            self.broadcast(line)

    def sendToClient(self, line):
        parts = line.split(" ", 2)
        if len(parts) == 3:
            dest_ip, message = parts[1:]
            client = self.factory.clients.get(dest_ip)
            if client:
                encrypted_message = encrypt_message(client.public_key, message)
                client.sendLine(encrypted_message)
            else:
                self.sendLine(f"Client with IP {dest_ip} not found.".encode('utf-8'))
        else:
            self.sendLine("Invalid command usage. Use /send <IP> <message>".encode('utf-8'))

    def showHelp(self):
        help_message = """Available commands:
                        /exit: Stop the server
                        /send <IP>: Send a message to a specific client
                        /broadcast <message>: Send a message to all connected clients
                        /help: Show this help message
                        /connect <IP> <port>: Connect to a server
                        /publickey: Display your public key"""
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
            reactor.connectTCP(ip, port, self.factory.getClientProtocol())
        else:
            self.sendLine("Invalid command usage. Use /connect <IP> <port>".encode('utf-8'))

    def showPublicKey(self):
        self.sendLine(f"Your public key is: {self.public_key}".encode('utf-8'))

class ChatFactory(protocol.Factory):
    def __init__(self, server_ip, server_port):
        self.clients = {}
        self.server_ip = server_ip
        self.server_port = server_port

    def buildProtocol(self, addr):
        return ChatProtocol(self)

    def getClientProtocol(self):
        return ChatClientProtocol(self.private_key)

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
        elif command.startswith("/publickey"):
            self.showPublicKey()
        else:
            print("Unknown command. Type '/help' to see the list of valid commands.")
        self.transport.write(b">>> ")  # Write prompt symbol again after handling command

    def prepareMessage(self, command):
        parts = command.split(" ", 3)
        if len(parts) == 4:
            public_key_client = parts[1]
            ip_client = parts[2]
            message_client = parts[3]
            client = self.factory.clients.get(ip_client)
            if client:
                message_client = encrypt_message(public_key_client, message_client)
                client.sendLine(message_client)
            else:
                print(f"Client with IP {ip_client} not found.")
        else:
            print("Invalid command usage. Use /send <public_key> <IP> <message>")

class ChatClientProtocol(protocol.Protocol):
    def __init__(self, private_key):
        self.private_key = private_key

    def connectionMade(self):
        print("Connected to server")

    def dataReceived(self, data):
        received_message = decrypt_message(self.private_key, data)
        if received_message:
            print(f"Received message: {received_message}")

    def connectionLost(self, reason):
        print("Connection lost")

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
