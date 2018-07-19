from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, String, VarIntPrefixedByteArray, TrailingByteArray
)


# Formerly known as state_login_clientbound.
def get_packets(context):
    packets = {
        DisconnectPacket,
        EncryptionRequestPacket,
        LoginSuccessPacket,
        SetCompressionPacket,
    }
    if context.protocol_version >= 385:
        packets |= {
            PluginRequestPacket,
        }
    return packets


class DisconnectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x00 if context.protocol_version >= 391 else \
               0x01 if context.protocol_version >= 385 else \
               0x00

    packet_name = "disconnect"
    definition = [
        {'json_data': String}]


class EncryptionRequestPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x01 if context.protocol_version >= 391 else \
               0x02 if context.protocol_version >= 385 else \
               0x01

    packet_name = "encryption request"
    definition = [
        {'server_id': String},
        {'public_key': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]


class LoginSuccessPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x02 if context.protocol_version >= 391 else \
               0x03 if context.protocol_version >= 385 else \
               0x02

    packet_name = "login success"
    definition = [
        {'UUID': String},
        {'Username': String}]


class SetCompressionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x03 if context.protocol_version >= 391 else \
               0x04 if context.protocol_version >= 385 else \
               0x03

    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]


class PluginRequestPacket(Packet):
    """ NOTE: pyCraft's default behaviour on receiving a 'PluginRequestPacket'
        is to send a corresponding 'PluginResponsePacket' with
        'successful=False'. To override this, set a packet listener that:

          (1) has the keyword argument 'early=True' set when calling
              'register_packet_listener'; and

          (2) raises 'minecraft.networking.connection.IgnorePacket' after
              sending a corresponding 'PluginResponsePacket'.

        Otherwise, one 'PluginRequestPacket' may result in multiple responses,
        which contravenes Minecraft's protocol.
    """

    @staticmethod
    def get_id(context):
        return 0x04 if context.protocol_version >= 391 else \
               0x00

    packet_name = 'login plugin request'
    definition = [
        {'message_id': VarInt},
        {'channel': String},
        {'data': TrailingByteArray}]
