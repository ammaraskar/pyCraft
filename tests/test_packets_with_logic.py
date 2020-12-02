import unittest
from minecraft.networking.types import (UUID, VarInt)
from minecraft.networking.packets import PacketBuffer
from minecraft.networking.packets.clientbound.play import (
    PlayerPositionAndLookPacket, PlayerListItemPacket, MapPacket
)
from minecraft.networking.connection import ConnectionContext

from tests.test_packets import TEST_VERSIONS


class PlayerPositionAndLookTest(unittest.TestCase):

    def test_position_and_look(self):
        current_position = PlayerPositionAndLookPacket.PositionAndLook(
            x=999, y=999, z=999, yaw=999, pitch=999)

        packet = PlayerPositionAndLookPacket()
        packet.x = 1.0
        packet.y = 2.0
        packet.z = 3.0
        packet.yaw = 4.0
        packet.pitch = 5.0
        # First do an absolute move to these cordinates
        packet.flags = 0

        packet.apply(current_position)
        self.assertEqual(current_position.x, 1.0)
        self.assertEqual(current_position.y, 2.0)
        self.assertEqual(current_position.z, 3.0)
        self.assertEqual(current_position.yaw, 4.0)
        self.assertEqual(current_position.pitch, 5.0)

        # Now a relative move
        packet.flags = 0b11111

        packet.apply(current_position)
        self.assertEqual(current_position.x, 2.0)
        self.assertEqual(current_position.y, 4.0)
        self.assertEqual(current_position.z, 6.0)
        self.assertEqual(current_position.yaw, 8.0)
        self.assertEqual(current_position.pitch, 10.0)


class MapPacketTest(unittest.TestCase):

    @staticmethod
    def make_map_packet(
            context, width=2, height=2, offset=(2, 2), pixels=b"this"):

        packet = MapPacket(context)

        packet.map_id = 1
        packet.scale = 42
        packet.is_tracking_position = True
        packet.is_locked = False
        packet.icons = []
        d_name = u'Marshmallow' if context.protocol_later_eq(364) else None
        packet.icons.append(MapPacket.MapIcon(
            type=2, direction=2, location=(1, 1), display_name=d_name
        ))
        packet.icons.append(MapPacket.MapIcon(
            type=3, direction=3, location=(3, 3)
        ))
        packet.width = width
        packet.height = height if width else 0
        packet.offset = offset if width else None
        packet.pixels = pixels if width else None
        return packet

    def packet_roundtrip(self, context, **kwds):
        packet = self.make_map_packet(context, **kwds)

        packet_buffer = PacketBuffer()
        packet.write(packet_buffer)

        packet_buffer.reset_cursor()

        # Read the length and packet id
        VarInt.read(packet_buffer)
        packet_id = VarInt.read(packet_buffer)
        self.assertEqual(packet_id, packet.id)

        p = MapPacket(context)
        p.read(packet_buffer)

        self.assertEqual(p.map_id, packet.map_id)
        self.assertEqual(p.scale, packet.scale)
        self.assertEqual(p.is_tracking_position, packet.is_tracking_position)
        self.assertEqual(p.width, packet.width)
        self.assertEqual(p.height, packet.height)
        self.assertEqual(p.offset, packet.offset)
        self.assertEqual(p.pixels, packet.pixels)
        self.assertEqual(str(p.icons[0]), str(packet.icons[0]))
        self.assertEqual(str(p.icons[1]), str(packet.icons[1]))
        self.assertEqual(str(p), str(packet))

    def test_packet_roundtrip(self):
        self.packet_roundtrip(ConnectionContext(protocol_version=106))
        self.packet_roundtrip(ConnectionContext(protocol_version=107))
        self.packet_roundtrip(ConnectionContext(protocol_version=379))
        self.packet_roundtrip(ConnectionContext(protocol_version=379),
                              width=0)

    def test_map_set(self):
        map_set = MapPacket.MapSet()

        context = ConnectionContext(protocol_version=107)
        packet = self.make_map_packet(context)

        packet.apply_to_map_set(map_set)
        self.assertEqual(len(map_set.maps_by_id), 1)

        packet = self.make_map_packet(
            context, width=1, height=0, offset=(2, 2), pixels=b"x"
        )
        packet.apply_to_map_set(map_set)
        map = map_set.maps_by_id[1]
        self.assertIn(b"xh", map.pixels)
        self.assertIn(b"is", map.pixels)
        self.assertIsNotNone(str(map_set))


fake_uuid = "12345678-1234-5678-1234-567812345678"


class PlayerListItemTest(unittest.TestCase):
    maxDiff = None

    def test_base_action(self):
        packet_buffer = PacketBuffer()
        UUID.send(fake_uuid, packet_buffer)
        packet_buffer.reset_cursor()

        with self.assertRaises(NotImplementedError):
            action = PlayerListItemPacket.Action()
            action.read(packet_buffer)

    def test_invalid_action(self):
        packet_buffer = PacketBuffer()
        VarInt.send(200, packet_buffer)  # action_id
        packet_buffer.reset_cursor()

        with self.assertRaises(ValueError):
            PlayerListItemPacket().read(packet_buffer)

    def make_add_player_packet(self, context, display_name=True):
        packet_buffer = PacketBuffer()
        packet = PlayerListItemPacket(
            context=context,
            action_type=PlayerListItemPacket.AddPlayerAction,
            actions=[
                PlayerListItemPacket.AddPlayerAction(
                    uuid=fake_uuid,
                    name='goodmonson',
                    properties=[
                        PlayerListItemPacket.PlayerProperty(
                            name='property1', value='value1', signature=None),
                        PlayerListItemPacket.PlayerProperty(
                            name='property2', value='value2', signature='gm')
                    ],
                    gamemode=42,
                    ping=69,
                    display_name='Goodmonson' if display_name else None
                ),
            ],
        )
        if display_name:
            self.assertEqual(
                str(packet), "0x%02X PlayerListItemPacket("
                "action_type=AddPlayerAction, actions=[AddPlayerAction("
                "uuid=%r, name='goodmonson', properties=[PlayerProperty("
                "name='property1', value='value1', signature=None), "
                "PlayerProperty(name='property2', value='value2', "
                "signature='gm')], gamemode=42, ping=69, "
                "display_name='Goodmonson')])" % (packet.id, fake_uuid))
        packet.write_fields(packet_buffer)
        packet_buffer.reset_cursor()
        return packet_buffer

    def test_add_player_action(self):
        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)
            player_list = PlayerListItemPacket.PlayerList()
            packet_buffer = self.make_add_player_packet(context)

            packet = PlayerListItemPacket(context)
            packet.read(packet_buffer)
            packet.apply(player_list)

            self.assertIn(fake_uuid, player_list.players_by_uuid)
            player = player_list.players_by_uuid[fake_uuid]

            self.assertEqual(player.name, 'goodmonson')
            self.assertEqual(player.properties[0].name, 'property1')
            self.assertIsNone(player.properties[0].signature)
            self.assertEqual(player.properties[1].value, 'value2')
            self.assertEqual(player.properties[1].signature, 'gm')
            self.assertEqual(player.gamemode, 42)
            self.assertEqual(player.ping, 69)
            self.assertEqual(player.display_name, 'Goodmonson')

    def read_and_apply(self, context, packet_buffer, player_list):
        packet_buffer.reset_cursor()
        packet = PlayerListItemPacket(context)
        packet.read(packet_buffer)
        packet.apply(player_list)

    def test_add_and_others(self):
        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            player_list = PlayerListItemPacket.PlayerList()
            by_uuid = player_list.players_by_uuid

            packet_buffer = self.make_add_player_packet(
                context, display_name=False)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertEqual(by_uuid[fake_uuid].gamemode, 42)
            self.assertEqual(by_uuid[fake_uuid].ping, 69)
            self.assertIsNone(by_uuid[fake_uuid].display_name)

            # Change the game mode
            packet_buffer = PacketBuffer()
            packet = PlayerListItemPacket(
                context=context,
                action_type=PlayerListItemPacket.UpdateGameModeAction,
                actions=[
                    PlayerListItemPacket.UpdateGameModeAction(
                        uuid=fake_uuid, gamemode=43),
                ],
            )
            self.assertEqual(
                str(packet), "0x%02X PlayerListItemPacket("
                "action_type=UpdateGameModeAction, actions=["
                "UpdateGameModeAction(uuid=%r, gamemode=43)])"
                % (packet.id, fake_uuid))
            packet.write_fields(packet_buffer)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertEqual(by_uuid[fake_uuid].gamemode, 43)

            # Change the ping
            packet_buffer = PacketBuffer()
            packet = PlayerListItemPacket(
                context=context,
                action_type=PlayerListItemPacket.UpdateLatencyAction,
                actions=[
                    PlayerListItemPacket.UpdateLatencyAction(
                        uuid=fake_uuid, ping=70),
                ],
            )
            self.assertEqual(
                str(packet), "0x%02X PlayerListItemPacket("
                "action_type=UpdateLatencyAction, actions=["
                "UpdateLatencyAction(uuid=%r, ping=70)])"
                % (packet.id, fake_uuid))
            packet.write_fields(packet_buffer)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertEqual(by_uuid[fake_uuid].ping, 70)

            # Change the display name
            packet_buffer = PacketBuffer()
            packet = PlayerListItemPacket(
                context=context,
                action_type=PlayerListItemPacket.UpdateDisplayNameAction,
                actions=[
                    PlayerListItemPacket.UpdateDisplayNameAction(
                        uuid=fake_uuid, display_name='Badmonson'),
                ],
            )
            self.assertEqual(
                str(packet), "0x%02X PlayerListItemPacket("
                "action_type=UpdateDisplayNameAction, actions=["
                "UpdateDisplayNameAction(uuid=%r, display_name='Badmonson')])"
                % (packet.id, fake_uuid))
            packet.write_fields(packet_buffer)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertEqual(by_uuid[fake_uuid].display_name, 'Badmonson')

            # Remove the display name
            packet_buffer = PacketBuffer()
            PlayerListItemPacket(
                context=context,
                action_type=PlayerListItemPacket.UpdateDisplayNameAction,
                actions=[
                    PlayerListItemPacket.UpdateDisplayNameAction(
                        uuid=fake_uuid, display_name=None),
                ],
            ).write_fields(packet_buffer)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertIsNone(by_uuid[fake_uuid].display_name)

            # Remove the player
            packet_buffer = PacketBuffer()
            packet = PlayerListItemPacket(
                context=context,
                action_type=PlayerListItemPacket.RemovePlayerAction,
                actions=[
                    PlayerListItemPacket.RemovePlayerAction(uuid=fake_uuid),
                ],
            )
            self.assertEqual(
                str(packet), "0x%02X PlayerListItemPacket("
                "action_type=RemovePlayerAction, actions=[RemovePlayerAction("
                "uuid=%r)])" % (packet.id, fake_uuid))
            packet.write_fields(packet_buffer)
            self.read_and_apply(context, packet_buffer, player_list)
            self.assertNotIn(fake_uuid, player_list.players_by_uuid)
