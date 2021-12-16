from abc import ABCMeta, abstractmethod

from minecraft import PRE
from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, Integer, String, MutableRecord
)


# Note: this packet was removed in Minecraft 21w07a (protocol PRE|15)
# and replaced with the separate EnterCombatEvent, EndCombatEvent, and
# DeathCombatEvent packets. These are subclasses of CombatEventPacket, so
# that code written to listen for CombatEventPacket instances should in most
# cases continue to work without modification.
class CombatEventPacket(Packet):
    @classmethod
    def get_id(cls, context):
        return cls.deprecated() if context.protocol_later_eq(PRE | 15) else \
               0x31 if context.protocol_later_eq(741) else \
               0x32 if context.protocol_later_eq(721) else \
               0x33 if context.protocol_later_eq(550) else \
               0x32 if context.protocol_later_eq(471) else \
               0x30 if context.protocol_later_eq(451) else \
               0x2F if context.protocol_later_eq(389) else \
               0x2E if context.protocol_later_eq(345) else \
               0x2D if context.protocol_later_eq(336) else \
               0x2C if context.protocol_later_eq(332) else \
               0x2D if context.protocol_later_eq(318) else \
               0x2C if context.protocol_later_eq(86) else \
               0x2D if context.protocol_later_eq(80) else \
               0x2C if context.protocol_later_eq(67) else \
               0x42

    packet_name = 'combat event'

    fields = 'event',

    # The abstract type of the 'event' field of this packet.
    class EventType(MutableRecord, metaclass=ABCMeta):
        __slots__ = ()
        type_from_id_dict = {}

        # Read the fields of the event (not including the ID) from the file.
        @abstractmethod
        def read(self, file_object):
            pass

        # Write the fields of the event (not including the ID) to the buffer.
        @abstractmethod
        def write(self, packet_buffer):
            pass

        @classmethod
        def type_from_id(cls, event_id):
            subcls = cls.type_from_id_dict.get(event_id)
            if subcls is None:
                raise ValueError('Unknown combat event ID: %s.' % event_id)
            return subcls

    class EnterCombatEvent(EventType):
        __slots__ = ()
        id = 0

        def read(self, file_object):
            pass

        def write(self, packet_buffer):
            pass
    EventType.type_from_id_dict[EnterCombatEvent.id] = EnterCombatEvent

    class EndCombatEvent(EventType):
        __slots__ = 'duration', 'entity_id'
        id = 1

        def read(self, file_object):
            self.duration = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)

        def write(self, packet_buffer):
            VarInt.send(self.duration, packet_buffer)
            Integer.send(self.entity_id, packet_buffer)
    EventType.type_from_id_dict[EndCombatEvent.id] = EndCombatEvent

    class EntityDeadEvent(EventType):
        __slots__ = 'player_id', 'entity_id', 'message'
        id = 2

        def read(self, file_object):
            self.player_id = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)
            self.message = String.read(file_object)

        def write(self, packet_buffer):
            VarInt.send(self.player_id, packet_buffer)
            Integer.send(self.entity_id, packet_buffer)
            String.send(self.message, packet_buffer)
    EventType.type_from_id_dict[EntityDeadEvent.id] = EntityDeadEvent

    def read(self, file_object):
        if self.context and self.context.protocol_later_eq(PRE | 15):
            self.deprecated()
        event_id = VarInt.read(file_object)
        self.event = CombatEventPacket.EventType.type_from_id(event_id)()
        self.event.read(file_object)

    def write_fields(self, packet_buffer):
        if self.context and self.context.protocol_later_eq(PRE | 15):
            self.deprecated()
        VarInt.send(self.event.id, packet_buffer)
        self.event.write(packet_buffer)

    @staticmethod
    def deprecated():
        raise NotImplementedError(
            '`CombatEventPacket` was removed in Minecraft snapshot 21w07a '
            '(protocol version 2**30 + 15). In this and later versions, one '
            'of the subclasses '
            + repr(SpecialisedCombatEventPacket.__subclasses__()) + ' must be '
            'used directly for usage like that which generates this message.')


# Contains the behaviour common to all concrete CombatEventPacket subclasses
class SpecialisedCombatEventPacket(CombatEventPacket):
    def __init__(self, *args, **kwds):
        super(SpecialisedCombatEventPacket, self).__init__(*args, **kwds)

        # Prior to Minecraft 21w07a, instances of CombatEventPacket had a
        # single 'event' field giving a 'MutableRecord' of one of three types
        # corresponding to the type of combat event represented. For backward
        # compatibility, we here present a similar interface, giving the packet
        # object itself as the 'event', which should work identically in most
        # use cases, since it is a virtual subclass of, and has attributes of
        # the same names and contents as those of, the previous event records.
        self.event = self

    # The 'get_id', 'fields', 'read', and 'write_fields' attributes of the
    # 'Packet' base class are all overridden in 'CombatEventPacket'. We desire
    # the default behaviour of these attributes, so we restore them here:
    get_id = Packet.__dict__['get_id']
    fields = Packet.__dict__['fields']
    read = Packet.__dict__['read']
    write_fields = Packet.__dict__['write_fields']


@CombatEventPacket.EnterCombatEvent.register  # virtual subclass
class EnterCombatEventPacket(SpecialisedCombatEventPacket):
    packet_name = 'enter combat event'
    id = 0x34
    definition = []


@CombatEventPacket.EndCombatEvent.register  # virtual subclass
class EndCombatEventPacket(SpecialisedCombatEventPacket):
    packet_name = 'end combat event'
    id = 0x33
    definition = [
        {'duration': VarInt},
        {'entity_id': Integer}]


@CombatEventPacket.EntityDeadEvent.register  # virtual subclass
class DeathCombatEventPacket(SpecialisedCombatEventPacket):
    packet_name = 'death combat event'
    id = 0x35
    definition = [
        {'player_id': VarInt},
        {'entity_id': Integer},
        {'message': String}]
