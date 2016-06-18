# -*- coding: utf-8 -*-
import unittest
import string
from zlib import decompress
from random import choice

from minecraft import SUPPORTED_PROTOCOL_VERSIONS
from minecraft.networking.connection import ConnectionContext
from minecraft.networking.types import VarInt
from minecraft.networking.packets import (
    PacketBuffer, ChatPacket, KeepAlivePacket, PacketListener)


class PacketSerializatonTest(unittest.TestCase):

    def test_packet(self):
        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            packet = ChatPacket(context)
            packet.message = u"κόσμε"

            packet_buffer = PacketBuffer()
            packet.write(packet_buffer)

            packet_buffer.reset_cursor()
            # Read the length and packet id
            VarInt.read(packet_buffer)
            packet_id = VarInt.read(packet_buffer)
            self.assertEqual(packet_id, packet.id)

            deserialized = ChatPacket(context)
            deserialized.read(packet_buffer)

            self.assertEqual(packet.message, deserialized.message)

    def test_compressed_packet(self):
        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            msg = ''.join(choice(string.ascii_lowercase) for i in range(500))
            packet = ChatPacket(context)
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

            deserialized = ChatPacket(context)
            deserialized.read(packet_buffer)

            self.assertEqual(packet.message, deserialized.message)


class PacketListenerTest(unittest.TestCase):

    def test_listener(self):
        message = "hello world"

        def test_packet(chat_packet):
            self.assertEqual(chat_packet.message, message)

        for protocol_version in SUPPORTED_PROTOCOL_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            listener = PacketListener(test_packet, ChatPacket)

            packet = ChatPacket(context).set_values(message=message)
            uncalled_packet = KeepAlivePacket().set_values(keep_alive_id=0)

            listener.call_packet(packet)
            listener.call_packet(uncalled_packet)
