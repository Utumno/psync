import logging
import socket
import threading
from time import sleep

_UDP = 0
_TCP = 1

BROADCAST_INTERVAL = TIMEOUT = 5 # TODO
PORT = 8001

class _BaseClient(threading.Thread):

    def __init__(self, socket_type=_UDP, tcp_host="0.0.0.0", port=PORT):
        super(_BaseClient, self).__init__(name=self.__class__.__name__,
                                              target=self._task)
        self.s = None
        self.setup(socket_type, tcp_host, port)
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = PORT  # Reserve a port for your service. TODO...

    def setup(self, socket_type, tcp_host, port):
        try:
            if socket_type is _UDP:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # SOL_SOCKET is needed for SO_BROADCAST
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((tcp_host, port))
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.settimeout(TIMEOUT)
        except socket.error:
            logging.exception( "Failed to create the socket")

    def _task(self):
        try:
            self.service()
        finally:
            if self.s: self.s.close()

    def service(self): raise NotImplemented

    def shutdown(self): raise NotImplemented


_RECEIVE_BUFFER = 1024 # TODO: belongs to message

class DiscoveryClient(_BaseClient):

    def __init__(self, broadcast_interval=BROADCAST_INTERVAL):
        super(DiscoveryClient, self).__init__(socket_type=_UDP)
        self.broadcast_interval = broadcast_interval
        self.interrupted = False

    def service(self):
        """Discover if there is an active sync application in the LAN."""
        logging.info("Starting Discovery client at: %s:%s", self.host,
                     self.port)
        while not self.interrupted:
            # Sync.broadcast()
            self.s.sendto("DISCOVERY MESSAGE", ('255.255.255.255', PORT))
            # Sync.notifyPeers()
            try:
                c, addr = self.s.recvfrom(_RECEIVE_BUFFER)
                if addr[0] != self.host:
                    print "The received message's payload is ", c
                    logging.info('New peer')
            except socket.timeout: logging.debug("Broadcast timed out")
            except: logging.exception("Broadcast failed")
            sleep(self.broadcast_interval)
        logging.info("Stopping Discovery client at: %s:%s", self.host,
                     self.port)

    def shutdown(self):
        self.interrupted = True
