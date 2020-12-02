import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from minecraft import SUPPORTED_PROTOCOL_VERSIONS
from minecraft.networking.connection import (
    LoginReactor, PlayingReactor, ConnectionContext
)
from minecraft.networking.packets import clientbound


latest_proto = SUPPORTED_PROTOCOL_VERSIONS[-1]


class LoginReactorTest(unittest.TestCase):

    @mock.patch('minecraft.networking.connection.encryption')
    def test_encryption_online_server(self, encrypt):
        connection = mock.MagicMock()
        connection.context = ConnectionContext(protocol_version=latest_proto)
        reactor = LoginReactor(connection)

        packet = clientbound.login.EncryptionRequestPacket()
        packet.server_id = "123"
        packet.public_key = b"asdf"
        packet.verify_token = b"23"

        secret = b"secret"
        encrypt.generate_shared_secret.return_value = secret
        encrypt.encrypt_token_and_secret.return_value = (b"a", b"b")
        encrypt.generate_verification_hash.return_value = b"hash"

        reactor.react(packet)

        encrypt.encrypt_token_and_secret.assert_called_once_with(
            packet.public_key, packet.verify_token, secret
        )
        connection.auth_token.join.assert_called_once_with(b"hash")
        self.assertEqual(connection.write_packet.call_count, 1)

    @mock.patch('minecraft.networking.connection.encryption')
    def test_encryption_offline_server(self, encrypt):
        connection = mock.MagicMock()
        connection.context = ConnectionContext(protocol_version=latest_proto)
        reactor = LoginReactor(connection)

        packet = clientbound.login.EncryptionRequestPacket()
        packet.server_id = "-"
        packet.public_key = b"asdf"
        packet.verify_token = b"23"

        secret = b"secret"
        encrypt.generate_shared_secret.return_value = secret
        encrypt.encrypt_token_and_secret.return_value = (b"a", b"b")

        reactor.react(packet)

        encrypt.encrypt_token_and_secret.assert_called_once_with(
            packet.public_key, packet.verify_token, secret
        )
        self.assertEqual(connection.auth_token.join.call_count, 0)
        self.assertEqual(connection.write_packet.call_count, 1)


class PlayingReactorTest(unittest.TestCase):

    def get_position_packet(self):
        packet = clientbound.play.PlayerPositionAndLookPacket()
        packet.x = 1.0
        packet.y = 2.0
        packet.z = 3.0
        packet.yaw = 4.0
        packet.pitch = 5.0

        packet.teleport_id = 42

        return packet

    def test_teleport_confirmation_old(self):
        connection = mock.MagicMock()
        connection.context = ConnectionContext(protocol_version=106)
        reactor = PlayingReactor(connection)

        packet = self.get_position_packet()
        reactor.react(packet)

        self.assertEqual(connection.write_packet.call_count, 1)
        response_packet = connection.write_packet.call_args[0][0]

        self.assertEqual(response_packet.x, 1.0)
        self.assertEqual(response_packet.feet_y, 2.0)
        self.assertEqual(response_packet.z, 3.0)
        self.assertEqual(response_packet.yaw, 4.0)
        self.assertEqual(response_packet.pitch, 5.0)
        self.assertTrue(response_packet.on_ground)

    def test_teleport_confirmation_new(self):
        connection = mock.MagicMock()
        connection.context = ConnectionContext(protocol_version=107)
        reactor = PlayingReactor(connection)

        packet = self.get_position_packet()
        reactor.react(packet)

        self.assertEqual(connection.write_packet.call_count, 1)

        response_packet = connection.write_packet.call_args[0][0]
        self.assertEqual(response_packet.teleport_id, 42)
