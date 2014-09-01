#!/usr/bin/env python2 # This is client.py file
import socket               # Import socket module

class DiscoveryClient(object):
    def __init__(self, s = None):
        if s is None:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error as e:
                print "Failed to create the socket. ERROR Code: ", e.errno, " Message: ",e.message
        else:
            self.s = s
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.settimeout(1) #FIXME

    def discovery(self):
        ''' This method discovers if there is an active sync application in the LAN '''
        self.s.sendto("DISCOVERY MESSAGE", ('255.255.255.255', 8001))
        try:
            c, addr =  self.s.recvfrom(1024)
            print "The received message's payload is ",c
            print "The responding server address is ",addr

        except socket.timeout as e:
            msg  = e.message
            print msg.upper()

    def close_connection(self):
          self.s.close()


if __name__ == "__main__":
   x =  DiscoveryClient()
   x.discovery()
   x.close_connection()