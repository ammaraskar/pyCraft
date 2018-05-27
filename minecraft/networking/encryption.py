import os
from hashlib import sha1
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def generate_shared_secret():
    return os.urandom(16)


def create_AES_cipher(shared_secret):
    cipher = Cipher(algorithms.AES(shared_secret), modes.CFB8(shared_secret),
                    backend=default_backend())
    return cipher


def encrypt_token_and_secret(pubkey, verification_token, shared_secret):
    """Encrypts the verification token and shared secret
    with the server's public key.

    :param pubkey: The RSA public key provided by the server
    :param verification_token: The verification token provided by the server
    :param shared_secret: The generated shared secret
    :return: A tuple containing (encrypted token, encrypted secret)
    """
    pubkey = load_der_public_key(pubkey, default_backend())

    encrypted_token = pubkey.encrypt(verification_token, PKCS1v15())
    encrypted_secret = pubkey.encrypt(shared_secret, PKCS1v15())
    return encrypted_token, encrypted_secret


def generate_verification_hash(server_id, shared_secret, public_key):
    verification_hash = sha1()

    verification_hash.update(server_id.encode('utf-8'))
    verification_hash.update(shared_secret)
    verification_hash.update(public_key)

    return minecraft_sha1_hash_digest(verification_hash)


def minecraft_sha1_hash_digest(sha1_hash):
    # Minecraft first parses the sha1 bytes as a signed number and then
    # spits outs its hex representation
    number_representation = _number_from_bytes(sha1_hash.digest(), signed=True)
    return format(number_representation, 'x')


def _number_from_bytes(b, signed=False):
    try:
        return int.from_bytes(b, byteorder='big', signed=signed)
    except AttributeError:  # pragma: no cover
        # py-2 compatibility
        if len(b) == 0:
            b = b'\x00'
        num = int(str(b).encode('hex'), 16)
        if signed and (ord(b[0]) & 0x80):
            num -= 2 ** (len(b) * 8)
        return num


class EncryptedFileObjectWrapper(object):
    def __init__(self, file_object, decryptor):
        self.actual_file_object = file_object
        self.decryptor = decryptor

    def read(self, length):
        return self.decryptor.update(self.actual_file_object.read(length))

    def fileno(self):
        return self.actual_file_object.fileno()

    def close(self):
        self.actual_file_object.close()


class EncryptedSocketWrapper(object):
    def __init__(self, socket, encryptor, decryptor):
        self.actual_socket = socket
        self.encryptor = encryptor
        self.decryptor = decryptor

    def recv(self, length):
        return self.decryptor.update(self.actual_socket.recv(length))

    def send(self, data):
        self.actual_socket.send(self.encryptor.update(data))

    def fileno(self):
        return self.actual_socket.fileno()

    def close(self):
        return self.actual_socket.close()

    def shutdown(self, *args, **kwds):
        return self.actual_socket.shutdown(*args, **kwds)
