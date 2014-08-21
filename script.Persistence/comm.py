#**************************************************************************************
#*** Simple wrapper for sending and receiving pickled Python objects over an        ***
#***  established socket connection.                                                ***
#**************************************************************************************

import os, cPickle
from struct import *
from socket import *

#######################################################################################
def send(sock, data):
    # Convert the data (any Python object) into a pickled string
    data = cPickle.dumps(data)
    # Get data size so the receiving connection will know how much to receive
    datasize = len(data)
    # Send the data size as a socket message
    sock.send(pack("<i", datasize))
    # Send the pickled string as a socket message
    sock.send(data)

#######################################################################################
def recv(sock):
    # Read in a waiting int-sized message from the given socket connection
    datasize = unpack("<i", sock.recv(4))[0]
    # Read in a pickled object of the size given above, and convert it
    pick = cPickle.loads(sock.recv(datasize))
    # Return the Python object to the receiver
    return pick