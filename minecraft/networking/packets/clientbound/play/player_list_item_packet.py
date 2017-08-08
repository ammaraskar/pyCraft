from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    String, Boolean, UUID, VarInt
)


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
