from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    String, Boolean, UUID, VarInt, MutableRecord,
)


# Player Info
class PlayerListItemPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x34 if context.protocol_version >= 550 else \
               0x33 if context.protocol_version >= 471 else \
               0x31 if context.protocol_version >= 451 else \
               0x30 if context.protocol_version >= 389 else \
               0x2F if context.protocol_version >= 345 else \
               0x2E if context.protocol_version >= 336 else \
               0x2D if context.protocol_version >= 332 else \
               0x2E if context.protocol_version >= 318 else \
               0x2D if context.protocol_version >= 107 else \
               0x38

    packet_name = "player list item"

    fields = 'action_type', 'actions'

    def field_string(self, field):
        if field == 'action_type':
            return self.action_type.__name__
        return super(PlayerListItemPacket, self).field_string(field)

    class PlayerList(object):
        __slots__ = 'players_by_uuid'

        def __init__(self, *items):
            self.players_by_uuid = {item.uuid: item for item in items}

    class PlayerListItem(MutableRecord):
        __slots__ = (
            'uuid', 'name', 'properties', 'gamemode', 'ping', 'display_name')

    class PlayerProperty(MutableRecord):
        __slots__ = 'name', 'value', 'signature'

        def read(self, file_object):
            self.name = String.read(file_object)
            self.value = String.read(file_object)
            is_signed = Boolean.read(file_object)
            if is_signed:
                self.signature = String.read(file_object)
            else:
                self.signature = None

        def send(self, packet_buffer):
            String.send(self.name, packet_buffer)
            String.send(self.value, packet_buffer)
            if self.signature is not None:
                Boolean.send(True, packet_buffer)
                String.send(self.signature, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)

    class Action(MutableRecord):
        __slots__ = 'uuid',

        def read(self, file_object):
            self.uuid = UUID.read(file_object)
            self._read(file_object)

        def send(self, packet_buffer):
            UUID.send(self.uuid, packet_buffer)
            self._send(packet_buffer)

        def _read(self, file_object):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        def _send(self, packet_buffer):
            raise NotImplementedError(
                'This abstract method must be overridden in a subclass.')

        @classmethod
        def type_from_id(cls, action_id):
            for subcls in cls.__subclasses__():
                if subcls.action_id == action_id:
                    return subcls
            raise ValueError("Unknown player list action ID: %s." % action_id)

    class AddPlayerAction(Action):
        __slots__ = 'name', 'properties', 'gamemode', 'ping', 'display_name'
        action_id = 0

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

        def _send(self, packet_buffer):
            String.send(self.name, packet_buffer)
            VarInt.send(len(self.properties), packet_buffer)
            for property in self.properties:
                property.send(packet_buffer)
            VarInt.send(self.gamemode, packet_buffer)
            VarInt.send(self.ping, packet_buffer)
            if self.display_name is not None:
                Boolean.send(True, packet_buffer)
                String.send(self.display_name, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)

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
        action_id = 1

        def _read(self, file_object):
            self.gamemode = VarInt.read(file_object)

        def _send(self, packet_buffer):
            VarInt.send(self.gamemode, packet_buffer)

        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player:
                player.gamemode = self.gamemode

    class UpdateLatencyAction(Action):
        __slots__ = 'ping'
        action_id = 2

        def _read(self, file_object):
            self.ping = VarInt.read(file_object)

        def _send(self, packet_buffer):
            VarInt.send(self.ping, packet_buffer)

        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player:
                player.ping = self.ping

    class UpdateDisplayNameAction(Action):
        __slots__ = 'display_name'
        action_id = 3

        def _read(self, file_object):
            has_display_name = Boolean.read(file_object)
            if has_display_name:
                self.display_name = String.read(file_object)
            else:
                self.display_name = None

        def _send(self, packet_buffer):
            if self.display_name is not None:
                Boolean.send(True, packet_buffer)
                String.send(self.display_name, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)

        def apply(self, player_list):
            player = player_list.players_by_uuid.get(self.uuid)
            if player:
                player.display_name = self.display_name

    class RemovePlayerAction(Action):
        action_id = 4

        def _read(self, file_object):
            pass

        def _send(self, packet_buffer):
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

    def write_fields(self, packet_buffer):
        VarInt.send(self.action_type.action_id, packet_buffer)
        VarInt.send(len(self.actions), packet_buffer)
        for action in self.actions:
            action.send(packet_buffer)

    def apply(self, player_list):
        for action in self.actions:
            action.apply(player_list)
