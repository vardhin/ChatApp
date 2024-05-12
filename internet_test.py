from twisted.internet import reactor
from txsocksx.client import SOCKS5ClientEndpoint
from txsocksx.client import SOCKS5ClientFactory
from txsocksx.client import SOCKS4ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint, connectProtocol

class MessageReceiver(Protocol):
    def dataReceived(self, data):
        print("Received message:", data.decode('utf-8'))

def send_message_to_friend(friend_ip):
    endpoint = SOCKS5ClientEndpoint(friend_ip, 1080)  # Change 1080 to the SOCKS proxy port
    d = endpoint.connect(MessageReceiver())
    d.addErrback(handle_failure)

def start_server():
    endpoint = TCP4ServerEndpoint(reactor, 12345)  # Change 12345 to the desired server port
    endpoint.listen(SOCKS4ClientFactory(MessageReceiver))

def handle_failure(reason):
    print("Connection failed:", reason.getErrorMessage())
    reactor.stop()

# Replace 'friend_ip' with your friend's actual IP address
friend_ip = 'your_friend_ip_here'

try:
    # If the script is run with an argument 'server', it will start as a server.
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        start_server()
    else:
        send_message_to_friend(friend_ip)
    reactor.run()
except Exception as e:
    print("An error occurred:", e)
