# Wake-On-LAN
#
# Copyright (C) 2002 by Micro Systems Marc Balmer
# Written by Marc Balmer, marc@msys.ch, http://www.msys.ch/
# This code is free software under the GPL
#
# Modified 2008 for use in XBMC Plugins - ozNick


import struct
import socket

from time import sleep


def WakeOnLan(ethernet_address):
    try:
        # Construct a six-byte hardware address
        addr_byte = ethernet_address.split(':')
        hw_addr = struct.pack('BBBBBB',
            int(addr_byte[0], 16),
            int(addr_byte[1], 16),
            int(addr_byte[2], 16),
            int(addr_byte[3], 16),
            int(addr_byte[4], 16),
            int(addr_byte[5], 16))

        # Build the Wake-On-LAN "Magic Packet"...
        msg = '\xff' * 6 + hw_addr * 16

        # ...and send it to the broadcast address using UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ('<broadcast>', 9))
        s.close()
    except Exception, e:
        print str(e)
        return

def CheckHost( path, port=139, retries=1 ):
    # if a smb path we check to see if host is awake
    if ( not path.lower().startswith( "smb://" ) ): return True
    # parse the computers hostname from path
    hostname = path.split( "/" )[ 2 ]
    # filter out username/password
    if ( "@" in hostname ):
        hostname = hostname.split( "@" )[ 1 ]
    # check if host is alive, no more than number of retries
    for retry in range( retries ):
        try:
            # try and connect to host on supplied port
            s = socket.socket()
            s.settimeout( 0.25 )
            s.connect( ( hostname, port ) )
            s.close()
            # we return True since connection succeeded
            return hostname, True
        except socket.error, e:
            # we sleep for 5 seconds before next retry
            sleep( 5 )
    # we return False since connection failed
    return hostname, False


if ( __name__ == "__main__" ):
    # send the WOL packet
    mac_address = "##:##:##:##:##:##"
    WakeOnLan( ethernet_address=mac_address )
    print "WOL packet sent for %s" % ( mac_address, )
    # check if host is alive
    hostname, alive = CheckHost( path="smb://SERVER/Movies/", port=139, retries=5 )
    print "Host '%s' is %salive:" % ( hostname, ( "not ", "", )[ alive == True ], )
