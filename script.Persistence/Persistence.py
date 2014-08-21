import comm, sys, thread
from socket import socket, gethostname, AF_INET, SOCK_STREAM

# Type below the port you want to use to exchange data.
commport = 51999

#######################################################################################
class ClassServer:
    def __init__(self):
        self.dying = False
        self.classInstances = {}
        self.connect()

    ###################################################################################
    def connect(self):
        # Find out from Python the hostname of this computer, and label yourself as it.
        host = gethostname()
        # These three lines create a socket and listen for a connection.
        self.serversock = socket(AF_INET, SOCK_STREAM)      # listen on tcp/ip socket
        self.serversock.bind((host, commport))              # serve clients in threads
        self.serversock.listen(1)
        while self.dying == False:
            # When you get a connection, save the client's connection info
            clientsock, clientaddr = self.serversock.accept()
            print "Connected to client at " + str(clientaddr)
            # And then begin listening for an image request (the value 110)
            self.processCommand(clientsock, clientaddr)

    ###################################################################################
    def processCommand(self, clientsock, clientaddr):
        # Comm.recv just sits and waits until it hears SOMETHING from the client
        commandMessage = comm.recv(clientsock)
        if commandMessage == "getClassInstance":
            # If that's "Get Class" it should be immediately followed by a class definition
            className = comm.recv(clientsock)
            # Get an instance of that class (it should already exist, but if it doesn't GetClassInstance will try to create it)
            classInstance = self.getClassInstance(className)
            # Then return the instance to the client
            comm.send(clientsock, classInstance)
        elif commandMessage == "saveClassInstance":
            # If that's "Save Class" it should be immediately followed by a remote system path, then the class instance
            modulePaths = comm.recv(clientsock)
            classInstance = comm.recv(clientsock)
            # Save that instance (overwriting any existing instances of the same class)
            self.saveClassInstance(modulePaths, classInstance)
        elif commandMessage == "break":
            self.dying = True

    ###################################################################################
    def getClassInstance(self, className):
        if className in self.classInstances.keys():
            return self.classInstances[className]
        else:
            return None

    ###################################################################################
    def saveClassInstance(self, modulePaths, remoteClassInstance):
        for item in modulePaths:
            if not item in sys.path:
                sys.path.append(item)
        self.classInstances[remoteClassInstance.__class__.__name__] = remoteClassInstance

#######################################################################################
if __name__ == "__main__":
    server = ClassServer()
