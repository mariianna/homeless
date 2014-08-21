import __builtin__, os, string, StringIO, sys, thread, time, traceback, xbmc, xbmcgui
import EventHandler, typewriter

RootDir = os.getcwd().replace( ";", "" )

NUM_LINES = 25

g = globals()
l = locals()

#######################################################################################
class MyClass(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(4)

        # Initialize class variables
        self.typewriter = typewriter.Typewriter()
        self.commandListIndex = 0
        self.commandList = []
        self.promptPos = 0
        self.cursorPos = 0
        self.overwrite = False
        self.multiline = False
        
        # Redirect stdout to print to our client
        self.text = NewOut()
        sys.stdout = self.text
        sys.displayhook = self.text.display

        # Set up the GUI
        self.pic = xbmcgui.ControlImage(0,0,0,0, os.path.join(RootDir, "background.png"))   # (0,0,0,0) Makes it draw the image full size, starting at the top left
        self.addControl(self.pic)
        self.textBox = xbmcgui.ControlTextBox(9,36,686,436)
        self.addControl(self.textBox)

        # Then activate the command prompt
        self.getInput()
        thread.start_new_thread(self.startBlinker, ())

    ###################################################################################
    def onAction(self, action):
        EventHandler.onAction(self, action)

    ###################################################################################
    def screenSize(self):
        #for i in range(30):
        #    line = str(i + 1)
        #    if i == 0: line += " " + str(self.getHeight())
        #    self.chatOut(line)
        print self.text.write(("W" * 76) + "\n")

    ###################################################################################
    def getInput(self):
        if self.multiline:
            self.text.write("...")
            self.cursorPos = len(self.text.getvalue()[self.promptPos:])
        else:
            self.text.write(">>>")
            self.promptPos = len(self.text)
            self.cursorPos = 0
        self.idle = True

    ###################################################################################
    def startBlinker(self):
        self.dying = False
        self.cursorOn = False
        while True:
            self.blink()
            if self.dying: break
            time.sleep(0.3)
            if self.dying: break
            
    ###################################################################################
    def blink(self):
        if self.idle:
            text = self.text.getvalue()
            self.cursorOn = not self.cursorOn
            if self.cursorOn:
                if self.overwrite:
                    text = text[:self.promptPos + self.cursorPos] + "[]" + text[self.promptPos + self.cursorPos + 1:]
                else:
                    text = text[:self.promptPos + self.cursorPos] + "_" + text[self.promptPos + self.cursorPos:]
            else:
                if not self.overwrite:
                    text = text[:self.promptPos + self.cursorPos] + " " + text[self.promptPos + self.cursorPos:]
            self.textBox.setText(text)

    ###################################################################################
    def close(self):
        self.dying = True
        time.sleep(1)
        xbmcgui.Window.close(self)

    ###################################################################################
    def getCommandLine(self):
        self.idle = False
        command = self.text.getvalue()[self.promptPos:].strip()
        if command and not command.endswith("\n..."):
            if command.find("\n") > -1:
                saveCommand = command.split("\n")[-1][3:]
            else:
                saveCommand = command
            if not saveCommand in self.commandList:
                self.commandList.append(saveCommand)
                self.commandListIndex = 0
        if command.endswith(":") or (self.multiline and not command.endswith("\n...")):
            self.multiline = True
        else:
            if self.multiline:
                command = command.replace("\n...", "\n")
            try:
                exec(command, g, l)
            except Exception:
                self.printError(sys.exc_info())
            self.multiline = False
        self.getInput()

    ###################################################################################
    def printError(self, exception):
        name = exception[0].__name__
        if exception[1].__dict__.has_key("args"):
            name += ": " + str(exception[1].__dict__["args"][0])#string.join(exception[1].__dict__["args"])
        self.text.write(name + "\n")
        #trace = "Traceback (most recent call last):\n" + string.join(traceback.format_tb(exception[2]), "\n")
        #self.text.write(trace + "\n")

#######################################################################################
class NewOut:
    def __init__(self):
        self.text = StringIO.StringIO()

    def __len__(self):
        return len(self.text.getvalue())

    def reset(self):
        self.text = StringIO.StringIO()
    
    def getvalue(self):
        return self.text.getvalue()

    def write(self, text):
        #oldout.write(text)
        self.text.write(text)

    def display(self, item):
        if item is not None:
            __builtin__._ = item
            self.write(str(item))

#######################################################################################
oldout = sys.stdout
olderr = sys.stderr
win = MyClass()
win.doModal()
del win
sys.stdout = oldout
sys.stderr = olderr