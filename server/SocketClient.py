import socket

DISCOVERY_MODE = 0
TRANSFER_MODE = 1

class BaseClient(object):
    def __init__(self, socket_type=0, host="0.0.0.0", port=0):
        self.setup(socket_type, host, port)
        self.service()
        self.close_connection()

    def setup(self, socket_type, host, port):
        if socket_type is 0:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except socket.error as e:
                print "Failed to create the socket. ERROR Code: ", e.errno, \
                    " Message: ", e.message
        else:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((host, port))
            except socket.error as e:
                print "Failed to create the socket. ERROR Code: ", e.errno, \
                    " Message: ", e.message
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(1)  # FIXME

    def service(self):
        """
        Called by the constructor
        Must be overridden
        """
        pass

    def close_connection(self):
        self.s.close()
