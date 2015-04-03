import unittest
import minecraft.networking.connection as conn


class ConnectionTest(unittest.TestCase):

    def test_connection(self):
        connection = conn.Connection("localhost", 25565, None)
        self.assertFalse(connection.options.compression_enabled)
