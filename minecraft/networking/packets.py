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
    id = None
    definition = None

    # To define the packet ID, either:
    #  1. Define the attribute `id', of type int, in a subclass; or
    #  2. Override `get_id' in a subclass and return the correct packet ID
    #     for the given ConnectionContext. This is necessary if the packet ID
    #     has changed across protocol versions, for example.
    @classmethod
    def get_id(cls, context):
        return cls.id

    # To define the network data layout of a packet, either:
    #  1. Define the attribute `definition', a list of fields, each of which
    #     is a dict mapping attribute names to data types; or
    #  2. Override `get_definition' in a subclass and return the correct
    #     definition for the given ConnectionContext. This may be necessary
    #     if the layout has changed across protocol versions, for example; or
    #  3. Override the methods `read' and/or `write' in a subclass. This may be
    #     necessary if the packet layout cannot be described as a list of fields.
    @classmethod
    def get_definition(cls, context):
        return cls.definition

    def __init__(self, context=None, **kwargs):
        self.context = context
        self.set_values(**kwargs)

    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, _context):
        self._context = _context
        if _context is not None:
            self.id = self.get_id(_context)
            self.definition = self.get_definition(_context)
        else:
            self.id = None
            self.definition = None

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


def state_handshake_clientbound(context):
    return {
        
    }
def state_handshake_serverbound(context):
    return {
        HandShakePacket
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


def state_status_clientbound(context):
    return {
        ResponsePacket,
        PingPacketResponse,
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


def state_status_serverbound(context):
    return {
        RequestPacket,
        PingPacket
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


def state_login_clientbound(context):
    return {
        DisconnectPacket,
        EncryptionRequestPacket,
        LoginSuccessPacket,
        SetCompressionPacket
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


def state_login_serverbound(context):
    return {
        LoginStartPacket,
        EncryptionResponsePacket
    }


# Playing State
# ==============

class KeepAlivePacket(Packet):
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]

class KeepAlivePacketClientbound(KeepAlivePacket):
     get_id = staticmethod(lambda context:
        0x1F if context.protocol_version >= 107 else
        0x00)

class KeepAlivePacketServerbound(KeepAlivePacket):
     get_id = staticmethod(lambda context:
        0x0B if context.protocol_version >= 107 else
        0x00)

class JoinGamePacket(Packet):
    get_id = staticmethod(lambda context:
        0x23 if context.protocol_version >= 107 else
        0x01)
    packet_name = "join game"
    get_definition = staticmethod(lambda context: [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Integer if context.protocol_version >= 108 else Byte},
        {'difficulty': UnsignedByte},
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'reduced_debug_info': Boolean}])


class ChatMessagePacket(Packet):
    get_id = staticmethod(lambda context:
        0x0F if context.protocol_version >= 107 else
        0x02)
    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]


class PlayerPositionAndLookPacket(Packet):
    get_id = staticmethod(lambda context:
        0x2E if context.protocol_version >= 107 else
        0x08)
    packet_name = "player position and look"
    get_definition = staticmethod(lambda context: [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'flags': Byte},
        {'teleport_id': VarInt} if context.protocol_version >= 107 else {},
    ])

    FLAG_REL_X     = 0x01
    FLAG_REL_Y     = 0x02
    FLAG_REL_Z     = 0x04
    FLAG_REL_YAW   = 0x08
    FLAG_REL_PITCH = 0x10

    class PositionAndLook(object):
        __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'
        def __init__(self, **kwds):
            for attr in self.__slots__:
                setattr(self, attr, kwds.get(attr))

    # Update a PositionAndLook instance using this packet.
    def apply(self, target):
        if self.flags & self.FLAG_REL_X: target.x += self.x
        else: target.x = self.x
        if self.flags & self.FLAG_REL_Y: target.y += self.y
        else: target.y = self.y
        if self.flags & self.FLAG_REL_Z: target.z += self.z
        else: target.z = self.z
        if self.flags & self.FLAG_REL_YAW: target.yaw += self.yaw
        else: target.yaw = self.yaw
        if self.flags & self.FLAG_REL_PITCH: target.pitch += self.pitch
        else: target.pitch = self.pitch
        self.yaw %= 360
        self.pitch %= 360

class DisconnectPacketPlayState(Packet):
    get_id = staticmethod(lambda context:
        0x1A if context.protocol_version >= 107 else
        0x40)
    packet_name = "disconnect"

    definition = [
        {'json_data': String}]


class SetCompressionPacketPlayState(Packet):
    # Note: removed between protocol versions 47 and 107. 
    id = 0x46
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]

class PlayerListItemPacket(Packet):
    get_id = staticmethod(lambda context:
        0x2D if context.protocol_version >= 107 else
        0x38)
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

class MapPacket(Packet):
    get_id = staticmethod(lambda context:
        0x24 if context.protocol_version >= 107 else
        0x34)
    packet_name = 'map'
    
    class MapIcon(object):
        __slots__ = 'type', 'direction', 'location'
        def __init__(self, type, direction, (x, z)):
            self.type = type
            self.direction = direction
            self.location = (x, z)
        def __repr__(self):
            return ('MapIcon(type=%s, direction=%s, location=%s)'
                % (self.type, self.direction, self.location))
        def __str__(self):
            return self.__repr__()

    class Map(object):
        __slots__ = ('id', 'scale', 'icons', 'pixels', 'width', 'height',
                     'is_tracking_position')
        def __init__(self, id=None, scale=None, width=128, height=128):
            self.id = id
            self.scale = scale
            self.icons = []
            self.width = width
            self.height = height
            self.pixels = bytearray(0 for i in range(width*height))
            self.is_tracking_position = True
        def __repr__(self):
            return ('Map(id=%s, scale=%s, icons=%s, width=%s, height=%s)'
                % (self.id, self.scale, self.icons, self.width, self.height))
        def __str__(self):
            return self.__repr__()

    class MapSet(object):
        __slots__ = 'maps_by_id'
        def __init__(self):
            self.maps_by_id = dict()
        def __repr__(self):
            return 'MapSet(%s)' % ', '.join(self.maps_by_id.itervalues())
        def __str__(self):
            return self.__repr__()

    def read(self, file_object):
        self.map_id = VarInt.read(file_object)
        self.scale = Byte.read(file_object)

        if self.context.protocol_version >= 107:
            self.is_tracking_position = Boolean.read(file_object)
        else:
            self.is_tracking_position = True

        icon_count = VarInt.read(file_object)
        self.icons = []
        for i in range(icon_count):
            type, direction = divmod(UnsignedByte.read(file_object), 16)
            x = Byte.read(file_object)
            z = Byte.read(file_object)
            icon = MapPacket.MapIcon(type, direction, (x, z))
            self.icons.append(icon)
        self.width = UnsignedByte.read(file_object)
        if self.width:
            self.height = UnsignedByte.read(file_object)
            x = Byte.read(file_object)
            z = Byte.read(file_object)
            self.offset = (x, z)
            self.pixels = VarIntPrefixedByteArray.read(file_object)
        else:
            self.height = 0
            self.offset = None
            self.pixels = None

    def apply_to_map(self, map):
        map.id = self.map_id
        map.scale = self.scale
        map.icons[:] = self.icons
        if self.pixels is not None:
            for i in range(len(self.pixels)):
                x = self.offset[0] + i % self.width
                z = self.offset[1] + i / self.width
                map.pixels[x + map.width * z] = self.pixels[i]
        map.is_tracking_position = self.is_tracking_position
    
    def apply_to_map_set(self, map_set):
        map = map_set.maps_by_id.get(self.map_id)
        if map is None:
            map = MapPacket.Map(self.map_id)
            map_set.maps_by_id[self.map_id] = map
        self.apply_to_map(map)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

    def __repr__(self):
        return 'MapPacket(%s)' % ', '.join(
            '%s=%r' % (k, v)
            for (k,v) in self.__dict__.iteritems()
            if k != 'pixels')
    def __str__(self):
        return self.__repr__()

def state_playing_clientbound(context):
    packets = {
        KeepAlivePacketClientbound,
        JoinGamePacket,
        ChatMessagePacket,
        PlayerPositionAndLookPacket,
        MapPacket,
        PlayerListItemPacket,
        DisconnectPacketPlayState,
    }
    if context.protocol_version <= 47: packets |= {
        SetCompressionPacketPlayState,
    }
    return packets


class ChatPacket(Packet):
    get_id = staticmethod(lambda context:
        0x02 if context.protocol_version >= 107 else
        0x01)
    packet_name = "chat"
    definition = [
        {'message': String}]


class PositionAndLookPacket(Packet):
    get_id = staticmethod(lambda context:
        0x0D if context.protocol_version >= 107 else
        0x06)
    packet_name = "position and look"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'on_ground': Boolean}]

class TeleportConfirmPacket(Packet):
    # Note: added between protocol versions 47 and 107.
    id = 0x00
    packet_name = "teleport confirm"
    definition = [
        {'teleport_id': VarInt}]

class AnimationPacketServerbound(Packet):
    get_id = staticmethod(lambda context:
        0x1A if context.protocol_version >= 107 else
        0x0A)
    packet_name = "animation"
    get_definition = staticmethod(lambda context: [
        {'hand': VarInt} if context.protocol_version >= 107 else {}])
    HAND_MAIN = 0
    HAND_OFF  = 1

def state_playing_serverbound(context):
    packets = {
        KeepAlivePacketServerbound,
        ChatPacket,
        PositionAndLookPacket,
        AnimationPacketServerbound,
    }
    if context.protocol_version >= 107: packets |= {
        TeleportConfirmPacket,
    }
    return packets
