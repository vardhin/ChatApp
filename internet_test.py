from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import error

class MessageReceiver(Protocol):
    def dataReceived(self, data):
        print("Received message:", data.decode('utf-8'))

class MessageClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        return MessageReceiver()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed:", reason.getErrorMessage())
        reactor.stop()

def send_message_to_friend(friend_ip):
    endpoint = TCP4ClientEndpoint(reactor, friend_ip, 1080)  # Change 1080 to the SOCKS proxy port
    d = endpoint.connect(MessageClientFactory())

def start_server():
    endpoint = TCP4ServerEndpoint(reactor, 12345)  # Change 12345 to the desired server port
    endpoint.listen(MessageReceiver())

def main():
    try:
        choice = input("Do you want to run as a server or client? (server/client): ").lower()
        if choice == 'server':
            start_server()
        elif choice == 'client':
            friend_ip = input("Enter your friend's IP address: ")
            send_message_to_friend(friend_ip)
        else:
            print("Invalid choice. Please enter 'server' or 'client'.")
            return

        reactor.run()
    except error.CannotListenError:
        print("Port is already in use.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
