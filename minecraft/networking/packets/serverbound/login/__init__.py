from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, Boolean, String, VarIntPrefixedByteArray, TrailingByteArray
)


# Formerly known as state_login_serverbound.
def get_packets(context):
    packets = {
        LoginStartPacket,
        EncryptionResponsePacket
    }
    if context.protocol_version >= 385:
        packets |= {
            PluginResponsePacket
        }
    return packets


class LoginStartPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x00 if context.protocol_version >= 391 else \
               0x01 if context.protocol_version >= 385 else \
               0x00

    packet_name = "login start"
    definition = [
        {'name': String}]


class EncryptionResponsePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x01 if context.protocol_version >= 391 else \
               0x02 if context.protocol_version >= 385 else \
               0x01

    packet_name = "encryption response"
    definition = [
        {'shared_secret': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]


class PluginResponsePacket(Packet):
    """ NOTE: see comments on 'clientbound.login.PluginRequestPacket' for
        important information on the usage of this packet.
    """

    @staticmethod
    def get_id(context):
        return 0x02 if context.protocol_version >= 391 else \
               0x00

    packet_name = 'login plugin response'
    fields = (
        'message_id',  # str
        'successful',  # bool
        'data',        # bytes, or None if 'successful' is False
    )

    def read(self, file_object):
        self.message_id = VarInt.read(file_object)
        self.successful = Boolean.read(file_object)
        if self.successful:
            self.data = TrailingByteArray.read(file_object)
        else:
            self.data = None

    def write_fields(self, packet_buffer):
        VarInt.send(self.message_id, packet_buffer)
        successful = getattr(self, 'data', None) is not None
        successful = getattr(self, 'successful', successful)
        Boolean.send(successful, packet_buffer)
        if successful:
            TrailingByteArray.send(self.data, packet_buffer)
