import getpass
import sys
from optparse import OptionParser
import authentication

PROTOCOL_VERSION = 5

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

    login_response = authentication.login_to_minecraft(options.username, options.password)
    from pprint import pprint # TODO: remove debug
    pprint(vars(login_response)) # TODO: remove debug

    if login_response.error:
        print login_response.human_error
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

    from network.connection import Connection
    connection = Connection(address, port, login_response)
    connection.status()

    while True:
        try:
            text = raw_input()
        except KeyboardInterrupt:
            print "Bye!"
            sys.exit()


if __name__ == "__main__":
    main()