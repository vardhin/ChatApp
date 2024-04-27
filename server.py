from twisted.internet import reactor, protocol
from twisted.protocols import basic

class ChatProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print("Client connected")
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
    def __init__(self):
        self.clients = []

    def buildProtocol(self, addr):
        return ChatProtocol(self)

def main():
    reactor.listenTCP(9999, ChatFactory())
    print("Chat server started")
    reactor.run()

if __name__ == "__main__":
    main()
