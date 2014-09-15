import SocketServer
import logging
import socket
import threading

class DiscoveryServer(threading.Thread):

    class _DiscoveryUDPHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            data = self.request[0].strip()
            logging.debug("self.request value is %s", data)
            _socket = self.request[1]
            _socket.sendto(str(self.server.host), self.client_address)

    def __init__(self):
        super(DiscoveryServer, self).__init__(name=self.__class__.__name__,
                                              target=self._task)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 8001  # Reserve a port for your service. TODO...
        self.server = SocketServer.UDPServer((self.host, self.port),
                                      DiscoveryServer._DiscoveryUDPHandler)
        # TODO: inherit from UDPServer

    def _task(self):
        logging.info("Starting Discovery server at: %s:%s", self.host,
                     self.port)
        try:
            self.server.serve_forever()
        except:
            logging.exception("Discovery server crashed.")
        logging.info("Stopping Discovery server at: %s:%s", self.host,
                     self.port)

    def shutdown(self):
        self.server.shutdown()
