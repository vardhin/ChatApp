from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import error

class MessageReceiver(Protocol):
    def dataReceived(self, data):
        print("Received message:", data.decode('utf-8'))

def send_message_to_friend(friend_ip):
    def connected(protocol):
        protocol.transport.write(b"Hello, friend!")
    
    def failed(reason):
        print("Connection failed:", reason.getErrorMessage())
        reactor.stop()
    
    endpoint = TCP4ClientEndpoint(reactor, friend_ip, 1080)  # Change 1080 to the SOCKS proxy port
    d = endpoint.connect(MessageReceiver())
    d.addCallback(connected)
    d.addErrback(failed)

def start_server():
    endpoint = TCP4ServerEndpoint(reactor, 12345)  # Change 12345 to the desired server port
    endpoint.listen(MessageReceiver())

# Replace 'friend_ip' with your friend's actual IP address
friend_ip = 'your_friend_ip_here'

try:
    # If the script is run with an argument 'server', it will start as a server.
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        start_server()
    else:
        send_message_to_friend(friend_ip)
    reactor.run()
except error.CannotListenError:
    print("Port is already in use.")
except Exception as e:
    print("An error occurred:", e)
