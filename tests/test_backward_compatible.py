import unittest

from minecraft import SUPPORTED_PROTOCOL_VERSIONS
from minecraft import utility
from minecraft.networking.connection import ConnectionContext
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


class LegacyTypesTest(unittest.TestCase):
    def test_legacy_types(self):
        self.assertIsInstance(types.FixedPointInteger, types.FixedPoint)
        self.assertEqual(types.FixedPointInteger.denominator, 32)

        for attr in ('descriptor', 'overridable_descriptor',
                     'overridable_property', 'attribute_alias',
                     'multi_attribute_alias', 'attribute_transform',
                     'class_and_instancemethod'):
            self.assertEqual(getattr(types, attr), getattr(utility, attr))


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

    def test_block_change_packet(self):
        context = ConnectionContext()
        context.protocol_version = SUPPORTED_PROTOCOL_VERSIONS[-1]
        bi, bm = 358, 9
        packet = clientbound.play.BlockChangePacket(blockId=bi, blockMeta=bm)
        self.assertEqual((packet.blockId, packet.blockMeta), (bi, bm))
        self.assertEqual(packet.blockStateId, packet.block_state_id)

    def test_join_game_packet(self):
        GameMode = types.GameMode
        context = ConnectionContext()
        for pure_game_mode in (GameMode.SURVIVAL, GameMode.CREATIVE,
                               GameMode.ADVENTURE, GameMode.SPECTATOR):
            for is_hardcore in (False, True):
                context.protocol_version = 70
                game_mode = \
                    pure_game_mode | GameMode.HARDCORE \
                    if is_hardcore else pure_game_mode

                packet = clientbound.play.JoinGamePacket()
                packet.game_mode = game_mode
                packet.context = context
                self.assertEqual(packet.pure_game_mode, pure_game_mode)
                self.assertEqual(packet.is_hardcore, is_hardcore)

                del packet.context
                del packet.is_hardcore
                packet.context = context
                self.assertEqual(packet.game_mode, packet.pure_game_mode)

                del packet.context
                del packet.game_mode
                packet.context = context
                self.assertFalse(hasattr(packet, 'is_hardcore'))

                packet = clientbound.play.JoinGamePacket()
                packet.pure_game_mode = game_mode
                packet.is_hardcore = is_hardcore
                packet.context = context
                self.assertEqual(packet.game_mode, game_mode)

                context.protocol_version = 738
                game_mode = pure_game_mode | GameMode.HARDCORE

                packet = clientbound.play.JoinGamePacket()
                packet.game_mode = game_mode
                packet.is_hardcore = is_hardcore
                packet.context = context
                self.assertEqual(packet.game_mode, game_mode)
                self.assertEqual(packet.pure_game_mode, game_mode)
                self.assertEqual(packet.is_hardcore, is_hardcore)

                del packet.context
                packet.is_hardcore = is_hardcore
                packet.context = context
                self.assertEqual(packet.game_mode, game_mode)
                self.assertEqual(packet.pure_game_mode, game_mode)

                with self.assertRaises(AttributeError):
                    del packet.pure_game_mode

    def test_entity_position_delta_packet(self):
        packet = clientbound.play.EntityPositionDeltaPacket()
        packet.delta_x = -32768
        packet.delta_y = 33
        packet.delta_z = 32767
        self.assertEqual(packet.delta_x_float, -8.0)
        self.assertEqual(packet.delta_y_float, 0.008056640625)
        self.assertEqual(packet.delta_z_float, 7.999755859375)
        self.assertEqual(packet.delta_x, -32768)
        self.assertEqual(packet.delta_y, 33)
        self.assertEqual(packet.delta_z, 32767)
