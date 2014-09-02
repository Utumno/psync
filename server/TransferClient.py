import SocketClient
import socket

class TransferClient(SocketClient.BaseClient):

    HOST = "192.168.1.9"
    PORT = 8000

    def __init__(self):
      SocketClient.BaseClient.__init__(self,SocketClient.TRANSFER_MODE, TransferClient.HOST, TransferClient.PORT)


    def service(self):
        ''' This method discovers if there is an active sync application in the LAN '''
        self.s.sendall("ACTUAL GIT OPERATIONS")
        try:
            c, addr =  self.s.recvfrom(1024)
            print "The received message's payload is ",c
        except socket.timeout as e:
            msg  = e.message
            print msg.upper()

if __name__ == "__main__":
   TransferClient()