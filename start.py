import getpass
import sys
import Utils
from pluginloader import PluginLoader
from networking import PacketSenderManager, NetworkManager
from optparse import OptionParser
try:
    import colorama
    colorama.init()
except ImportError:
    pass

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username", default="",
        help="username to log in with")

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

    # pluginLoader
    pluginLoader = PluginLoader("plugins")
    pluginLoader.loadPlugins(parser)

    (options, args) = parser.parse_args()

    pluginLoader.notifyOptions(options)

    if (options.username != ""):
        user = options.username
    else:
        user = raw_input("Enter your username: ")
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
    connection = NetworkManager.ServerConnection(pluginLoader, user, sessionid, host, port, options)
    connection.setDaemon(True)
    connection.start()
    while True:
        try:
            chat_input = raw_input()
            if (connection.isConnected):
                PacketSenderManager.send03(connection.grabSocket(), chat_input.decode('utf-8'))
            else:
                pass
        except KeyboardInterrupt, e:
            connection.disconnect()
            pluginLoader.disablePlugins()
            sys.exit(1)
