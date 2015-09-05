from io import BytesIO
from zlib import compress

from .types import (
    VarInt, Integer, Float, Double, UnsignedShort, Long, Byte, UnsignedByte,
    String, VarIntPrefixedByteArray, Boolean, UUID
)


class PacketBuffer(object):
    def __init__(self):
        self.bytes = BytesIO()

    def send(self, value):
        """
        Writes the given bytes to the buffer, designed to emulate socket.send
        :param value: The bytes to write
        """
        self.bytes.write(value)

    def read(self, length):
        return self.bytes.read(length)

    def recv(self, length):
        return self.read(length)

    def reset(self):
        self.bytes = BytesIO()

    def reset_cursor(self):
        self.bytes.seek(0)

    def get_writable(self):
        return self.bytes.getvalue()


class PacketListener(object):
    def __init__(self, callback, *args):
        self.callback = callback
        self.packets_to_listen = []
        for arg in args:
            if issubclass(arg, Packet):
                self.packets_to_listen.append(arg)

    def call_packet(self, packet):
        for packet_type in self.packets_to_listen:
            if isinstance(packet, packet_type):
                self.callback(packet)


class Packet(object):
    packet_name = "base"
    id = -0x01
    definition = []

    def __init__(self, **kwargs):
        pass

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def read(self, file_object):
        for field in self.definition:
            for var_name, data_type in field.items():
                value = data_type.read(file_object)
                setattr(self, var_name, value)

    def write(self, socket, compression_threshold=None):
        # buffer the data since we need to know the length of each packet's
        # payload
        packet_buffer = PacketBuffer()
        # write packet's id right off the bat in the header
        VarInt.send(self.id, packet_buffer)

        for field in self.definition:
            for var_name, data_type in field.items():
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        # compression_threshold of None means compression is disabled
        if compression_threshold is not None:
            if len(packet_buffer.get_writable()) > compression_threshold != -1:
                # compress the current payload
                compressed_data = compress(packet_buffer.get_writable())
                packet_buffer.reset()
                # write out the length of the compressed payload
                VarInt.send(len(compressed_data), packet_buffer)
                # write the compressed payload itself
                packet_buffer.send(compressed_data)
            else:
                # write out a 0 to indicate uncompressed data
                packet_data = packet_buffer.get_writable()
                packet_buffer.reset()
                VarInt.send(0, packet_buffer)
                packet_buffer.send(packet_data)

        VarInt.send(len(packet_buffer.get_writable()), socket)  # Packet Size
        socket.send(packet_buffer.get_writable())  # Packet Payload


# Handshake State
# ==============
class HandShakePacket(Packet):
    id = 0x00
    packet_name = "handshake"
    definition = [
        {'protocol_version': VarInt},
        {'server_address': String},
        {'server_port': UnsignedShort},
        {'next_state': VarInt}]


STATE_HANDSHAKE_CLIENTBOUND = {

}
STATE_HANDSHAKE_SERVERBOUND = {
    0x00: HandShakePacket
}


# Status State
# ==============
class ResponsePacket(Packet):
    id = 0x00
    packet_name = "response"
    definition = [
        {'json_response': String}]


class PingPacketResponse(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]


STATE_STATUS_CLIENTBOUND = {
    0x00: ResponsePacket,
    0x01: PingPacketResponse
}


class RequestPacket(Packet):
    id = 0x00
    packet_name = "request"
    definition = []


class PingPacket(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]


STATE_STATUS_SERVERBOUND = {
    0x00: RequestPacket,
    0x01: PingPacket
}


# Login State
# ==============
class DisconnectPacket(Packet):
    id = 0x00
    packet_name = "disconnect"
    definition = [
        {'json_data': String}]


class EncryptionRequestPacket(Packet):
    id = 0x01
    packet_name = "encryption request"
    definition = [
        {'server_id': String},
        {'public_key': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]


class LoginSuccessPacket(Packet):
    id = 0x02
    packet_name = "login success"
    definition = [
        {'UUID': String},
        {'Username': String}]


class SetCompressionPacket(Packet):
    id = 0x03
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]


STATE_LOGIN_CLIENTBOUND = {
    0x00: DisconnectPacket,
    0x01: EncryptionRequestPacket,
    0x02: LoginSuccessPacket,
    0x03: SetCompressionPacket
}


class LoginStartPacket(Packet):
    id = 0x00
    packet_name = "login start"
    definition = [
        {'name': String}]


class EncryptionResponsePacket(Packet):
    id = 0x01
    packet_name = "encryption response"
    definition = [
        {'shared_secret': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]


STATE_LOGIN_SERVERBOUND = {
    0x00: LoginStartPacket,
    0x01: EncryptionResponsePacket
}


# Playing State
# ==============

class KeepAlivePacket(Packet):
    id = 0x00
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]


class JoinGamePacket(Packet):
    id = 0x01
    packet_name = "join game"
    definition = [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Byte},
        {'difficulty': UnsignedByte},
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'reduced_debug_info': Boolean}]


class ChatMessagePacket(Packet):
    id = 0x02
    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]


class PlayerPositionAndLookPacket(Packet):
    id = 0x08
    packet_name = "player position and look"
    definition = [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'flags': Byte}]


class DisconnectPacketPlayState(Packet):
    id = 0x40
    packet_name = "disconnect"

    definition = [
        {'json_data': String}]


class SetCompressionPacketPlayState(Packet):
    id = 0x46
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]

class PlayerListItemPacket(Packet):
    id = 0x38
    packet_name = "player list item"

    class PlayerList(object):
        __slots__ = 'players_by_uuid'
        def __init__(self):
            self.players_by_uuid = dict()

    class PlayerListItem(object):
        __slots__ = (
            'uuid', 'name', 'properties', 'gamemode', 'ping', 'display_name')
        def __init__(self, **kwds):
            for key, val in kwds.iteritems():
                setattr(self, key, val)

    class PlayerProperty(object):
        __slots__ = 'name', 'value', 'signature'       
        def read(self, file_object):
            self.name = String.read(file_object)
            self.value = String.read(file_object)
            is_signed = Boolean.read(file_object)
            if is_signed:
                self.signature = String.read(file_object)
            else:
                self.signature = None

    class Action(object):
        __slots__ = 'uuid'
        def read(self, file_object):
            self.uuid = UUID.read(file_object)
            self._read(file_object)

        @classmethod
        def type_from_id(cls, action_id):
            subcls = {
                0: PlayerListItemPacket.AddPlayerAction,
                1: PlayerListItemPacket.UpdateGameModeAction,
                2: PlayerListItemPacket.UpdateLatencyAction,
                3: PlayerListItemPacket.UpdateDisplayNameAction,
                4: PlayerListItemPacket.RemovePlayerAction
            }.get(action_id)
            if subcls is None: raise ValueError(
                "Unknown player list action ID: %s." % action_id)
            return subcls
 
    class AddPlayerAction(Action):
        __slots__ = 'name', 'properties', 'gamemode', 'ping', 'display_name'
        def _read(self, file_object):
            self.name = String.read(file_object)
            prop_count = VarInt.read(file_object)
            self.properties = []
            for i in range(prop_count):
                property = PlayerListItemPacket.PlayerProperty()
                property.read(file_object)
                self.properties.append(property)
            self.gamemode = VarInt.read(file_object)
            self.ping = VarInt.read(file_object)
            has_display_name = Boolean.read(file_object)
            if has_display_name:
                self.display_name = String.read(file_object)
            else:
                self.display_name = None
        def apply(self, player_list):
            player = PlayerListItemPacket.PlayerListItem(
                uuid         = self.uuid,
                name         = self.name,
                properties   = self.properties,
                gamemode     = self.gamemode,
                ping         = self.ping,
                display_name = self.display_name)
            player_list.players_by_uuid[self.uuid] = player
            
    class UpdateGameModeAction(Action):
        __slots__ = 'gamemode'
        def _read(self, file_object):
            self.gamemode = VarInt.read(file_object)
        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player: player.gamemode = self.gamemode
    
    class UpdateLatencyAction(Action):
        __slots__ = 'ping'
        def _read(self, file_object):
            self.ping = VarInt.read(file_object)
        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player: player.ping = self.ping

    class UpdateDisplayNameAction(Action):
        __slots__ = 'display_name'
        def _read(self, file_object):
            has_display_name = Boolean.read(file_object)
            if has_display_name:
                self.display_name = String.read(file_object)
            else:
                self.display_name = None
        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player: player.display_name = self.display_name

    class RemovePlayerAction(Action):
        def _read(self, file_object):
            pass
        def apply(self, player_list):
            if self.uuid in player_list.players_by_uuid:
                del player_list.players_by_uuid[self.uuid]

    def read(self, file_object):
        action_id = VarInt.read(file_object)
        self.action_type = PlayerListItemPacket.Action.type_from_id(action_id)
        action_count = VarInt.read(file_object)
        self.actions = []
        for i in range(action_count):
            action = self.action_type()
            action.read(file_object)
            self.actions.append(action)

    def apply(self, player_list):
        for action in self.actions:
            action.apply(player_list)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

STATE_PLAYING_CLIENTBOUND = {
    0x00: KeepAlivePacket,
    0x01: JoinGamePacket,
    0x02: ChatMessagePacket,
    0x08: PlayerPositionAndLookPacket,
    0x38: PlayerListItemPacket,
    0x40: DisconnectPacketPlayState,
    0x46: SetCompressionPacketPlayState
}


class ChatPacket(Packet):
    id = 0x01
    packet_name = "chat"
    definition = [
        {'message': String}]


class PositionAndLookPacket(Packet):
    id = 0x06
    packet_name = "position and look"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'on_ground': Boolean}]

STATE_PLAYING_SERVERBOUND = {
    0x00: KeepAlivePacket,
    0x01: ChatPacket,
    0x06: PositionAndLookPacket
}
