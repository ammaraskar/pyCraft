import getpass
import sys
from optparse import OptionParser

from minecraft.networking import authentication
from minecraft.networking.connection import Connection
from minecraft.networking.packets import ChatMessagePacket, ChatPacket


def main():
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username", default=None,
                      help="username to log in with")

    parser.add_option("-p", "--password", dest="password", default=None,
                      help="password to log in with")

    parser.add_option("-s", "--server", dest="server", default=None,
                      help="server to connect to")

    (options, args) = parser.parse_args()

    if not options.username:
        options.username = raw_input("Enter your username: ")

    if not options.password:
        options.password = getpass.getpass("Enter your password: ")

    try:
        login_response = authentication.login_to_minecraft(options.username, options.password)
        from pprint import pprint  # TODO: remove debug

        pprint(vars(login_response))  # TODO: remove debug
    except authentication.YggdrasilError as e:
        print e.human_readable_error
        return

    print("Logged in as " + login_response.username)

    if not options.server:
        options.server = raw_input("Please enter server address (including port): ")
    # Try to split out port and address
    if ':' in options.server:
        server = options.server.split(":")
        address = server[0]
        port = int(server[1])
    else:
        address = options.server
        port = 25565

    connection = Connection(address, port, login_response)
    connection.connect()

    def print_chat(chat_packet):
        print "Position: " + str(chat_packet.position)
        print "Data: " + chat_packet.json_data

    connection.register_packet_listener(print_chat, ChatMessagePacket)
    while True:
        try:
            text = raw_input()
            packet = ChatPacket()
            packet.message = text
            connection.write_packet(packet)
        except KeyboardInterrupt:
            print "Bye!"
            sys.exit()


if __name__ == "__main__":
    main()