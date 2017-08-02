from io import BytesIO
from zlib import compress

from .types import (
    VarInt, Integer, Float, Double, UnsignedShort, Long, Byte, UnsignedByte,
    String, VarIntPrefixedByteArray, Boolean, UUID, Short, UnsignedLong, Position
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

    def read(self, length=None):
        return self.bytes.read(length)

    def recv(self, length=None):
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
    #     necessary if the packet layout cannot be described as a list of
    #     fields.
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
        self._context_changed()

    def _context_changed(self):
        if self._context is not None:
            self.id = self.get_id(self._context)
            self.definition = self.get_definition(self._context)
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

    # Writes a packet buffer to the socket with the appropriate headers
    # and compressing the data if necessary
    def _write_buffer(self, socket, packet_buffer, compression_threshold):
        # compression_threshold of None means compression is disabled
        if compression_threshold is not None:
            if len(packet_buffer.get_writable()) > compression_threshold != -1:
                # compress the current payload
                packet_data = packet_buffer.get_writable()
                compressed_data = compress(packet_data)
                packet_buffer.reset()
                # write out the length of the uncompressed payload
                VarInt.send(len(packet_data), packet_buffer)
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

    def write(self, socket, compression_threshold=None):
        # buffer the data since we need to know the length of each packet's
        # payload
        packet_buffer = PacketBuffer()
        # write packet's id right off the bat in the header
        VarInt.send(self.id, packet_buffer)
        # write every individual field
        for field in self.definition:
            for var_name, data_type in field.items():
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        self._write_buffer(socket, packet_buffer, compression_threshold)

    def __str__(self):
        str = type(self).__name__
        if self.id is not None:
            str = '0x%02X %s' % (self.id, str)
        if self.definition is not None:
            fields = {a: getattr(self, a) for d in self.definition for a in d}
            str = '%s %s' % (str, fields)
        return str


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
    @staticmethod
    def get_id(context):
        return 0x1F if context.protocol_version >= 332 else \
               0x20 if context.protocol_version >= 318 else \
               0x1F if context.protocol_version >= 107 else \
               0x00


class KeepAlivePacketServerbound(KeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 336 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 107 else \
               0x00


class JoinGamePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x23 if context.protocol_version >= 332 else \
               0x24 if context.protocol_version >= 318 else \
               0x23 if context.protocol_version >= 107 else \
               0x01

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
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_version >= 332 else \
               0x10 if context.protocol_version >= 317 else \
               0x0F if context.protocol_version >= 107 else \
               0x02

    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]


class PlayerPositionAndLookPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x2F if context.protocol_version >= 336 else \
               0x2E if context.protocol_version >= 318 else \
               0x2F if context.protocol_version >= 107 else \
               0x08

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

    FLAG_REL_X = 0x01
    FLAG_REL_Y = 0x02
    FLAG_REL_Z = 0x04
    FLAG_REL_YAW = 0x08
    FLAG_REL_PITCH = 0x10

    class PositionAndLook(object):
        __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

        def __init__(self, **kwds):
            for attr in self.__slots__:
                setattr(self, attr, kwds.get(attr))

    # Update a PositionAndLook instance using this packet.
    def apply(self, target):
        # pylint: disable=no-member
        if self.flags & self.FLAG_REL_X:
            target.x += self.x
        else:
            target.x = self.x

        if self.flags & self.FLAG_REL_Y:
            target.y += self.y
        else:
            target.y = self.y

        if self.flags & self.FLAG_REL_Z:
            target.z += self.z
        else:
            target.z = self.z

        if self.flags & self.FLAG_REL_YAW:
            target.yaw += self.yaw
        else:
            target.yaw = self.yaw

        if self.flags & self.FLAG_REL_PITCH:
            target.pitch += self.pitch
        else:
            target.pitch = self.pitch

        target.yaw %= 360
        target.pitch %= 360


class DisconnectPacketPlayState(Packet):
    @staticmethod
    def get_id(context):
        return 0x1A if context.protocol_version >= 332 else \
               0x1B if context.protocol_version >= 318 else \
               0x1A if context.protocol_version >= 107 else \
               0x40

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
    @staticmethod
    def get_id(context):
        return 0x2E if context.protocol_version >= 336 else \
               0x2D if context.protocol_version >= 332 else \
               0x2E if context.protocol_version >= 318 else \
               0x2D if context.protocol_version >= 107 else \
               0x38

    packet_name = "player list item"

    class PlayerList(object):
        __slots__ = 'players_by_uuid'

        def __init__(self):
            self.players_by_uuid = dict()

    class PlayerListItem(object):
        __slots__ = (
            'uuid', 'name', 'properties', 'gamemode', 'ping', 'display_name')

        def __init__(self, **kwds):
            for key, val in kwds.items():
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

        def _read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        @classmethod
        def type_from_id(cls, action_id):
            subcls = {
                0: PlayerListItemPacket.AddPlayerAction,
                1: PlayerListItemPacket.UpdateGameModeAction,
                2: PlayerListItemPacket.UpdateLatencyAction,
                3: PlayerListItemPacket.UpdateDisplayNameAction,
                4: PlayerListItemPacket.RemovePlayerAction
            }.get(action_id)
            if subcls is None:
                raise ValueError("Unknown player list action ID: %s."
                                 % action_id)
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
                uuid=self.uuid,
                name=self.name,
                properties=self.properties,
                gamemode=self.gamemode,
                ping=self.ping,
                display_name=self.display_name)
            player_list.players_by_uuid[self.uuid] = player

    class UpdateGameModeAction(Action):
        __slots__ = 'gamemode'

        def _read(self, file_object):
            self.gamemode = VarInt.read(file_object)

        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player:
                player.gamemode = self.gamemode

    class UpdateLatencyAction(Action):
        __slots__ = 'ping'

        def _read(self, file_object):
            self.ping = VarInt.read(file_object)

        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player:
                player.ping = self.ping

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
            if player:
                player.display_name = self.display_name

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
    @staticmethod
    def get_id(context):
        return 0x24 if context.protocol_version >= 334 else \
               0x25 if context.protocol_version >= 318 else \
               0x24 if context.protocol_version >= 107 else \
               0x34

    packet_name = 'map'

    class MapIcon(object):
        __slots__ = 'type', 'direction', 'location'

        def __init__(self, type, direction, location):
            self.type = type
            self.direction = direction
            self.location = location

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
            return ('Map(id=%s, scale=%s, icons=%s, width=%s, height=%s)' % (
                    self.id, self.scale, self.icons, self.width, self.height))

        def __str__(self):
            return self.__repr__()

    class MapSet(object):
        __slots__ = 'maps_by_id'

        def __init__(self):
            self.maps_by_id = dict()

        def __repr__(self):
            maps = [str(map) for map in self.maps_by_id.values()]
            return 'MapSet(%s)' % ', '.join(maps)

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
                z = self.offset[1] + i // self.width
                map.pixels[x + map.width * z] = self.pixels[i]
        map.is_tracking_position = self.is_tracking_position

    def apply_to_map_set(self, map_set):
        map = map_set.maps_by_id.get(self.map_id)
        if map is None:
            map = MapPacket.Map(self.map_id)
            map_set.maps_by_id[self.map_id] = map
        self.apply_to_map(map)

    def write(self, socket, compression_threshold=None):
        packet_buffer = PacketBuffer()
        VarInt.send(self.id, packet_buffer)

        VarInt.send(self.map_id, packet_buffer)
        Byte.send(self.scale, packet_buffer)
        if self.context.protocol_version >= 107:
            Boolean.send(self.is_tracking_position, packet_buffer)

        VarInt.send(len(self.icons), packet_buffer)
        for icon in self.icons:
            type_and_direction = (icon.direction << 4) & 0xF0
            type_and_direction |= (icon.type & 0xF)
            UnsignedByte.send(type_and_direction, packet_buffer)
            Byte.send(icon.location[0], packet_buffer)
            Byte.send(icon.location[1], packet_buffer)

        UnsignedByte.send(self.width, packet_buffer)
        if self.width:
            UnsignedByte.send(self.height, packet_buffer)
            UnsignedByte.send(self.offset[0], packet_buffer)  # x
            UnsignedByte.send(self.offset[1], packet_buffer)  # z
            VarIntPrefixedByteArray.send(self.pixels, packet_buffer)

        self._write_buffer(socket, packet_buffer, compression_threshold)

    def __repr__(self):
        return 'MapPacket(%s)' % ', '.join(
            '%s=%r' % (k, v)
            for (k, v) in self.__dict__.items()
            if k != 'pixels')

    def __str__(self):
        return self.__repr__()

class ClientSpawnPlayer(Packet):
    @staticmethod
    def get_id(context):
        return 0x05 if context.protocol_version >= 67 else \
               0x0C

    packet_name = 'spawn player'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'player_UUID': UUID},
        {'x': Double} if context.protocol_version >= 100 else {'x': Integer},
        {'y': Double} if context.protocol_version >= 100 else {'y': Integer},
        {'z': Double} if context.protocol_version >= 100 else {'z': Integer},
        {'yaw': Float},
        {'pitch': Float},
        {'current_item': Short} if context.protocol_version <= 49 else {}
    ])

class ClientEntityVelocity(Packet):
    @staticmethod
    def get_id(context):
        return 0x3D if context.protocol_version >= 332 else \
               0x3B if context.protocol_version >= 86 else \
               0x3C if context.protocol_version >= 77 else \
               0x3B if context.protocol_version >= 67 else \
               0x12

    packet_name = 'entity velocity'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'velocity_x': Short},
        {'velocity_y': Short},
        {'velocity_z': Short}
    ])

class ClientUpdateHealth(Packet):
    @staticmethod
    def get_id(context):
        return 0x40 if context.protocol_version >= 318 else \
               0x3E if context.protocol_version >= 86 else \
               0x3F if context.protocol_version >= 77 else \
               0x3E if context.protocol_version >= 67 else \
               0x06

    packet_name = 'update health'
    get_definition = staticmethod(lambda context: [
        {'health': Float},
        {'food': VarInt},
        {'food_saturation': Float}
    ])

class ClientCombatEvent(Packet):
    @staticmethod
    def get_id(context):
        return 0x2C if context.protocol_version >= 332 else \
               0x2D if context.protocol_version >= 318 else \
               0x2C if context.protocol_version >= 86 else \
               0x2D if context.protocol_version >= 80 else \
               0x2C if context.protocol_version >= 67 else \
               0x42

    packet_name = 'combat event'

    class EventTypes(object):
        def read(self, file_object):
            self._read(file_object)

        def _read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        @classmethod
        def type_from_id(cls, event_id):
            subcls = {
                0: ClientCombatEvent.EnterCombatEvent,
                1: ClientCombatEvent.EndCombatEvent,
                2: ClientCombatEvent.EntityDeadEvent
            }.get(event_id)
            if subcls is None:
                raise ValueError("Unknown combat event ID: %s."
                                 % event_id)
            return subcls

    class EnterCombatEvent(EventTypes):
        def _read(self, file_object):
            pass

    class EndCombatEvent(EventTypes):
        __slots__ = 'duration', 'entity_id'

        def _read(self, file_object):
            self.duration = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)

    class EntityDeadEvent(EventTypes):
        __slots__ = 'player_id', 'entity_id', 'message'

        def _read(self, file_object):
            self.player_id = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)
            self.message = String.read(file_object)

    def read(self, file_object):
        event_id = VarInt.read(file_object)
        self.event_type = ClientCombatEvent.EventTypes.type_from_id(event_id)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

class ClientExplosion(Packet):
    @staticmethod
    def get_id(context):
        return 0x1C if context.protocol_version >= 332 else \
               0x1D if context.protocol_version >= 318 else \
               0x1C if context.protocol_version >= 80 else \
               0x1B if context.protocol_version >= 67 else \
               0x27

    packet_name = 'explosion'

    class Record(object):
        __slots__ = 'x', 'y', 'z'

        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

        def __repr__(self):
            return ('Record(x=%s, y=%s, z=%s)'
                    % (self.x, self.y, self.z))

        def __str__(self):
            return self.__repr__()


    class Explosion(object):
        __slots__ = ('x', 'y', 'z', 'radius', 'records',
                     'player_motion_x', 'player_motion_y', 'player_motion_z')

        def __repr__(self):
            return ('Explosion(x=%s, y=%s, z=%s, radius=%s, records=%s)' % (
                    self.x, self.y, self.z, self.radius, self.records))

        def __str__(self):
            return self.__repr__()

    def read(self, file_object):
        self.x = Float.read(file_object)
        self.y = Float.read(file_object)
        self.z = Float.read(file_object)
        self.radius = Float.read(file_object)
        records_count = VarInt.read(file_object)
        self.records = []
        for i in range(records_count):
            rec_x = Byte.read(file_object)
            rec_y = Byte.read(file_object)
            rec_z = Byte.read(file_object)
            record = ClientExplosion.Record(rec_x,rec_y,rec_z)
            self.records.append(record)
        self.player_motion_x = Float.read(file_object)
        self.player_motion_y = Float.read(file_object)
        self.player_motion_z = Float.read(file_object)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError


class ClientSpawnObject(Packet):
    @staticmethod
    def get_id(context):
        return 0x00 if context.protocol_version >= 67 else \
               0x0E

    packet_name = 'spawn object'

    class Type(object):
        def read(self, file_object):
            self._read(file_object)

        def _read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        @classmethod
        def type_from_id(cls, type_id):
            subcls = {
                1 : ClientSpawnObject.Type_Boat,
                2 : ClientSpawnObject.Type_Item_Stack,
                3 : ClientSpawnObject.Type_Area_Effect_Cloud,
                10: ClientSpawnObject.Type_Minecart,
                50: ClientSpawnObject.Type_Activated_TNT,
                51: ClientSpawnObject.Type_EnderCrystal,
                60: ClientSpawnObject.Type_Arrow,
                61: ClientSpawnObject.Type_Snowball,
                62: ClientSpawnObject.Type_Egg,
                63: ClientSpawnObject.Type_FireBall,
                64: ClientSpawnObject.Type_FireCharge,
                65: ClientSpawnObject.Type_Enderpearl,
                66: ClientSpawnObject.Type_Wither_Skull,
                67: ClientSpawnObject.Type_Shulker_Bullet,
                68: ClientSpawnObject.Type_Llama_spit,
                70: ClientSpawnObject.Type_Falling_Objects,
                71: ClientSpawnObject.Type_Item_frames,
                72: ClientSpawnObject.Type_Eye_of_Ender,
                73: ClientSpawnObject.Type_Potion,
                75: ClientSpawnObject.Type_Exp_Bottle,
                76: ClientSpawnObject.Type_Firework_Rocket,
                77: ClientSpawnObject.Type_Leash_Knot,
                78: ClientSpawnObject.Type_ArmorStand,
                79: ClientSpawnObject.Type_Evocation_Fangs,
                90: ClientSpawnObject.Type_Fishing_Hook,
                91: ClientSpawnObject.Type_Spectral_Arrow,
                93: ClientSpawnObject.Type_Dragon_Fireball
            }.get(type_id)
            if subcls is None:
                raise ValueError("Unknown type ID: %s."
                                 % type_id)
            return subcls

    class Type_Boat(Type): pass
    class Type_Item_Stack(Type): pass
    class Type_Area_Effect_Cloud(Type): pass
    class Type_Minecart(Type): pass
    class Type_Activated_TNT(Type): pass
    class Type_EnderCrystal(Type): pass
    class Type_Arrow(Type): pass
    class Type_Snowball(Type): pass
    class Type_Egg(Type): pass
    class Type_FireBall(Type): pass
    class Type_FireCharge(Type): pass
    class Type_Enderpearl(Type): pass
    class Type_Wither_Skull(Type): pass
    class Type_Shulker_Bullet(Type): pass
    class Type_Llama_spit(Type): pass
    class Type_Falling_Objects(Type): pass
    class Type_Item_frames(Type): pass
    class Type_Eye_of_Ender(Type): pass
    class Type_Potion(Type): pass
    class Type_Exp_Bottle(Type): pass
    class Type_Firework_Rocket(Type): pass
    class Type_Leash_Knot(Type): pass
    class Type_ArmorStand(Type): pass
    class Type_Evocation_Fangs(Type): pass
    class Type_Fishing_Hook(Type): pass
    class Type_Spectral_Arrow(Type): pass
    class Type_Dragon_Fireball(Type): pass

    def read(self, file_object):
        self.entity_id = VarInt.read(file_object)
        if self._context.protocol_version >= 49:
            self.objectUUID = UUID.read(file_object)
        type_id = Byte.read(file_object)
        self.type = ClientSpawnObject.Type.type_from_id(type_id)

        if self._context.protocol_version >= 100:
            self.x = Double.read(file_object)
            self.y = Double.read(file_object)
            self.z = Double.read(file_object)
        else:
            self.x = Integer.read(file_object)
            self.y = Integer.read(file_object)
            self.z = Integer.read(file_object)

        self.pitch = UnsignedByte.read(file_object)
        self.yaw = UnsignedByte.read(file_object)
        self.data = Integer.read(file_object)

        if self._context.protocol_version < 49:
            if self.data != 0:
                self.velocity_x = Short.read(file_object)
                self.velocity_y = Short.read(file_object)
                self.velocity_z = Short.read(file_object)
        else:
            self.velocity_x = Short.read(file_object)
            self.velocity_y = Short.read(file_object)
            self.velocity_z = Short.read(file_object)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

class ClientBlockChange(Packet):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 332 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 67 else \
               0x24 if context.protocol_version >= 62 else \
               0x23

    packet_name = 'block change'

    def read(self, file_object):
        self.location = Position.read(file_object)
        blockData = VarInt.read(file_object)
        self.blockId = (blockData >> 4)
        self.blockMeta = (blockData & 0xF)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

class ClientMultiBlockChange(Packet):
    @staticmethod
    def get_id(context):
        return 0x10 if context.protocol_version >= 332 else \
               0x11 if context.protocol_version >= 318 else \
               0x10 if context.protocol_version >= 67 else \
               0x22

    packet_name = 'multi block change'

    class Record(object):
        __slots__ = 'x', 'y', 'z', 'blockId', 'blockMeta'

        def __init__(self, horizontal_position, y_coordinate, blockData):
            self.x = (horizontal_position & 0xF0)
            self.y = y_coordinate
            self.z = (horizontal_position & 0x0F)
            self.blockId = (blockData >> 4)
            self.blockMeta = (blockData & 0xF)

        def __repr__(self):
            return ('Record(x=%s, y=%s, z=%s, blockId=%s)'
                    % (self.x, self.y, self.z, self.blockId))

        def __str__(self):
            return self.__repr__()

    def read(self, file_object):
        self.chunk_x = Integer.read(file_object)
        self.chunk_z = Integer.read(file_object)
        records_count = VarInt.read(file_object)
        self.records = []
        for i in range(records_count):
            rec_horizontal_position = UnsignedByte.read(file_object)
            rec_y_coordinate = UnsignedByte.read(file_object)
            rec_blockData = VarInt.read(file_object)
            record = ClientMultiBlockChange.Record(rec_horizontal_position,rec_y_coordinate,rec_blockData)
            self.records.append(record)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

def state_playing_clientbound(context):
    packets = {
        KeepAlivePacketClientbound,
        JoinGamePacket,
        ChatMessagePacket,
        PlayerPositionAndLookPacket,
        MapPacket,
        PlayerListItemPacket,
        DisconnectPacketPlayState,
        ClientSpawnPlayer,
        ClientEntityVelocity,
        ClientUpdateHealth,
        ClientCombatEvent,
        ClientExplosion,
        ClientSpawnObject,
        ClientBlockChange,
        ClientMultiBlockChange,
    }
    if context.protocol_version <= 47:
        packets |= {
            SetCompressionPacketPlayState,
        }
    return packets

class ChatPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x02 if context.protocol_version >= 336 else \
               0x03 if context.protocol_version >= 318 else \
               0x02 if context.protocol_version >= 107 else \
               0x01

    @staticmethod
    def get_max_length(context):
        return 256 if context.protocol_version >= 306 else \
               100

    @property
    def max_length(self):
        if self.context is not None:
            return self.get_max_length(self.context)

    packet_name = "chat"
    definition = [
        {'message': String}]


class PositionAndLookPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0E if context.protocol_version >= 336 else \
               0x0F if context.protocol_version >= 332 else \
               0x0E if context.protocol_version >= 318 else \
               0x0D if context.protocol_version >= 107 else \
               0x06

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
    @staticmethod
    def get_id(context):
        return 0x1D if context.protocol_version >= 332 else \
               0x1C if context.protocol_version >= 318 else \
               0x1A if context.protocol_version >= 107 else \
               0x0A

    packet_name = "animation"
    get_definition = staticmethod(lambda context: [
        {'hand': VarInt} if context.protocol_version >= 107 else {}])
    HAND_MAIN = 0
    HAND_OFF = 1

class ServerClientStatus(Packet):
    @staticmethod
    def get_id(context):
        return 0x04 if context.protocol_version >= 318 else \
               0x03 if context.protocol_version >= 80 else \
               0x02 if context.protocol_version >= 67 else \
               0x17 if context.protocol_version >= 49 else \
               0x16

    packet_name = "client status"
    get_definition = staticmethod(lambda context: [
        {'action_id': VarInt}])

    RESPAWN = 0
    REQUEST_STATS = 1

def state_playing_serverbound(context):
    packets = {
        KeepAlivePacketServerbound,
        ChatPacket,
        PositionAndLookPacket,
        AnimationPacketServerbound,
        ServerClientStatus,
    }
    if context.protocol_version >= 107:
        packets |= {
            TeleportConfirmPacket,
        }
    return packets
