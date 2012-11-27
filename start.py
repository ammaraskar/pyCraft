import getpass
import sys
import Utils
from networking import PacketSenderManager, NetworkManager
from optparse import OptionParser

if __name__ == "__main__":
        
    parser = OptionParser()
    
    parser.add_option("-u", "--username", dest="username", default="",
                  help="username to log in with")
    
    parser.add_option("-p", "--password", dest="password", default="",
                  help="password to log in with")
    
    parser.add_option("-s", "--server", dest="server", default="",
                  help="server to connect to")
    
    parser.add_option("-d", "--dump-packets", 
                  action="store_true", dest="dumpPackets", default=False,
                  help="run with this argument to dump packets")
    
    parser.add_option("-o", "--out-file", dest="filename", default="dump.txt",
                  help="file to dump packets to")
    
    (options, args) = parser.parse_args()
                
    if(options.username != ""):
        user = options.username
    else:
        user = raw_input("Enter your username: ")
    if(options.password != ""):
        passwd = options.password
    else:
        passwd = getpass.getpass("Enter your password: ")
    loginThread = Utils.MinecraftLoginThread(user, passwd)
    loginThread.start()
    loginThread.join()
    derp = loginThread.getResponse()
    if(derp['Response'] != "Good to go!"):
        print derp['Response']
        sys.exit(1)
    sessionid = derp['SessionID']
    print "Logged in as " + derp['Username'] + "! Your session id is: " + sessionid
    if(options.server != ""):
        stuff = options.server
    else:
        stuff = raw_input("Enter host and port if any: ")
    if ':' in stuff:
        StuffEnteredIntoBox = stuff.split(":")
        host = StuffEnteredIntoBox[0]
        port = int(StuffEnteredIntoBox[1])
    else:
        host = stuff
        port = 25565
    connection = NetworkManager.ServerConnection(None, derp['Username'], passwd, sessionid, host, port, options)
    connection.start()
    while True:
        try:
            chat_input = raw_input()
            if (connection.isConnected):
                PacketSenderManager.send03(connection.grabSocket(), chat_input) 
            else:
                pass       
        except KeyboardInterrupt, e:
            connection.disconnect()
            sys.exit(1)
