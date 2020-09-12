#!/usr/bin/env python

import sys
import time
import random

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound

import minecraft_worker

def start(options):

    if options.offline:
        print("Connecting in offline mode...")
        connection = Connection(
            options.address, options.port, username=options.username)
    else:
        auth_token = authentication.AuthenticationToken()
        try:
            auth_token.authenticate(options.username, options.password)
        except YggdrasilError as e:
            print("Error encontrado")
            print(e)
            sys.exit()
        print("Logged in as %s..." % auth_token.username)
        connection = Connection(
            options.address, options.port, auth_token=auth_token)

    if options.dump_packets:
        def print_incoming(packet):
            if type(packet) is Packet:
                # This is a direct instance of the base Packet type, meaning
                # that it is a packet of unknown type, so we do not print it
                # unless explicitly requested by the user.
                if options.dump_unknown:
                    print('--> [unknown packet] %s' % packet, file=sys.stderr)
            else:
                print('--> %s' % packet, file=sys.stderr)

        def print_outgoing(packet):
            print('<-- %s' % packet, file=sys.stderr)

        connection.register_packet_listener(
            print_incoming, Packet, early=True)
        connection.register_packet_listener(
            print_outgoing, Packet, outgoing=True)

    def handle_join_game(join_game_packet):
        print('Connected.')
        if options.autologin:
            print("Auto login...")
            text = "/login " + options.autologin
            packet = serverbound.play.ChatPacket()
            packet.message = text
            connection.write_packet(packet)

    def handle_error_conect(error,error_type):
        #If detect error on too many coenctions, try again after X rand secs
        if str(error) == 'The server rejected our login attempt with: "{"translate":"Connection throttled! Please wait before reconnecting."}".':
             timeNext = random.randint(3, 15)
             print("Too many conections, reconecting in: " + str(timeNext)) + " secs."
             time.sleep(timeNext)
             minecraft_worker.main()
        else:
            #if other error -> stops
             print("Error found: ")
             print(error)
             print(error_type)

    connection.register_exception_handler(handle_error_conect)
    connection.register_packet_listener(handle_join_game, clientbound.play.JoinGamePacket)
    connection.connect()
    return connection
