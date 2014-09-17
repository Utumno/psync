from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import logging
import socket
import threading
from log import Log

class DiscoveryServer(threading.Thread):

    class _DiscoveryUDPHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            data = self.request[0].strip()
            logging.debug("self.request value is %s", data)
            _socket = self.request[1]
            _socket.sendto(str(self.server.server_address),
                           self.client_address)

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
            logging.info("Stopping Discovery server at: %s:%s", self.host,
                         self.port)
        except:
            logging.exception("Discovery server crashed.")

    def shutdown(self):
        self.server.shutdown()

class HttpServer(Log,threading.Thread):
    # Thread's superclass does not call super.init() so I had to put Log First
    PORT = 80

    def __init__(self):
        super(HttpServer, self).__init__(name=self.__class__.__name__,
                                         target=self._task)
        self.host = socket.gethostbyname(socket.gethostname())
        self.server = SocketServer.TCPServer((self.host, self.PORT),
                                             SimpleHTTPRequestHandler)

    def _task(self):
        self.i("Starting Http server at: %s", self.server.server_address)
        try:
            self.server.serve_forever()
            self.i("Stopping Http server at: %s",self.server.server_address)
        except:
            self.e("Http server server crashed.")

    def shutdown(self):
        self.server.shutdown()
