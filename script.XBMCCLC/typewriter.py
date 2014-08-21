NORMAL_CHARACTERS = {
                        # Control Characters
                        61449: "Tab",
                        61472: " ", 
                        61600: "Shift",
                        61601: "Shift",

                        # Alphabet
                        61505: "a",
                        61506: "b",
                        61507: "c",
                        61508: "d",
                        61509: "e",
                        61510: "f",
                        61511: "g",
                        61512: "h",
                        61513: "i",
                        61514: "j",
                        61515: "k",
                        61516: "l",
                        61517: "m",
                        61518: "n",
                        61519: "o",
                        61520: "p",
                        61521: "q",
                        61522: "r",
                        61523: "s",
                        61524: "t",
                        61525: "u",
                        61526: "v",
                        61527: "w",
                        61528: "x",
                        61529: "y",
                        61530: "z",

                        # Numbers
                        61536: "0",
                        61537: "1",
                        61538: "2",
                        61539: "3",
                        61540: "4",
                        61541: "5",
                        61542: "6",
                        61543: "7",
                        61544: "8",
                        61545: "9",

                        # Punctuation and Special Characters
                        61632: "`",
                        61629: "-",
                        61627: "=",
                        61675: "[",
                        61677: "]",
                        #616xx: "\",
                        61626: ";",
                        61678: "'",
                        61628: ",",
                        61630: ".",
                        61631: "/"
                    }

SHIFTED_CHARACTERS = {
                        # Control Characters
                        61449: "Tab",
                        61472: " ", 
                        #61xxx: "Caps Lock",
                        61600: "Shift",
                        61601: "Shift",
                        #61xxx: "Ctrl",
                        #61xxx: "Alt",

                        # Alphabet
                        61505: "A",
                        61506: "B",
                        61507: "C",
                        61508: "D",
                        61509: "E",
                        61510: "F",
                        61511: "G",
                        61512: "H",
                        61513: "I",
                        61514: "J",
                        61515: "K",
                        61516: "L",
                        61517: "M",
                        61518: "N",
                        61519: "O",
                        61520: "P",
                        61521: "Q",
                        61522: "R",
                        61523: "S",
                        61524: "T",
                        61525: "U",
                        61526: "V",
                        61527: "W",
                        61528: "X",
                        61529: "Y",
                        61530: "Z",

                        # Numbers
                        61536: ")",
                        61537: "!",
                        61538: "@",
                        61539: "#",
                        61540: "$",
                        61541: "%",
                        61542: "^",
                        61543: "&",
                        61544: "*",
                        61545: "(",

                        # Punctuation and Special Characters
                        61632: "~",
                        61629: "_",
                        61627: "+",
                        61675: "{",
                        61677: "}",
                        #616xx: "|",
                        61626: ":",
                        61678: '"',
                        61628: "<",
                        61630: ">",
                        61631: "?"
                    }

class Typewriter:
    def __init__(self):
        self.num_lock = False
        self.caps_lock = False
        self.shift = False
        self.ctrl = False
        self.alt = False
        self.tab_size = 4
        
    def getChar(self, buttonCode):
        if buttonCode in NORMAL_CHARACTERS.keys():
            if NORMAL_CHARACTERS[buttonCode] == "Shift":
                self.shift = not self.shift
                return ""
            elif NORMAL_CHARACTERS[buttonCode] == "Tab":
                return " " * self.tab_size
            else:
                if self.shift:
                    self.shift = False
                    return SHIFTED_CHARACTERS[buttonCode]    
                else:
                    return NORMAL_CHARACTERS[buttonCode]    
        else:
            return "bc" + str(buttonCode)