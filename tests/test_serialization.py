#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from minecraft.networking.types import (
    Type, Boolean, UnsignedByte, Byte, Short, UnsignedShort,
    Integer, FixedPointInteger, Angle, VarInt, Long, Float, Double,
    ShortPrefixedByteArray, VarIntPrefixedByteArray, UUID,
    String as StringType, Position, TrailingByteArray, UnsignedLong,
)
from minecraft.networking.packets.clientbound.play import (
    MultiBlockChangePacket
)
from minecraft.networking.packets import PacketBuffer
from minecraft.networking.connection import ConnectionContext
from minecraft import SUPPORTED_PROTOCOL_VERSIONS, RELEASE_PROTOCOL_VERSIONS


TEST_VERSIONS = list(RELEASE_PROTOCOL_VERSIONS)
if SUPPORTED_PROTOCOL_VERSIONS[-1] not in TEST_VERSIONS:
    TEST_VERSIONS.append(SUPPORTED_PROTOCOL_VERSIONS[-1])

TEST_DATA = {
    Boolean: [True, False],
    UnsignedByte: [0, 125],
    Byte: [-22, 22],
    Short: [-340, 22, 350],
    UnsignedShort: [0, 400],
    UnsignedLong: [0, 400],
    Integer: [-1000, 1000],
    FixedPointInteger: [float(-13098.3435), float(-0.83), float(1000)],
    Angle: [0, 360.0, 720, 47.12947238973, -108.7],
    VarInt: [1, 250, 50000, 10000000],
    Long: [50000000],
    Float: [21.000301],
    Double: [36.004002],
    ShortPrefixedByteArray: [bytes(245)],
    VarIntPrefixedByteArray: [bytes(1234)],
    TrailingByteArray: [b'Q^jO<5*|+o  LGc('],
    UUID: ["12345678-1234-5678-1234-567812345678"],
    StringType: ["hello world"],
    Position: [(758, 0, 691), (-500, -12, -684)],
    MultiBlockChangePacket.ChunkSectionPos: [
        (x, y, z)
        for x in [-0x200000, -123, -1, 0, 123, 0x1FFFFF]
        for z in [-0x200000, -456, -1, 0, 456, 0x1FFFFF]
        for y in [-0x80000, -789, -1, 0, 789, 0x7FFFF]
    ]
}


class SerializationTest(unittest.TestCase):
    def test_serialization(self):
        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            for data_type in Type.__subclasses__():
                if data_type in TEST_DATA:
                    test_cases = TEST_DATA[data_type]

                    for test_data in test_cases:
                        packet_buffer = PacketBuffer()
                        data_type.send_with_context(
                            test_data, packet_buffer, context)
                        packet_buffer.reset_cursor()

                        deserialized = data_type.read_with_context(
                            packet_buffer, context)
                        if data_type is FixedPointInteger:
                            self.assertAlmostEqual(
                                test_data, deserialized, delta=1.0/32.0)
                        elif data_type is Angle:
                            self.assertAlmostEqual(test_data % 360,
                                                   deserialized,
                                                   delta=360/256)
                        elif data_type is Float or data_type is Double:
                            self.assertAlmostEqual(test_data, deserialized, 3)
                        else:
                            self.assertEqual(test_data, deserialized)

    def test_exceptions(self):
        base_type = Type()
        with self.assertRaises(NotImplementedError):
            base_type.read(None)

        with self.assertRaises(NotImplementedError):
            base_type.read_with_context(None, None)

        with self.assertRaises(NotImplementedError):
            base_type.send(None, None)

        with self.assertRaises(NotImplementedError):
            base_type.send_with_context(None, None, None)

        with self.assertRaises(TypeError):
            Position.read(None)

        with self.assertRaises(TypeError):
            Position.send(None, None)

        empty_socket = PacketBuffer()
        with self.assertRaises(Exception):
            VarInt.read(empty_socket)

    def test_varint(self):
        self.assertEqual(VarInt.size(2), 1)
        self.assertEqual(VarInt.size(1250), 2)

        with self.assertRaises(ValueError):
            VarInt.size(2 ** 90)

        with self.assertRaises(ValueError):
            packet_buffer = PacketBuffer()
            VarInt.send(2 ** 49, packet_buffer)
            packet_buffer.reset_cursor()
            VarInt.read(packet_buffer)

        packet_buffer = PacketBuffer()
        VarInt.send(50000, packet_buffer)
        packet_buffer.reset_cursor()

        self.assertEqual(VarInt.read(packet_buffer), 50000)
