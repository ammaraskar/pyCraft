from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    VarInt, Byte, Boolean, UnsignedByte, VarIntPrefixedByteArray, String,
    MutableRecord
)


class MapPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x27 if context.protocol_version >= 550 else \
               0x26 if context.protocol_version >= 389 else \
               0x25 if context.protocol_version >= 345 else \
               0x24 if context.protocol_version >= 334 else \
               0x25 if context.protocol_version >= 318 else \
               0x24 if context.protocol_version >= 107 else \
               0x34

    packet_name = 'map'

    @property
    def fields(self):
        fields = 'id', 'scale', 'icons', 'width', 'height', 'pixels'
        if self.context.protocol_version >= 107:
            fields += 'is_tracking_position',
        if self.context.protocol_version >= 452:
            fields += 'is_locked',
        return fields

    def field_string(self, field):
        if field == 'pixels' and isinstance(self.pixels, bytearray):
            return 'bytearray(...)'
        return super(MapPacket, self).field_string(field)

    class MapIcon(MutableRecord):
        __slots__ = 'type', 'direction', 'location', 'display_name'

        def __init__(self, type, direction, location, display_name=None):
            self.type = type
            self.direction = direction
            self.location = location
            self.display_name = display_name

    class Map(MutableRecord):
        __slots__ = ('id', 'scale', 'icons', 'pixels', 'width', 'height',
                     'is_tracking_position', 'is_locked')

        def __init__(self, id=None, scale=None, width=128, height=128):
            self.id = id
            self.scale = scale
            self.icons = []
            self.width = width
            self.height = height
            self.pixels = bytearray(0 for i in range(width*height))
            self.is_tracking_position = True
            self.is_locked = False

    class MapSet(object):
        __slots__ = 'maps_by_id'

        def __init__(self, *maps):
            self.maps_by_id = {map.id: map for map in maps}

        def __repr__(self):
            maps = (repr(map) for map in self.maps_by_id.values())
            return 'MapSet(%s)' % ', '.join(maps)

    def read(self, file_object):
        self.map_id = VarInt.read(file_object)
        self.scale = Byte.read(file_object)

        if self.context.protocol_version >= 107:
            self.is_tracking_position = Boolean.read(file_object)
        else:
            self.is_tracking_position = True

        if self.context.protocol_version >= 452:
            self.is_locked = Boolean.read(file_object)
        else:
            self.is_locked = False

        icon_count = VarInt.read(file_object)
        self.icons = []
        for i in range(icon_count):
            if self.context.protocol_version >= 373:
                type = VarInt.read(file_object)
            else:
                type, direction = divmod(UnsignedByte.read(file_object), 16)
            x = Byte.read(file_object)
            z = Byte.read(file_object)
            if self.context.protocol_version >= 373:
                direction = UnsignedByte.read(file_object)
            if self.context.protocol_version >= 364:
                has_name = Boolean.read(file_object)
                display_name = String.read(file_object) if has_name else None
            else:
                display_name = None
            icon = MapPacket.MapIcon(type, direction, (x, z), display_name)
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
        map.is_locked = self.is_locked

    def apply_to_map_set(self, map_set):
        map = map_set.maps_by_id.get(self.map_id)
        if map is None:
            map = MapPacket.Map(self.map_id)
            map_set.maps_by_id[self.map_id] = map
        self.apply_to_map(map)

    def write_fields(self, packet_buffer):
        VarInt.send(self.map_id, packet_buffer)
        Byte.send(self.scale, packet_buffer)
        if self.context.protocol_version >= 107:
            Boolean.send(self.is_tracking_position, packet_buffer)

        VarInt.send(len(self.icons), packet_buffer)
        for icon in self.icons:
            if self.context.protocol_version >= 373:
                VarInt.send(icon.type, packet_buffer)
            else:
                type_and_direction = (icon.type << 4) & 0xF0
                type_and_direction |= (icon.direction & 0xF)
                UnsignedByte.send(type_and_direction, packet_buffer)
            Byte.send(icon.location[0], packet_buffer)
            Byte.send(icon.location[1], packet_buffer)
            if self.context.protocol_version >= 373:
                UnsignedByte.send(icon.direction, packet_buffer)
            if self.context.protocol_version >= 364:
                Boolean.send(icon.display_name is not None, packet_buffer)
                if icon.display_name is not None:
                    String.send(icon.display_name, packet_buffer)

        UnsignedByte.send(self.width, packet_buffer)
        if self.width:
            UnsignedByte.send(self.height, packet_buffer)
            UnsignedByte.send(self.offset[0], packet_buffer)  # x
            UnsignedByte.send(self.offset[1], packet_buffer)  # z
            VarIntPrefixedByteArray.send(self.pixels, packet_buffer)
