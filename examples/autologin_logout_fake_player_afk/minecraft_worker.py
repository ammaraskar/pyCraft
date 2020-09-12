#!/usr/bin/env python

import json
import time

import sys
from options import get_options
import client_start_connection

from minecraft.networking.packets import Packet, clientbound, serverbound

class main():
    def __init__(self):
        options = get_options()
        
        def print_chat(chat_packet):
            text =  json.loads(chat_packet.json_data)['extra'][0]['text']
            print(text)

        def handle_movement(packet):
            print(packet.x)
            print(packet.y)
            print(packet.z)


        def handle_health(packet):
            print(packet.health)
            print(packet.food)
            print(packet.food_saturation)


        def handle_time(packet):
            #Used for shutdown the bot for sleep on beds ;)
            # Note: you must input masteruser variable
            timeMinecraft = packet.time_of_day % 24000

            if ( (timeMinecraft>=0) and (timeMinecraft<=12040) or (timeMinecraft>=23961) and (timeMinecraft<=24000) ):
                timeDn='Day'
            else:
                timeDn='Night'

            if (options.masteruser in playersOnline.values()) and timeDn == 'Night':
                print('Is Night and Master is Online -> Auto Logout for 15 secs')
                playersOnline.clear()
                time.sleep(1)
                self.connection.disconnect()
                time.sleep(2)
                startConection()

        def handle_players(packet):
            if packet.action_type.__name__ == 'AddPlayerAction':
                print('New user logged: ' + packet.actions[0].name)
                uuid = packet.actions[0].uuid
                playersOnline[packet.actions[0].uuid] =packet.actions[0].name

            if packet.action_type.__name__ == 'RemovePlayerAction':
                print('User dissconnected: ' + packet.actions[0].uuid)
                playersOnline.pop(packet.actions[0].uuid)



        def startConection():
            print("Start connection")
            self.connection = client_start_connection.start(options)
            self.connection.register_packet_listener(print_chat, clientbound.play.ChatMessagePacket)
            #self.connection.register_packet_listener(handle_movement,clientbound.play.PlayerPositionAndLookPacket)
            #self.connection.register_packet_listener(handle_health,clientbound.play.UpdateHealthPacket)
            self.connection.register_packet_listener(handle_time,clientbound.play.TimeUpdatePacket)
            self.connection.register_packet_listener(handle_players,clientbound.play.PlayerListItemPacket)

        playersOnline = {}
        startConection()

        while True:
            try:
                text = input()
                if text == "/respawn":
                    print("respawning...")
                    packet = serverbound.play.ClientStatusPacket()
                    packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                    self.connection.write_packet(packet)
                else:
                    packet = serverbound.play.ChatPacket()
                    packet.message = text
                    self.connection.write_packet(packet)
            except KeyboardInterrupt:
                print("Bye!")
                sys.exit()



if __name__== '__main__':
    main()
