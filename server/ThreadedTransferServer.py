import SocketServer
import socket  # Import socket module
import threading

class ThreadedTransferTCPHandler(SocketServer.BaseRequestHandler):
    """Here we implement the required service."""

    def handle(self):
        self.data = self.request.recv(1024).strip()
        cur_thread = threading.current_thread()
        print "{} wrote:".format(self.client_address[0])
        print self.data, cur_thread
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

class ThreadedTransferServer(SocketServer.ThreadingMixIn,
                             SocketServer.TCPServer):
    host = socket.gethostbyname(socket.gethostname())
    port = 8000

server = ThreadedTransferServer(
    (ThreadedTransferServer.host, ThreadedTransferServer.port),
    ThreadedTransferTCPHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = False
server_thread.start()
print "Server loop running in thread:", server_thread.name
