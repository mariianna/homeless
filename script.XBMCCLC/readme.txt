XBMC Command-Line Client (XBMC-CLC) exposes the XBMC Python interpreter
to a command-prompt, for quick execution and debugging of Python code 
within the XBMC Python environment.

The initial version of this script is very much a rough development build.
It uses button IDs in the onAction to capture keyboard input, but it cannot
suppress XBMC responses to these keypresses (which results in some strange 
behavior). XBMC also does not register key-up events, so it's impossible to 
properly monitor behavior of modifier keys such as Shift and Ctrl. These 
currently act as single-instance toggles (so if you press and hold shift and 
then type "true," only the first letter will be capitalized).

Also, I'm using a TextBox control to contain the printout, but I don't have 
an easy way to recognize how many lines are in it, so I can't scroll up and 
down. That means, for now, after you hit 25 lines of text, the program 
essentially becomes useless. 

Also...something about the way I'm using exec() means I don't get return 
values, so they are no printed to the command line as you would expect. 
So calling dir() on a module would end up looking like this:

>>>import xbmcplugin
>>>dir(xbmcplugin)
>>>

In the normal interpreter, of course, that would print out the results. 
You can still get that effect by typing 'print dir(xbmcplugin),' but 
that's not standard behavior so I'm working on resolving it.

I'm working on fixing these issues, obviously, but I wanted to release 
the script to developers now that it's almost functional so I can start 
getting feedback from some of the other great XBMC Python programmers. 
I'll start a release thread on the XBMC Python Development Forum, and I 
welcome any and all feedback there.

I'll also develop a rough how-to and some better documentation for the 
script's status on my website:

http://www.maskedfox.com/xbmc/