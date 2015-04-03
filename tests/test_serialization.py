#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import string
from random import choice
from zlib import decompress
from minecraft.networking.types import (
    Type, Boolean, UnsignedByte, Byte, Short, UnsignedShort,
    Integer, VarInt, Long, Float, Double, ShortPrefixedByteArray,
    VarIntPrefixedByteArray, String as StringType
)
from minecraft.networking.packets import PacketBuffer, ChatPacket


TEST_DATA = {
    Boolean: [True, False],
    UnsignedByte: [0, 125],
    Byte: [-22, 22],
    Short: [-340, 22, 350],
    UnsignedShort: [0, 400],
    Integer: [-1000, 1000],
    VarInt: [1, 250, 50000, 10000000],
    Long: [50000000],
    Float: [21.000301],
    Double: [36.004002],
    ShortPrefixedByteArray: [bytes(245)],
    VarIntPrefixedByteArray: [bytes(1234)],
    StringType: ["hello world"]
}


class SerializationTest(unittest.TestCase):

    def test_serialization(self):
        for data_type in Type.__subclasses__():
            if data_type in TEST_DATA:
                test_cases = TEST_DATA[data_type]

                for test_data in test_cases:
                    packet_buffer = PacketBuffer()
                    data_type.send(test_data, packet_buffer)
                    packet_buffer.reset_cursor()

                    deserialized = data_type.read(packet_buffer)
                    if data_type is Float or data_type is Double:
                        self.assertAlmostEquals(test_data, deserialized, 3)
                    else:
                        self.assertEqual(test_data, deserialized)

    def test_varint(self):
        self.assertEqual(VarInt.size(2), 1)
        self.assertEqual(VarInt.size(1250), 2)

        packet_buffer = PacketBuffer()
        VarInt.send(50000, packet_buffer)
        packet_buffer.reset_cursor()

        self.assertEqual(VarInt.read_socket(packet_buffer), 50000)

    def test_packet(self):
        packet = ChatPacket()
        packet.message = u"κόσμε"

        packet_buffer = PacketBuffer()
        packet.write(packet_buffer)

        packet_buffer.reset_cursor()
        # Read the length and packet id
        VarInt.read(packet_buffer)
        packet_id = VarInt.read(packet_buffer)
        self.assertEqual(packet_id, packet.id)

        deserialized = ChatPacket()
        deserialized.read(packet_buffer)

        self.assertEqual(packet.message, deserialized.message)

    def test_compressed_packet(self):
        msg = ''.join(choice(string.ascii_lowercase) for i in range(500))

        packet = ChatPacket()
        packet.message = msg

        packet_buffer = PacketBuffer()
        packet.write(packet_buffer, compression_threshold=20)

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

        deserialized = ChatPacket()
        deserialized.read(packet_buffer)

        self.assertEqual(packet.message, deserialized.message)
