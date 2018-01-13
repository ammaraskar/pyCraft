from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, Integer, String
)


class CombatEventPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x2E if context.protocol_version >= 345 else \
               0x2D if context.protocol_version >= 336 else \
               0x2C if context.protocol_version >= 332 else \
               0x2D if context.protocol_version >= 318 else \
               0x2C if context.protocol_version >= 86 else \
               0x2D if context.protocol_version >= 80 else \
               0x2C if context.protocol_version >= 67 else \
               0x42

    packet_name = 'combat event'

    class EventType(object):
        def read(self, file_object):
            self._read(file_object)

        def _read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        @classmethod
        def type_from_id(cls, event_id):
            subcls = {
                0: CombatEventPacket.EnterCombatEvent,
                1: CombatEventPacket.EndCombatEvent,
                2: CombatEventPacket.EntityDeadEvent
            }.get(event_id)
            if subcls is None:
                raise ValueError("Unknown combat event ID: %s."
                                 % event_id)
            return subcls

    class EnterCombatEvent(EventType):
        def _read(self, file_object):
            pass

    class EndCombatEvent(EventType):
        __slots__ = 'duration', 'entity_id'

        def _read(self, file_object):
            self.duration = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)

    class EntityDeadEvent(EventType):
        __slots__ = 'player_id', 'entity_id', 'message'

        def _read(self, file_object):
            self.player_id = VarInt.read(file_object)
            self.entity_id = Integer.read(file_object)
            self.message = String.read(file_object)

    def read(self, file_object):
        event_id = VarInt.read(file_object)
        self.event_type = CombatEventPacket.EventType.type_from_id(event_id)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError
