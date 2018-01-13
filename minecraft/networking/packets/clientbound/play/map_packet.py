from minecraft.networking.packets import (
    Packet, PacketBuffer
)

from minecraft.networking.types import (
    VarInt, Byte, Boolean, UnsignedByte, VarIntPrefixedByteArray
)


class MapPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x25 if context.protocol_version >= 345 else \
               0x24 if context.protocol_version >= 334 else \
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
