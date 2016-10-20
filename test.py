import getpass
import sys
from optparse import OptionParser

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import ChatMessagePacket, ChatPacket
from minecraft.compat import input


def get_options():
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username", default=None,
                      help="username to log in with")

    parser.add_option("-p", "--password", dest="password", default=None,
                      help="password to log in with")

    parser.add_option("-s", "--server", dest="server", default=None,
                      help="server to connect to")

    parser.add_option("-o", "--offline", dest="offline", action="store_true",
                      help="connect to a server in offline mode")

    (options, args) = parser.parse_args()

    if not options.username:
        options.username = input("Enter your username: ")

    if not options.password and not options.offline:
        options.password = getpass.getpass("Enter your password: ")

    if not options.server:
        options.server = input("Please enter server address"
                               " (including port): ")
    # Try to split out port and address
    if ':' in options.server:
        server = options.server.split(":")
        options.address = server[0]
        options.port = int(server[1])
    else:
        options.address = options.server
        options.port = 25565

    return options


def main():
    #options = get_options()
    username = input('Enter username! ')
    address, port = input('Enter address and port! ').split(':')
    print("Connecting in offline mode")
    connection = Connection(
        address, int(port), username=username)
    connection.connect()

    def print_chat(chat_packet):
        print("Position: " + str(chat_packet.position))
        print("Data: " + chat_packet.json_data)

    connection.register_packet_listener(print_chat, ChatMessagePacket)
    while True:
        try:
            text = input()
            packet = ChatPacket()
            packet.message = text
            connection.write_packet(packet)
        except KeyboardInterrupt:
            print("Bye!")
            sys.exit()


if __name__ == "__main__":
    main()