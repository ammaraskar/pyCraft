import os
import unittest
import hashlib
from io import BytesIO
from minecraft.networking.encryption import (
    minecraft_sha1_hash_digest,
    encrypt_token_and_secret,
    generate_shared_secret,
    generate_verification_hash,
    create_AES_cipher,
    EncryptedFileObjectWrapper,
    EncryptedSocketWrapper
)
from minecraft.networking.packets import clientbound
from tests import test_connection

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_private_key

KEY_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            "encryption")


def setUpModule():
    global private_key, public_key, token

    with open(os.path.join(KEY_LOCATION, "priv_key.bin"), "rb") as f:
        private_key = f.read()
    private_key = load_der_private_key(private_key, None, default_backend())

    with open(os.path.join(KEY_LOCATION, "pub_key.bin"), "rb") as f:
        public_key = f.read()

    token = generate_shared_secret()


def tearDownModule():
    global private_key, public_key, token
    del private_key, public_key, token


class Hashing(unittest.TestCase):
    test_data = {'Notch': '4ed1f46bbe04bc756bcb17c0c7ce3e4632f06a48',
                 'jeb_': '-7c9d5b0044c130109a5d7b5fb5c317c02b4e28c1',
                 'simon': '88e16a1019277b15d58faf0541e11910eb756f6'}

    def test_hashing(self):
        for input_value, result in self.test_data.items():
            sha1_hash = hashlib.sha1()
            sha1_hash.update(input_value.encode('utf-8'))
            self.assertEquals(minecraft_sha1_hash_digest(sha1_hash), result)


class Encryption(unittest.TestCase):

    def test_token_secret_encryption(self):
        secret = generate_shared_secret()
        encrypted_token, encrypted_secret = \
            encrypt_token_and_secret(public_key, token, secret)
        decrypted_token = private_key.decrypt(encrypted_token, PKCS1v15())
        decrypted_secret = private_key.decrypt(encrypted_secret, PKCS1v15())

        self.assertEquals(token, decrypted_token)
        self.assertEquals(secret, decrypted_secret)

    def test_generate_hash(self):
        verification_hash = generate_verification_hash(
            u"", "secret".encode('utf-8'),  public_key)
        self.assertEquals("1f142e737a84a974a5f2a22f6174a78d80fd97f5",
                          verification_hash)

    def test_file_object_wrapper(self):
        cipher = create_AES_cipher(generate_shared_secret())
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        test_data = "hello".encode('utf-8')
        io = BytesIO()
        io.write(encryptor.update(test_data))
        io.seek(0)

        file_object_wrapper = EncryptedFileObjectWrapper(io, decryptor)
        decrypted_data = file_object_wrapper.read(len(test_data))

        self.assertEqual(test_data, decrypted_data)

    def test_socket_wrapper(self):
        secret = generate_shared_secret()

        cipher = create_AES_cipher(secret)
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        server_cipher = create_AES_cipher(secret)
        server_encryptor = server_cipher.encryptor()
        server_decryptor = server_cipher.decryptor()

        mock_socket = MockSocket(server_encryptor, server_decryptor)
        wrapper = EncryptedSocketWrapper(mock_socket, encryptor, decryptor)

        self.assertEqual(wrapper.fileno(), 0)

        # Ensure that the 12 bytes we receive are the same as the 12 bytes
        # sent by the server, after undergoing encryption
        self.assertEqual(wrapper.recv(12), mock_socket.raw_data[:12])

        # Ensure that hello reaches the server properly after undergoing
        # encryption
        test_data = "hello".encode('utf-8')
        wrapper.send(test_data)
        self.assertEqual(test_data, mock_socket.received)


class EncryptedConnection(test_connection.ConnectTest):
    def test_connect(self):
        self._test_connect(private_key=private_key,
                           public_key_bytes=public_key)

    def _start_client(self, client):
        def handle_login_success(_packet):
            assert isinstance(client.socket, EncryptedSocketWrapper)
            assert isinstance(client.file_object, EncryptedFileObjectWrapper)
        client.register_packet_listener(
            handle_login_success, clientbound.login.LoginSuccessPacket)
        super(EncryptedConnection, self)._start_client(client)


class EncryptedCompressedConnection(EncryptedConnection,
                                    test_connection.ConnectCompressionLowTest):
    pass


# Regression test for <https://github.com/ammaraskar/pyCraft/issues/109>.
class EncryptedCompressedReconnect(test_connection.ReconnectTest,
                                   EncryptedCompressedConnection):
    pass


class MockSocket(object):

    def __init__(self, encryptor, decryptor):
        self.raw_data = os.urandom(100)
        self.encryptor = encryptor
        self.decryptor = decryptor
        self.received = None

    # when we receive data from the server
    # it'll be encrypted
    def recv(self, length):
        return self.encryptor.update(self.raw_data[:length])

    # decrypt the data as it reaches
    # the server side
    def send(self, data):
        self.received = self.decryptor.update(data)

    def fileno(self):
        return 0
