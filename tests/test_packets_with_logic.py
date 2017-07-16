import unittest
from minecraft.networking.types import (UUID, VarInt, String, Boolean)
from minecraft.networking.packets import PacketBuffer
from minecraft.networking.packets import PlayerPositionAndLookPacket
from minecraft.networking.packets import PlayerListItemPacket


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


fake_uuid = "12345678-1234-5678-1234-567812345678"


class PlayerListItemTest(unittest.TestCase):
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

    @staticmethod
    def make_add_player_packet(display_name=True):
        packet_buffer = PacketBuffer()

        VarInt.send(0, packet_buffer)  # action_id
        VarInt.send(1, packet_buffer)  # action count
        UUID.send(fake_uuid, packet_buffer)  # uuid
        String.send("player", packet_buffer)  # player name

        VarInt.send(2, packet_buffer)  # number of properties
        String.send("property1", packet_buffer)
        String.send("value1", packet_buffer)
        Boolean.send(False, packet_buffer)  # is signed
        String.send("property2", packet_buffer)
        String.send("value2", packet_buffer)
        Boolean.send(True, packet_buffer)  # is signed
        String.send("signature", packet_buffer)

        VarInt.send(42, packet_buffer)  # game mode
        VarInt.send(69, packet_buffer)  # ping
        Boolean.send(display_name, packet_buffer)  # has display name
        if display_name:
            String.send("display", packet_buffer)  # display name

        packet_buffer.reset_cursor()
        return packet_buffer

    def test_add_player_action(self):
        player_list = PlayerListItemPacket.PlayerList()

        packet_buffer = self.make_add_player_packet()

        packet = PlayerListItemPacket()
        packet.read(packet_buffer)
        packet.apply(player_list)

        self.assertIn(fake_uuid, player_list.players_by_uuid)
        player = player_list.players_by_uuid[fake_uuid]

        self.assertEqual(player.name, "player")
        self.assertEqual(player.properties[0].name, "property1")
        self.assertIsNone(player.properties[0].signature)
        self.assertEqual(player.properties[1].value, "value2")
        self.assertEqual(player.properties[1].signature, "signature")
        self.assertEqual(player.gamemode, 42)
        self.assertEqual(player.ping, 69)
        self.assertEqual(player.display_name, "display")

    @staticmethod
    def make_action_base(action_id):
        packet_buffer = PacketBuffer()
        VarInt.send(action_id, packet_buffer)
        VarInt.send(1, packet_buffer)  # action count
        UUID.send(fake_uuid, packet_buffer)

        return packet_buffer

    def read_and_apply(self, packet_buffer, player_list):
        packet_buffer.reset_cursor()
        packet = PlayerListItemPacket()
        packet.read(packet_buffer)
        packet.apply(player_list)

    def test_add_and_others(self):
        player_list = PlayerListItemPacket.PlayerList()
        by_uuid = player_list.players_by_uuid

        packet_buffer = self.make_add_player_packet()
        self.read_and_apply(packet_buffer, player_list)
        self.assertEqual(by_uuid[fake_uuid].gamemode, 42)
        self.assertEqual(by_uuid[fake_uuid].ping, 69)
        self.assertEqual(by_uuid[fake_uuid].display_name, "display")

        # Change the game mode
        packet_buffer = self.make_action_base(1)
        VarInt.send(43, packet_buffer)  # gamemode
        self.read_and_apply(packet_buffer, player_list)
        self.assertEqual(by_uuid[fake_uuid].gamemode, 43)

        # Change the ping
        packet_buffer = self.make_action_base(2)
        VarInt.send(70, packet_buffer)  # ping
        self.read_and_apply(packet_buffer, player_list)
        self.assertEqual(by_uuid[fake_uuid].ping, 70)

        # Remove the display name
        packet_buffer = self.make_action_base(3)
        Boolean.send(False, packet_buffer)
        self.read_and_apply(packet_buffer, player_list)
        self.assertIsNone(by_uuid[fake_uuid].display_name)

        # Change the display name
        packet_buffer = self.make_action_base(3)
        Boolean.send(True, packet_buffer)
        String.send("display2", packet_buffer)
        self.read_and_apply(packet_buffer, player_list)
        self.assertEqual(by_uuid[fake_uuid].display_name, "display2")

        # Remove the player
        packet_buffer = self.make_action_base(4)
        self.read_and_apply(packet_buffer, player_list)
        self.assertNotIn(fake_uuid, player_list.players_by_uuid)
