import pynbt

from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    NBT, Integer, Boolean, UnsignedByte, String, Byte, Long, VarInt,
    PrefixedArray, Difficulty, GameMode, Dimension,
)


def nbt_to_snbt(tag):
    '''Convert a pyNBT tag to SNBT ("stringified NBT") format.'''
    scalars = {
        pynbt.TAG_Byte: 'b',
        pynbt.TAG_Short: 's',
        pynbt.TAG_Int: '',
        pynbt.TAG_Long: 'l',
        pynbt.TAG_Float: 'f',
        pynbt.TAG_Double: 'd',
    }
    if type(tag) in scalars:
        return repr(tag.value) + scalars[type(tag)]

    arrays = {
        pynbt.TAG_Byte_Array: 'B',
        pynbt.TAG_Int_Array: 'I',
        pynbt.TAG_Long_Array: 'L',
    }
    if type(tag) in arrays:
        return '[' + arrays[type(tag)] + ';' + \
               ','.join(map(repr, tag.value)) + ']'

    if isinstance(tag, pynbt.TAG_String):
        return repr(tag.value)

    if isinstance(tag, pynbt.TAG_List):
        return '[' + ','.join(map(nbt_to_snbt, tag.value)) + ']'

    if isinstance(tag, pynbt.TAG_Compound):
        return '{' + ','.join(n + ':' + nbt_to_snbt(v)
                              for (n, v) in tag.items()) + '}'

    raise TypeError('Unknown NBT tag type: %r' % type(tag))


class AbstractDimensionPacket(Packet):
    ''' The abstract superclass of JoinGamePacket and RespawnPacket, containing
        common definitions relating to their 'dimension' field.
    '''
    def field_string(self, field):
        # pylint: disable=no-member
        if self.context.protocol_later_eq(748) and field == 'dimension':
            return nbt_to_snbt(self.dimension)
        elif self.context.protocol_earlier(718) and field == 'dimension':
            return Dimension.name_from_value(self.dimension)
        return super(AbstractDimensionPacket, self).field_string(field)


class JoinGamePacket(AbstractDimensionPacket):
    @staticmethod
    def get_id(context):
        return 0x24 if context.protocol_later_eq(741) else \
               0x25 if context.protocol_later_eq(721) else \
               0x26 if context.protocol_later_eq(550) else \
               0x25 if context.protocol_later_eq(389) else \
               0x24 if context.protocol_later_eq(345) else \
               0x23 if context.protocol_later_eq(332) else \
               0x24 if context.protocol_later_eq(318) else \
               0x23 if context.protocol_later_eq(107) else \
               0x01

    packet_name = "join game"
    get_definition = staticmethod(lambda context: [
        {'entity_id': Integer},
        {'is_hardcore': Boolean} if context.protocol_later_eq(738) else {},
        {'game_mode': UnsignedByte},
        {'previous_game_mode': UnsignedByte}
        if context.protocol_later_eq(730) else {},
        {'world_names': PrefixedArray(VarInt, String)}
        if context.protocol_later_eq(722) else {},
        {'dimension_codec': NBT}
        if context.protocol_later_eq(718) else {},
        {'dimension':
         NBT if context.protocol_later_eq(748) else
         String if context.protocol_later_eq(718) else
         Integer if context.protocol_later_eq(108) else
         Byte},
        {'world_name': String} if context.protocol_later_eq(722) else {},
        {'hashed_seed': Long} if context.protocol_later_eq(552) else {},
        {'difficulty': UnsignedByte} if context.protocol_earlier(464) else {},
        {'max_players':
            VarInt if context.protocol_later_eq(749) else UnsignedByte},
        {'level_type': String} if context.protocol_earlier(716) else {},
        {'render_distance': VarInt} if context.protocol_later_eq(468) else {},
        {'reduced_debug_info': Boolean},
        {'respawn_screen': Boolean} if context.protocol_later_eq(571) else {},
        {'is_debug': Boolean} if context.protocol_later_eq(716) else {},
        {'is_flat': Boolean} if context.protocol_later_eq(716) else {},
    ])

    # These aliases declare the Enum type corresponding to each field:
    Difficulty = Difficulty
    GameMode = GameMode

    # Accesses the 'game_mode' field appropriately depending on the protocol.
    # Can be set or deleted when 'context' is undefined.
    @property
    def game_mode(self):
        if self.context.protocol_later_eq(738):
            return self._game_mode_738
        else:
            return self._game_mode_0

    @game_mode.setter
    def game_mode(self, value):
        self._game_mode_738 = value
        self._game_mode_0 = value

    @game_mode.deleter
    def game_mode(self):
        del self._game_mode_738
        del self._game_mode_0

    # Accesses the 'is_hardcore' field, or its equivalent in older protocols.
    # Can be set or deleted when 'context' is undefined.
    @property
    def is_hardcore(self):
        if self.context.protocol_later_eq(738):
            return self._is_hardcore
        else:
            return bool(self._game_mode_0 & GameMode.HARDCORE)

    @is_hardcore.setter
    def is_hardcore(self, value):
        self._is_hardcore = value
        self._game_mode_0 = \
            getattr(self, '_game_mode_0', 0) | GameMode.HARDCORE \
            if value else \
            getattr(self, '_game_mode_0', 0) & ~GameMode.HARDCORE

    @is_hardcore.deleter
    def is_hardcore(self):
        if hasattr(self, '_is_hardcore'):
            del self._is_hardcore
        if hasattr(self, '_game_mode_0'):
            self._game_mode_0 &= ~GameMode.HARDCORE

    # Accesses the component of the 'game_mode' field without any hardcore bit,
    # version-independently. Can be set or deleted when 'context' is undefined.
    @property
    def pure_game_mode(self):
        if self.context.protocol_later_eq(738):
            return self._game_mode_738
        else:
            return self._game_mode_0 & ~GameMode.HARDCORE

    @pure_game_mode.setter
    def pure_game_mode(self, value):
        self._game_mode_738 = value
        self._game_mode_0 = \
            value & ~GameMode.HARDCORE | \
            getattr(self, '_game_mode_0', 0) & GameMode.HARDCORE

    def field_string(self, field):
        if field == 'dimension_codec':
            # pylint: disable=no-member
            return nbt_to_snbt(self.dimension_codec)
        return super(JoinGamePacket, self).field_string(field)


class RespawnPacket(AbstractDimensionPacket):
    @staticmethod
    def get_id(context):
        return 0x39 if context.protocol_later_eq(741) else \
               0x3A if context.protocol_later_eq(721) else \
               0x3B if context.protocol_later_eq(550) else \
               0x3A if context.protocol_later_eq(471) else \
               0x38 if context.protocol_later_eq(461) else \
               0x39 if context.protocol_later_eq(451) else \
               0x38 if context.protocol_later_eq(389) else \
               0x37 if context.protocol_later_eq(352) else \
               0x36 if context.protocol_later_eq(345) else \
               0x35 if context.protocol_later_eq(336) else \
               0x34 if context.protocol_later_eq(332) else \
               0x35 if context.protocol_later_eq(318) else \
               0x33 if context.protocol_later_eq(70) else \
               0x07

    packet_name = 'respawn'
    get_definition = staticmethod(lambda context: [
        {'dimension':
         NBT if context.protocol_later_eq(748) else
         String if context.protocol_later_eq(718) else
         Integer},
        {'world_name': String} if context.protocol_later_eq(719) else {},
        {'difficulty': UnsignedByte} if context.protocol_earlier(464) else {},
        {'hashed_seed': Long} if context.protocol_later_eq(552) else {},
        {'game_mode': UnsignedByte},
        {'previous_game_mode': UnsignedByte}
        if context.protocol_later_eq(730) else {},
        {'level_type': String} if context.protocol_earlier(716) else {},
        {'is_debug': Boolean} if context.protocol_later_eq(716) else {},
        {'is_flat': Boolean} if context.protocol_later_eq(716) else {},
        {'copy_metadata': Boolean} if context.protocol_later_eq(714) else {},
    ])

    # These aliases declare the Enum type corresponding to each field:
    Difficulty = Difficulty
    GameMode = GameMode
