import unittest
import hashlib
from minecraft.networking.encryption import minecraft_sha1_hash_digest


class Hashing(unittest.TestCase):

    test_data = {'Notch': '4ed1f46bbe04bc756bcb17c0c7ce3e4632f06a48',
     'jeb_':  '-7c9d5b0044c130109a5d7b5fb5c317c02b4e28c1',
     'simon': '88e16a1019277b15d58faf0541e11910eb756f6'}

    def test_hashing(self):
        for input_value in self.test_data.iterkeys():
            sha1_hash = hashlib.sha1()
            sha1_hash.update(input_value)
            self.assertEquals(minecraft_sha1_hash_digest(sha1_hash), self.test_data[input_value])
        