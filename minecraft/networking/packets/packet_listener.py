from .packet import Packet


class PacketListener(object):
    def __init__(self, callback, *args):
        self.callback = callback
        self.packets_to_listen = [arg for arg in args if issubclass(arg, Packet)]

    def call_packet(self, packet):
        for packet_type in self.packets_to_listen:
            if isinstance(packet, packet_type):
                self.callback(packet)
                return True
        return False
