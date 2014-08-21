import os, thread, time
import ClassHandler

# Type below the port you want to use to exchange data (probably shouldn't be a port you're forwarding for anything else).
class TestClass:
    def __init__(self, testValue = 0):
        self.testValue = testValue
        print "Generating test class instance...",
        time.sleep(10)
        print "Done!"

    def testFunction(self):
        print "Test Value:", self.testValue        

class TestClient:
    def __init__(self):
        self.handler = ClassHandler.ClassHandler()
        # The following lines grab an existing instance of the class if it exists, or makes a new instance if not.
        if self.handler.exists(TestClass):
            self.classInstance = self.handler.exists(TestClass)
        else:
            self.classInstance = self.handler.new(TestClass, ())

        #  Notes:
        #  A cleaner way to write the same logic is this:
        #self.classInstance = self.handler.exists(TestClass) or self.handler.new(TestClass, ())

        #  You could also FORCE a new instance using just this line:
        #self.classInstance = self.handler.new(TestClass, ())
        
    def changeClassInstance(self, value):
        # Update the instance from the server
        self.handler.update(self.classInstance)
        # Then print out its initial testValue
        print "Before:"
        self.classInstance.testFunction()
        self.classInstance.testValue = value
        print "After (local):"
        self.classInstance.testFunction()
        
        # Then save local changes to the server
        self.handler.save(self.classInstance)
        # And reacquire the remote version of the instance, to make sure our changes persisted
        self.handler.update(self.classInstance)
        print "After (remote):"
        self.classInstance.testFunction()
        