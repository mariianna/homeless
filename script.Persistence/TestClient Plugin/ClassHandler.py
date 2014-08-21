import os
import comm
from socket import socket, gethostname, AF_INET, SOCK_STREAM

# Type below the port you want to use to exchange data.
commport = 51999

#######################################################################################
class ClassHandler:
    def __init__(self, modulePaths = None):
        self.modulePaths = modulePaths or os.getcwd()
        self.classInstances = {}
        
    ###################################################################################
    def connect(self):
        host = gethostname()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, commport))
        return sock

    ###################################################################################
    def getClassInstance(self, className):
        sock = self.connect()
        # Request instance of TestClass above
        comm.send(sock, "getClassInstance")
        # After a "getClassInstance" request, we must provide a class name
        comm.send(sock, className)
        # Then we receive back the remote instance of that class
        classInstance = comm.recv(sock)
        sock.close()
        return classInstance

    ###################################################################################
    def exists(self, classDefinition):
        return self.getClassInstance(classDefinition.__name__)

    ###################################################################################
    def new(self, classDefinition, initArgs):
        classInstance = classDefinition(*initArgs)
        self.save(classInstance)
        return classInstance

    ###################################################################################
    def update(self, classInstance):
        self.classInstances[classInstance.__class__.__name__] = self.getClassInstance(classInstance.__class__.__name__)

    ###################################################################################
    def save(self, classInstance):
        if not classInstance.__class__.__name__ in self.classInstances.keys():
            self.classInstances[classInstance.__class__.__name__] = classInstance

        # Inform the server we have updates to the local class
        sock = self.connect()
        comm.send(sock, "saveClassInstance")
        # After a "Save Class" request, we must provide modulePaths (for importing modules) and then the class instance
        comm.send(sock, self.modulePaths)
        comm.send(sock, classInstance)
        sock.close()