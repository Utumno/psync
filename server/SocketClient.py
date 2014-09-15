import logging
import socket
import threading
from time import sleep


DISCOVERY_MODE = 0
TRANSFER_MODE = 1

class BaseClient(threading.Thread):

    def __init__(self, socket_type=0, tcp_host="0.0.0.0", port=0):
        super(BaseClient, self).__init__(name=self.__class__.__name__,
                                              target=self._task)
        self.setup(socket_type, tcp_host, port)
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 8001  # Reserve a port for your service. TODO...

    def setup(self, socket_type, tcp_host, port):
        self.s = None
        try:
            if socket_type is 0:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((tcp_host, port))
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.settimeout(1)  # FIXME
        except socket.error:
            logging.exception( "Failed to create the socket")

    def _task(self):
        try:
            self.service()
        finally:
            if self.s: self.s.close()

    def service(self): raise NotImplemented

    def shutdown(self): raise NotImplemented


class DiscoveryClient(BaseClient):

    def __init__(self, broadcast_interval=5):
        super(DiscoveryClient, self).__init__(socket_type=DISCOVERY_MODE)
        self.broadcast_interval = broadcast_interval
        self.interrupted = False

    def service(self):
        """Discover if there is an active sync application in the LAN."""
        logging.info("Starting Discovery client at: %s:%s", self.host,
                     self.port)
        while not self.interrupted:
            # Sync.broadcast()
            self.s.sendto("DISCOVERY MESSAGE", ('255.255.255.255', 8001))
            # Sync.notifyPeers()
            try:
                c, addr = self.s.recvfrom(1024)
                print "The received message's payload is ", c
                print "The responding server address is ", addr
            except socket.timeout: logging.debug("Broadcast timed out")
            except: logging.exception("Broadcast timed out")
            sleep(self.broadcast_interval)
        logging.info("Stopping Discovery client at: %s:%s", self.host,
                     self.port)

    def shutdown(self):
        self.interrupted = True
