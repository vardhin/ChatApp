from twisted.internet import reactor
from txsocksx.client import SOCKS5ClientEndpoint
from twisted.internet.protocol import Protocol

class MessageSender(Protocol):
    def connectionMade(self):
        self.transport.write(b'hi')
        self.transport.loseConnection()

def send_message_to_friend(friend_ip):
    endpoint = SOCKS5ClientEndpoint(friend_ip, 1080)  # Change 1080 to the SOCKS proxy port
    d = endpoint.connect(MessageSender())
    d.addErrback(handle_failure)

def handle_failure(reason):
    print("Connection failed:", reason.getErrorMessage())
    reactor.stop()

# Replace 'friend_ip' with your friend's actual IP address
friend_ip = 'your_friend_ip_here'

try:
    send_message_to_friend(friend_ip)
    reactor.run()
except Exception as e:
    print("An error occurred:", e)
