The script contained in this file is designed to provide a background server that 
holds persistent objects in memory and makes them available (via socket connections) 
to other client scripts and plugins. Please note that Persistence is an advanced 
developer's tool because it is useless as a standalone script, and any plugins or 
scripts that connect to it must be configured properly to act as clients.

In order for the script to run properly, "Persistence.py" should be copied to your 
XBMC installation's "/scripts/Persistence/" subfolder, along with the other Python 
files script included in this distribution, "Unpersist.py". You will also need to 
copy "ClassHandler.py" into the folder of the plugin or script you want to use as a 
client. 

In addition to the Persistence files, you'll need to copy the attached "comm.py" to 
either the "/scripts/Persistence/" folder AND your client's folder, or to your XBMC's 
"/python/Lib/" subfolder. I recommend the latter, as that will make the single file 
available to both the client and the server.

This distribution also includes a pair of test files, "TestClient.py" and 
"default.py." These files are dummy clients used for development purposes. If you're 
not interested in modifying the Persistence server, you can ignore or delete these 
files. (To run them, import TestClient from a command-line Python interpreter and 
create a client instance with the command "client = TestClient.TestClient()" or 
move "default.py" (along with "TestClient.py" and "comm.py") into a folder in your 
XBMC's "/plugins/Videos/" subfolder and launch it as a plugin.)

In order to use Persistence, simply launch it from the script launcher. The word 
"(Running)" will appear next to the script's name to let you know the server is now 
active. Any add-ons that have been configured as Persistence scripts should be able 
to connect to it automatically. To close the server, run the companion script 
Unpersist from the script launcher.

For detailed instructions on configuring a script or plugin as a Persistence client, 
check out the tutorial on the XBMC Online Manual:
http://xbmc.org/wiki/?title=HOW-TO:_Optimize_Load_Time_of_Plugins_with_Persistence_Scripts

There are several known issues with the Persistence server. You MUST run Unpersist 
to interrupt the server before closing XBMC, or the whole application will lock up. 
Also, repeated calls to the server can generate an "Access violation" error in the 
C engine that I haven't been able to track down yet. I'm hoping releasing this early 
version of the code will get me feedback from more experienced programmers, so I can 
track that down.

In the meantime, consider this script in development, and please give me all your 
complaints and comments! The more feedback I get, the better I can make the script 
run. There'll be a thread devoted to this topic on the XBMC Python scripting forums, 
and you can also email me at the address listed on my website.

Please check back at my website frequently for updates! I'm constantly trying to make 
these things better.

Visit my website: http://www.maskedfox.com/xbmc/