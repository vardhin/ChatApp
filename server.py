from twisted.internet import reactor, protocol
from twisted.protocols import basic

class ChatProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        peer = self.transport.getPeer()
        print(f"Client connected from {peer.host}:{peer.port}")
        print(f"Server running on {self.factory.server_ip}:{self.factory.server_port}")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print("Client disconnected")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print(f"Received message: {line}")
        for client in self.factory.clients:
            if client != self:
                client.sendLine(line.encode('utf-8'))

class ChatFactory(protocol.Factory):
    def __init__(self, server_ip, server_port):
        self.clients = []
        self.server_ip = server_ip
        self.server_port = server_port

    def buildProtocol(self, addr):
        return ChatProtocol(self)

def main():
    server_ip = '127.0.0.1'  # Change this to your server's IP address
    server_port = 9999
    reactor.listenTCP(server_port, ChatFactory(server_ip, server_port))
    print(f"Chat server started on {server_ip}:{server_port}")
    reactor.run()

if __name__ == "__main__":
    main()
