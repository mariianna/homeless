import comm
from socket import *

commport = 51999

host = gethostname()
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, commport))
comm.send(sock, "break")
