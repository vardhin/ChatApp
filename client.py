from twisted.internet import reactor, protocol
from twisted.protocols import basic

class ChatClientProtocol(basic.LineReceiver):
    def connectionMade(self):
        print("Connected to server")

    def lineReceived(self, line):
        print(f"Received message: {line.decode('utf-8')}")

class ChatClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return ChatClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost")
        reactor.stop()

def main():
    reactor.connectTCP("127.0.0.1", 9999, ChatClientFactory())
    reactor.run()

if __name__ == "__main__":
    main()
