import SocketServer
import socket


class DiscoveryServer(object):
    host = socket.gethostbyname(socket.gethostname())

    class DiscoveryUDPHandler(SocketServer.BaseRequestHandler):
        ''' Here we implement the required service '''

        def handle(self):
            data = self.request[0].strip()
            print "self.request value is ", self.request[0]
            socket = self.request[1]
            print 'Got that: ', data
            socket.sendto(str(DiscoveryServer.host), self.client_address)

    def __init__(self):
        self.port = 8001  # Reserve a port for your service.
        print self.host
        print self.port
        server = SocketServer.UDPServer((self.host, self.port), DiscoveryServer.DiscoveryUDPHandler)
        server.serve_forever()


if __name__ == "__main__":
    x = DiscoveryServer()
