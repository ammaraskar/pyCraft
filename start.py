import getpass
import sys
import Utils
import time
from pluginloader import PluginLoader
from networking import PacketSenderManager, NetworkManager
from optparse import OptionParser
from bots import names
try:
    import colorama
    colorama.init()
except ImportError:
    pass

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-p", "--password", dest="password", default="",
        help="password to log in with")

    parser.add_option("-s", "--server", dest="server", default="",
        help="server to connect to")

    parser.add_option("-x", "--offline-mode", dest="offlineMode",
        action="store_true", default=False,
        help="run in offline mode i.e don't attempt to auth via minecraft.net")

    parser.add_option("-c", "--disable-console-colours", dest="disableAnsiColours",
        action="store_true", default=False,
        help="print minecraft chat colours as their equivalent ansi colours")

    parser.add_option("-b", "--bot-count", dest="bots", default=25, type="int",
        help="the number of bots to connect") 

    parser.add_option("-f", "--fun-bot-names", dest="funBotNames",
        action="store_true", default=False,
        help="use more fun bot names")
        
    parser.add_option("-t", "--throttle", dest="throttle",
        action="store_true", default=False,
        help="throttle bot connections to join 1 per second")

    # pluginLoader
    pluginLoader = PluginLoader("plugins")
    pluginLoader.loadPlugins(parser)

    (options, args) = parser.parse_args()

    pluginLoader.notifyOptions(options)

    if (options.password != ""):
        passwd = options.password
    elif (not options.offlineMode):
        passwd = getpass.getpass("Enter your password: ")

    if (not options.offlineMode):
        loginThread = Utils.MinecraftLoginThread(user, passwd)
        loginThread.start()
        loginThread.join()
        loginResponse = loginThread.getResponse()
        if (loginResponse['Response'] != "Good to go!"):
            print loginResponse['Response']
            sys.exit(1)
        sessionid = loginResponse['SessionID']
        user = loginResponse['Username']
        print "Logged in as " + loginResponse['Username'] + "! Your session id is: " + sessionid
    else:
        sessionid = None

    if (options.server != ""):
        serverAddress = options.server
    else:
        serverAddress = raw_input("Enter host and port if any: ")
    if ':' in serverAddress:
        StuffEnteredIntoBox = serverAddress.split(":")
        host = StuffEnteredIntoBox[0]
        port = int(StuffEnteredIntoBox[1])
    else:
        host = serverAddress
        port = 25565
    ###
    print "Connecting with " + str(options.bots) + " bots"
    connections = []
    for i in range(options.bots):
        if options.throttle:
            time.sleep(1)
        if options.funBotNames and i < len(names):
            name = names[i]
        else:
            name = "bot_" + str(i)
        connection = NetworkManager.ServerConnection(pluginLoader, name, sessionid, host, port, options)
        connection.setDaemon(True)
        connection.start()
        connections.append(connection) 
    ###
    while True:
        try:
            chat_input = raw_input()
            if (connection.isConnected):
                PacketSenderManager.send03(connection.grabSocket(),
                        chat_input.decode('utf-8')[:100])
            else:
                pass
        except KeyboardInterrupt, e:
            ###
            for connection in connections:
                connection.disconnect() 
            ###
            pluginLoader.disablePlugins()
            sys.exit(1)
