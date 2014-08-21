BUTTON_CTRL_Z = 61602
BUTTON_CTRL_D = 61603

BUTTON_ESCAPE = 61467
BUTTON_BACKSPACE = 61448
BUTTON_ENTER = 61453

BUTTON_END = 61475
BUTTON_HOME = 61476
BUTTON_LEFT = 61477
BUTTON_UP = 61478
BUTTON_RIGHT = 61479
BUTTON_DOWN = 61480
#BUTTON_CTRL_LEFT = 61477
#BUTTON_CTRL_RIGHT = 61479
BUTTON_INSERT = 61485
BUTTON_DELETE = 61486

###################################################################################
def onAction(self, action):
    bc = action.getButtonCode()
    allText = self.text.getvalue()
    if bc == BUTTON_CTRL_Z or bc == BUTTON_CTRL_D:
        self.close()
    elif bc == BUTTON_ESCAPE:
        if self.multiline:
            text = allText[:-len(allText.split("\n...")[-1])]
        else:
            text = allText[:self.promptPos]
        self.text.reset()
        self.text.write(text)
    elif bc == BUTTON_BACKSPACE:
        if self.multiline:
            bumper = (len(allText)-self.promptPos)-len(allText.split("\n...")[-1])
        else:
            bumper = 0
        if self.cursorPos > bumper:
            text = allText

            if self.promptPos + self.cursorPos == len(self.text):
                text = text[:-1]
            else:
                text = text[:self.promptPos + self.cursorPos - 1] + text[self.promptPos + self.cursorPos:]
            self.text.reset()
            self.text.write(text)
            self.cursorPos -= 1

    elif bc == BUTTON_END:
        if self.promptPos + self.cursorPos < len(self.text):
            self.cursorPos = len(self.text) - self.promptPos
    elif bc == BUTTON_HOME:
        if self.cursorPos > 0:
            self.cursorPos = 0
    elif bc == BUTTON_LEFT:
        if self.cursorPos > 0:
            self.cursorPos -= 1
    elif bc == BUTTON_UP:
        text = allText[:self.promptPos]
        self.text.reset()
        self.text.write(text)
        if self.commandListIndex < len(self.commandList):
            self.commandListIndex += 1
        if self.commandListIndex > 0:
            self.text.write(self.commandList[-self.commandListIndex])
            self.cursorPos = len(self.commandList[-self.commandListIndex])
    elif bc == BUTTON_RIGHT:
        if self.promptPos + self.cursorPos < len(self.text):
            self.cursorPos += 1
    elif bc == BUTTON_DOWN:
        if self.commandList:
            text = allText[:self.promptPos]
            self.text.reset()
            self.text.write(text)
            if self.commandListIndex > 1:
                self.commandListIndex -= 1
            self.text.write(self.commandList[-self.commandListIndex])
            self.cursorPos = len(self.commandList[-self.commandListIndex])
    elif bc == BUTTON_INSERT:
        self.overwrite = not self.overwrite
        
    elif bc == BUTTON_ENTER:
        self.text.write("\n")
        self.getCommandLine()
    else:
        new = self.typewriter.getChar(bc)
        if self.promptPos + self.cursorPos == len(self.text):
            self.text.write(new)
        else:
            text = allText
            if self.overwrite:
                text = text[:self.promptPos + self.cursorPos] + new + text[self.promptPos + self.cursorPos + 1:]
            else:
                text = text[:self.promptPos + self.cursorPos] + new + text[self.promptPos + self.cursorPos:]
            self.text.reset()
            self.text.write(text)
        self.cursorPos += len(new)

