#!/usr/bin/env python

import re
import getpass
from optparse import OptionParser

def get_options():
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username",
                            default=None,
                            help="username to log in with")

    parser.add_option("-p", "--password", dest="password",
                            default=None,
                            help="password to log in with")

    parser.add_option("-s", "--server", dest="server",
                            default=None,
                            help="server host or host:port "
                        "(enclose IPv6 addresses in square brackets)")

    parser.add_option("-o", "--offline", dest="offline",
                            action="store_true",
                            help="connect to a server in offline mode "
                        "(no password required)")

    parser.add_option("-d", "--dump-packets", dest="dump_packets",
                            action="store_true",
                            help="print sent and received packets to standard error")

    parser.add_option("-a", "--autologin", dest="autologin",
                            default=None,
                            help="use auto /login XX password automatically")
    
    parser.add_option("-m", "--masteruser", dest="masteruser",
                            default=None,
                            help="Is used for receive calls in game")

    parser.add_option("-v", "--dump-unknown-packets", dest="dump_unknown",
                            action="store_true",
                            help="include unknown packets in --dump-packets output")

    (options, args) = parser.parse_args()

    if not options.username:
        options.username = input("Enter your username: ")

    if not options.password and not options.offline:
        options.password = getpass.getpass("Enter your password (leave "
                                        "blank for offline mode): ")
        options.offline = options.offline or (options.password == "")

    if not options.server:
        options.server = input("Enter server host or host:port "
                            "(enclose IPv6 addresses in square brackets): ")

    if not options.autologin:
        options.autologin = input("Enter autologin password "
                            "(blank for offline mode if it is not requiered for the server): ")

    if not options.masteruser:
        options.masteruser = input("Enter master user "
                            "(blank if you no use a master user): ")

    # Try to split out port and address
    match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                    r"(:(?P<port>\d+))?$", options.server)
    if match is None:
        raise ValueError("Invalid server address: '%s'." % options.server)

    options.address = match.group("host") or match.group("addr")

    options.port = int(match.group("port") or 25565)

    return options
