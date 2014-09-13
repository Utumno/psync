import SocketClient
import socket

class DiscoveryClient(SocketClient.BaseClient):
    def __init__(self):
        SocketClient.BaseClient.__init__(self, SocketClient.DISCOVERY_MODE)

    def service(self):
        """Discover if there is an active sync application in the LAN."""
        self.s.sendto("DISCOVERY MESSAGE", ('255.255.255.255', 8001))
        try:
            c, addr = self.s.recvfrom(1024)
            print "The received message's payload is ", c
            print "The responding server address is ", addr
        except socket.timeout as e:
            msg = e.message
            print msg.upper()

if __name__ == "__main__":
    DiscoveryClient()
