from twisted.internet import reactor, protocol
from twisted.protocols import basic

class ChatClientProtocol(basic.LineReceiver):
    def connectionMade(self):
        print("Connected to server")
        self.send_message()

    def lineReceived(self, line):
        print(f"Received message: {line.decode('utf-8')}")
        self.send_message()

    def send_message(self):
        message = input(">>> ")
        if message:
            self.sendLine(message.encode('utf-8'))
            if message.strip() == "/exit":
                exit_program()
            elif message.strip() == "/disc":
                disconnect()
            elif message.strip() == "/connect":
                connect()
            else:
                reactor.callLater(0.1, self.send_message)  # Schedule sending next message

    def connectionLost(self, reason):
        print("Connection lost")
        connect()

class ChatClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return ChatClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        connect()

def connect():
    #ip="127.0.0.1"
    #port=9999
    print("Default: 127.0.0.1, 9999")
    ip = input("Enter the ip of the friend: ")
    port = int(input("Enter the port of the friend: "))
    
    print(f"Connecting to {ip}:{port}...")
    reactor.connectTCP(ip, port, ChatClientFactory())
    reactor.run()

def disconnect():
    print("Disconnecting...")
    reactor.disconnectAll()

def exit_program():
    print("exitting client interface...")
    reactor.stop()
    quit()

def main():
    connect()

if __name__ == "__main__":
    main()
