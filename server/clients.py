from Queue import Queue, Empty
from _socket import gaierror
import socket
import threading
from time import sleep
from log import Log
from watcher.sync import Sync

_BROADCAST = 0
_TCP = 1

BROADCAST_INTERVAL = TIMEOUT = 5 # TODO
PORT = 8001

class _BaseClient(threading.Thread,Log):

    def __init__(self, socket_type=_BROADCAST, tcp_host="0.0.0.0", port=PORT):
        super(_BaseClient, self).__init__(name=self.__class__.__name__,
                                              target=self._task)
        Log.__init__(self) # duh
        self.s = None
        self.setup(socket_type, tcp_host, port)
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = PORT  # Reserve a port for your service. TODO...

    def setup(self, socket_type, tcp_host, port):
        try:
            if socket_type is _BROADCAST:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # SOL_SOCKET is needed for SO_BROADCAST
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((tcp_host, port))
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.settimeout(TIMEOUT)
        except socket.error:
            self.e( "Failed to create the socket")

    def _task(self):
        try:
            self.service()
        finally:
            if self.s: self.s.close()

    def service(self): raise NotImplemented

    def shutdown(self): raise NotImplemented


_RECEIVE_BUFFER = 1024 # TODO: belongs to message

class DiscoveryClient(_BaseClient):
    """ Sends broadcast msgs to the lan informing
        its existence along with the its tracked UUIDS
    """

    def __init__(self, broadcast_interval=BROADCAST_INTERVAL):
        super(DiscoveryClient, self).__init__(socket_type=_BROADCAST)
        self.broadcast_interval = broadcast_interval
        self.interrupted = False

    def service(self):
        """Discover if there is an active sync application in the LAN."""
        self.i("Starting Discovery client at: %s:%s", self.host, self.port)
        while not self.interrupted:
            self.s.sendto(Sync.broadcastMsg().serialize(), ('255.255.255.255', PORT))
            # TODO: Sync.notifyPeers()
            try:
                c, addr = self.s.recvfrom(_RECEIVE_BUFFER)
                if addr[0] != self.host:
                    self.d( "The server's response is " % c)
                    self.i('New peer')
            except socket.timeout: self.d("Broadcast timed out")
            except: self.e("Broadcast failed")
            sleep(self.broadcast_interval)
        self.i("Stopping Discovery client at: %s:%s", self.host, self.port)

    def shutdown(self):
        self.interrupted = True

class SyncClient(_BaseClient):
    """Dispatches messages to the Discovery server."""

    def __init__(self):
        super(SyncClient, self).__init__(socket_type=_BROADCAST)
        self._queue = Queue()
        self.interrupted = False

    def service(self):
        """Discover if there is an active sync application in the LAN."""
        self.i("Starting Sync client at: %s:%s", self.host, self.port)
        while not self.interrupted:
            try:
                msg, host = self._queue.get(timeout=BROADCAST_INTERVAL)
                self.s.sendto(msg.serialize(), (host, PORT))
            except Empty:  # for the timeout - TODO - no timeout and special
                # quit token
                pass
            except gaierror:
                self.e(msg.label + " sending failed")
        self.i("Stopping Sync client at: %s:%s", self.host, self.port)

    def add(self,obj):
        self._queue.put(obj)

    def shutdown(self):
        self.interrupted = True
