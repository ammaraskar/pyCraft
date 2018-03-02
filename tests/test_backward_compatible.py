import unittest

from minecraft.networking import packets
from minecraft.networking import types
from minecraft.networking.packets import clientbound
from minecraft.networking.packets import serverbound


class LegacyPacketNamesTest(unittest.TestCase):
    def test_legacy_packets_equal_current_packets(self):
        self.assertEqual(packets.KeepAlivePacket,
                         packets.AbstractKeepAlivePacket)

        self.assertEqual(packets.state_handshake_clientbound,
                         clientbound.handshake.get_packets)
        self.assertEqual(packets.HandShakePacket,
                         serverbound.handshake.HandShakePacket)
        self.assertEqual(packets.state_handshake_serverbound,
                         serverbound.handshake.get_packets)

        self.assertEqual(packets.ResponsePacket,
                         clientbound.status.ResponsePacket)
        self.assertEqual(packets.PingPacketResponse,
                         clientbound.status.PingResponsePacket)
        self.assertEqual(packets.state_status_clientbound,
                         clientbound.status.get_packets)
        self.assertEqual(packets.RequestPacket,
                         serverbound.status.RequestPacket)
        self.assertEqual(packets.PingPacket,
                         serverbound.status.PingPacket)
        self.assertEqual(packets.state_status_serverbound,
                         serverbound.status.get_packets)

        self.assertEqual(packets.DisconnectPacket,
                         clientbound.login.DisconnectPacket)
        self.assertEqual(packets.EncryptionRequestPacket,
                         clientbound.login.EncryptionRequestPacket)
        self.assertEqual(packets.LoginSuccessPacket,
                         clientbound.login.LoginSuccessPacket)
        self.assertEqual(packets.SetCompressionPacket,
                         clientbound.login.SetCompressionPacket)
        self.assertEqual(packets.state_login_clientbound,
                         clientbound.login.get_packets)
        self.assertEqual(packets.LoginStartPacket,
                         serverbound.login.LoginStartPacket)
        self.assertEqual(packets.EncryptionResponsePacket,
                         serverbound.login.EncryptionResponsePacket)
        self.assertEqual(packets.state_login_serverbound,
                         serverbound.login.get_packets)

        self.assertEqual(packets.KeepAlivePacketClientbound,
                         clientbound.play.KeepAlivePacket)
        self.assertEqual(packets.KeepAlivePacketServerbound,
                         serverbound.play.KeepAlivePacket)
        self.assertEqual(packets.JoinGamePacket,
                         clientbound.play.JoinGamePacket)
        self.assertEqual(packets.ChatMessagePacket,
                         clientbound.play.ChatMessagePacket)
        self.assertEqual(packets.PlayerPositionAndLookPacket,
                         clientbound.play.PlayerPositionAndLookPacket)
        self.assertEqual(packets.DisconnectPacketPlayState,
                         clientbound.play.DisconnectPacket)
        self.assertEqual(packets.SetCompressionPacketPlayState,
                         clientbound.play.SetCompressionPacket)
        self.assertEqual(packets.PlayerListItemPacket,
                         clientbound.play.PlayerListItemPacket)
        self.assertEqual(packets.MapPacket,
                         clientbound.play.MapPacket)
        self.assertEqual(packets.state_playing_clientbound,
                         clientbound.play.get_packets)
        self.assertEqual(packets.ChatPacket,
                         serverbound.play.ChatPacket)
        self.assertEqual(packets.PositionAndLookPacket,
                         serverbound.play.PositionAndLookPacket)
        self.assertEqual(packets.TeleportConfirmPacket,
                         serverbound.play.TeleportConfirmPacket)
        self.assertEqual(packets.AnimationPacketServerbound,
                         serverbound.play.AnimationPacket)
        self.assertEqual(packets.state_playing_serverbound,
                         serverbound.play.get_packets)


class ClassMemberAliasesTest(unittest.TestCase):
    def test_alias_values(self):
        self.assertEqual(serverbound.play.AnimationPacket.HAND_MAIN,
                         types.RelativeHand.MAIN)
        self.assertEqual(serverbound.play.AnimationPacket.HAND_OFF,
                         types.RelativeHand.OFF)

        self.assertEqual(serverbound.play.ClientSettingsPacket.Hand.LEFT,
                         types.AbsoluteHand.LEFT)
        self.assertEqual(serverbound.play.ClientSettingsPacket.Hand.RIGHT,
                         types.AbsoluteHand.RIGHT)
