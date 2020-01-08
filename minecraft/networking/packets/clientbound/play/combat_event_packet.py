from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, Integer, String, MutableRecord
)


class CombatEventPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x33 if context.protocol_version >= 550 else \
               0x32 if context.protocol_version >= 471 else \
               0x30 if context.protocol_version >= 451 else \
               0x2F if context.protocol_version >= 389 else \
               0x2E if context.protocol_version >= 345 else \
               0x2D if context.protocol_version >= 336 else \
               0x2C if context.protocol_version >= 332 else \
               0x2D if context.protocol_version >= 318 else \
               0x2C if context.protocol_version >= 86 else \
               0x2D if context.protocol_version >= 80 else \
               0x2C if context.protocol_version >= 67 else \
               0x42

    packet_name = 'combat event'

    fields = 'event',

    # The abstract type of the 'event' field of this packet.
    class EventType(MutableRecord):
        __slots__ = ()
        type_from_id_dict = {}

        # Read the fields of the event (not including the ID) from the file.
        def read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        # Write the fields of the event (not including the ID) to the buffer.
        def write(self, packet_buffer):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

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
        event_id = VarInt.read(file_object)
        self.event = CombatEventPacket.EventType.type_from_id(event_id)()
        self.event.read(file_object)

    def write_fields(self, packet_buffer):
        VarInt.send(self.event.id, packet_buffer)
        self.event.write(packet_buffer)
