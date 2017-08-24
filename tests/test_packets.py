# -*- coding: utf-8 -*-
import unittest
import string
from zlib import decompress
from random import choice

from minecraft import SUPPORTED_PROTOCOL_VERSIONS
from minecraft.networking.connection import ConnectionContext
from minecraft.networking.types import VarInt, Enum, BitFieldEnum
from minecraft.networking.packets import (
    Packet, PacketBuffer, PacketListener, KeepAlivePacket, serverbound)


class PacketBufferTest(unittest.TestCase):
    def test_basic_read_write(self):
        message = b"hello"

        packet_buffer = PacketBuffer()
        packet_buffer.send(message)

        packet_buffer.reset_cursor()
        self.assertEqual(packet_buffer.read(), message)
        packet_buffer.reset_cursor()
        self.assertEqual(packet_buffer.recv(), message)

        packet_buffer.reset()
        self.assertNotEqual(packet_buffer.read(), message)

    def test_get_writable(self):
        message = b"hello"

        packet_buffer = PacketBuffer()
        packet_buffer.send(message)

        self.assertEqual(packet_buffer.get_writable(), message)


class PacketSerializatonTest(unittest.TestCase):

    def test_packet(self):
        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            packet = serverbound.play.ChatPacket(context)
            packet.message = u"κόσμε"

            packet_buffer = PacketBuffer()
            packet.write(packet_buffer)

            packet_buffer.reset_cursor()
            # Read the length and packet id
            VarInt.read(packet_buffer)
            packet_id = VarInt.read(packet_buffer)
            self.assertEqual(packet_id, packet.id)

            deserialized = serverbound.play.ChatPacket(context)
            deserialized.read(packet_buffer)

            self.assertEqual(packet.message, deserialized.message)

    def test_compressed_packet(self):
        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            msg = ''.join(choice(string.ascii_lowercase) for i in range(500))
            packet = serverbound.play.ChatPacket(context)
            packet.message = msg

            self.write_read_packet(packet, 20)
            self.write_read_packet(packet, -1)

    def write_read_packet(self, packet, compression_threshold):
        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            packet_buffer = PacketBuffer()
            packet.write(packet_buffer, compression_threshold)

            packet_buffer.reset_cursor()

            VarInt.read(packet_buffer)
            compressed_size = VarInt.read(packet_buffer)

            if compressed_size > 0:
                decompressed = decompress(packet_buffer.read(compressed_size))
                packet_buffer.reset()
                packet_buffer.send(decompressed)
                packet_buffer.reset_cursor()

            packet_id = VarInt.read(packet_buffer)
            self.assertEqual(packet_id, packet.id)

            deserialized = serverbound.play.ChatPacket(context)
            deserialized.read(packet_buffer)

            self.assertEqual(packet.message, deserialized.message)


class PacketListenerTest(unittest.TestCase):

    def test_listener(self):
        message = "hello world"

        def test_packet(chat_packet):
            self.assertEqual(chat_packet.message, message)

        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            listener = PacketListener(test_packet, serverbound.play.ChatPacket)

            packet = serverbound.play.ChatPacket(context).set_values(
                message=message)
            uncalled_packet = KeepAlivePacket().set_values(keep_alive_id=0)

            listener.call_packet(packet)
            listener.call_packet(uncalled_packet)


class PacketEnumTest(unittest.TestCase):
    def test_packet_str(self):
        class ExamplePacket(Packet):
            id = 0x00
            packet_name = 'example'
            definition = [
                {'alpha': VarInt},
                {'beta': VarInt},
                {'gamma': VarInt}]

            class Alpha(Enum):
                ZERO = 0

            class Beta(Enum):
                ONE = 1

        self.assertEqual(
            str(ExamplePacket(ConnectionContext(), alpha=0, beta=0, gamma=0)),
            '0x00 ExamplePacket(alpha=ZERO, beta=0, gamma=0)')


class EnumTest(unittest.TestCase):
    def test_enum(self):
        class Example(Enum):
            ONE = 1
            TWO = 2
            THREE = 3

        self.assertEqual(
            list(map(Example.name_from_value, range(5))),
            [None, 'ONE', 'TWO', 'THREE', None])


class BitFieldEnumTest(unittest.TestCase):
    def test_name_from_value(self):
        class Example1(BitFieldEnum):
            ONE = 1
            TWO = 2
            FOUR = 4
            ALL = 7
            NONE = 0

        self.assertEqual(
            list(map(Example1.name_from_value, range(9))),
            ['NONE', 'ONE', 'TWO', 'ONE|TWO', 'FOUR',
             'ONE|FOUR', 'TWO|FOUR', 'ALL', None])

        class Example2(BitFieldEnum):
            ONE = 1
            TWO = 2
            FOUR = 4

        self.assertEqual(
            list(map(Example2.name_from_value, range(9))),
            ['0', 'ONE', 'TWO', 'ONE|TWO', 'FOUR',
             'ONE|FOUR', 'TWO|FOUR', 'ONE|TWO|FOUR', None])
