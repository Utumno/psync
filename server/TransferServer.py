import SocketServer
import socket  # Import socket module


class TransferServer(object):
    host = socket.gethostbyname(socket.gethostname())

    class TransferTCPHandler(SocketServer.BaseRequestHandler):
        ''' Here we implement the required service '''

        def handle(self):
             self.data = self.request.recv(1024).strip()
             print "{} wrote:".format(self.client_address[0])
             print self.data
             # just send back the same data, but upper-cased
             self.request.sendall(self.data.upper())

    def __init__(self):
        self.port = 8000  # Reserve a port for your service.
        print self.host
        print self.port
        server = SocketServer.TCPServer((self.host, self.port), TransferServer.TransferTCPHandler)
        server.serve_forever()


if __name__ == "__main__":
    x = TransferServer()
