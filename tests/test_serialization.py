#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from minecraft.networking.types import (
    Type, Boolean, UnsignedByte, Byte, Short, UnsignedShort,
    Integer, VarInt, Long, Float, Double, ShortPrefixedByteArray,
    VarIntPrefixedByteArray, String as StringType
)
from minecraft.networking.packets import PacketBuffer


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

    def test_exceptions(self):
        base_type = Type()
        with self.assertRaises(NotImplementedError):
            base_type.read(None)

        with self.assertRaises(NotImplementedError):
            base_type.send(None, None)

        empty_socket = PacketBuffer()
        with self.assertRaises(Exception):
            VarInt.read(empty_socket)

    def test_varint(self):
        self.assertEqual(VarInt.size(2), 1)
        self.assertEqual(VarInt.size(1250), 2)

        packet_buffer = PacketBuffer()
        VarInt.send(50000, packet_buffer)
        packet_buffer.reset_cursor()

        self.assertEqual(VarInt.read(packet_buffer), 50000)
