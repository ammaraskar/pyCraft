# -*- coding: utf-8 -*-
import unittest
import string
import logging
import struct
from zlib import decompress
from random import choice

from minecraft import SUPPORTED_PROTOCOL_VERSIONS, RELEASE_PROTOCOL_VERSIONS
from minecraft.networking.connection import ConnectionContext
from minecraft.networking.types import (
    VarInt, Enum, Vector, PositionAndLook, OriginPoint,
)
from minecraft.networking.packets import (
    Packet, PacketBuffer, PacketListener, KeepAlivePacket, serverbound,
    clientbound
)

TEST_VERSIONS = list(RELEASE_PROTOCOL_VERSIONS)
if SUPPORTED_PROTOCOL_VERSIONS[-1] not in TEST_VERSIONS:
    TEST_VERSIONS.append(SUPPORTED_PROTOCOL_VERSIONS[-1])


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


class PacketSerializationTest(unittest.TestCase):

    def test_packet(self):
        for protocol_version in TEST_VERSIONS:
            logging.debug('protocol_version = %r' % protocol_version)
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
        for protocol_version in TEST_VERSIONS:
            logging.debug('protocol_version = %r' % protocol_version)
            context = ConnectionContext(protocol_version=protocol_version)

            msg = ''.join(choice(string.ascii_lowercase) for i in range(500))
            packet = serverbound.play.ChatPacket(context)
            packet.message = msg

            self.write_read_packet(packet, 20)
            self.write_read_packet(packet, -1)

    def write_read_packet(self, packet, compression_threshold):
        for protocol_version in TEST_VERSIONS:
            logging.debug('protocol_version = %r' % protocol_version)
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

        for protocol_version in TEST_VERSIONS:
            logging.debug('protocol_version = %r' % protocol_version)
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
            '0x00 ExamplePacket(alpha=ZERO, beta=0, gamma=0)'
        )


class TestReadWritePackets(unittest.TestCase):
    maxDiff = None

    def test_explosion_packet(self):
        Record = clientbound.play.ExplosionPacket.Record
        packet = clientbound.play.ExplosionPacket(
                    position=Vector(787, -37, 0), radius=15,
                    records=[Record(-14, -116, -5), Record(-77, 34, -36),
                             Record(-35, -127, 95), Record(11, 113, -8)],
                    player_motion=Vector(4, 5, 0))

        self.assertEqual(
            str(packet),
            'ExplosionPacket(x=787, y=-37, z=0, radius=15, records=['
            'Record(-14, -116, -5), Record(-77, 34, -36), '
            'Record(-35, -127, 95), Record(11, 113, -8)], '
            'player_motion_x=4, player_motion_y=5, player_motion_z=0)'
        )

        self._test_read_write_packet(packet)

    def test_combat_event_packet(self):
        packet = clientbound.play.CombatEventPacket(
            event=clientbound.play.CombatEventPacket.EnterCombatEvent())
        self.assertEqual(
            str(packet),
            'CombatEventPacket(event=EnterCombatEvent())'
        )
        self._test_read_write_packet(packet)

        packet = clientbound.play.CombatEventPacket(
            event=clientbound.play.CombatEventPacket.EndCombatEvent(
                duration=415, entity_id=91063502))
        self.assertEqual(str(packet),
                         'CombatEventPacket(event=EndCombatEvent('
                         'duration=415, entity_id=91063502))')
        self._test_read_write_packet(packet)

        packet = clientbound.play.CombatEventPacket(
            event=clientbound.play.CombatEventPacket.EntityDeadEvent(
                player_id=178, entity_id=36, message='RIP'))
        self.assertEqual(
            str(packet),
            "CombatEventPacket(event=EntityDeadEvent("
            "player_id=178, entity_id=36, message='RIP'))"
        )
        self._test_read_write_packet(packet)

    def test_multi_block_change_packet(self):
        Record = clientbound.play.MultiBlockChangePacket.Record

        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext()
            context.protocol_version = protocol_version
            packet = clientbound.play.MultiBlockChangePacket(context)

            if context.protocol_later_eq(741):
                packet.chunk_section_pos = Vector(167, 17, 33)
                packet.invert_trust_edges = False
            else:
                packet.chunk_x, packet.chunk_z = 167, 17
                self.assertEqual(packet.chunk_pos, (167, 17))

            packet.records = [
                Record(x=1, y=2, z=3, blockId=56, blockMeta=13),
                Record(position=Vector(1, 2, 3), block_state_id=909),
                Record(position=(1, 2, 3), blockStateId=909),
            ]

            for i in range(3):
                self.assertEqual(packet.records[i].blockId, 56)
                self.assertEqual(packet.records[i].blockMeta, 13)
                self.assertEqual(packet.records[i].blockStateId, 909)
                self.assertEqual(packet.records[i].position, Vector(1, 2, 3))

            self._test_read_write_packet(packet, context)

    def test_spawn_object_packet(self):
        for protocol_version in TEST_VERSIONS:
            logging.debug('protocol_version = %r' % protocol_version)
            context = ConnectionContext(protocol_version=protocol_version)

            EntityType = clientbound.play.SpawnObjectPacket.field_enum(
                            'type_id', context)

            pos_look = PositionAndLook(
                position=(Vector(68.0, 38.0, 76.0)
                          if context.protocol_later_eq(100) else
                          Vector(68, 38, 76)),
                yaw=263.494, pitch=180)
            velocity = Vector(21, 55, 41)
            entity_id, type_name, type_id = 49846, 'EGG', EntityType.EGG

            packet = clientbound.play.SpawnObjectPacket(
                        context=context,
                        x=pos_look.x, y=pos_look.y, z=pos_look.z,
                        yaw=pos_look.yaw, pitch=pos_look.pitch,
                        velocity_x=velocity.x, velocity_y=velocity.y,
                        velocity_z=velocity.z,
                        entity_id=entity_id, type_id=type_id, data=1)
            if context.protocol_later_eq(49):
                object_uuid = 'd9568851-85bc-4a10-8d6a-261d130626fa'
                packet.object_uuid = object_uuid
                self.assertEqual(packet.objectUUID, object_uuid)
            self.assertEqual(packet.position_and_look, pos_look)
            self.assertEqual(packet.position, pos_look.position)
            self.assertEqual(packet.velocity, velocity)
            self.assertEqual(packet.type, type_name)

            self.assertEqual(
                str(packet),
                "0x%02X SpawnObjectPacket(entity_id=49846, "
                "object_uuid='d9568851-85bc-4a10-8d6a-261d130626fa', "
                "type_id=EGG, x=68.0, y=38.0, z=76.0, pitch=180, yaw=263.494, "
                "data=1, velocity_x=21, velocity_y=55, velocity_z=41)"
                % packet.id if context.protocol_later_eq(100) else
                "0x%02X SpawnObjectPacket(entity_id=49846, "
                "object_uuid='d9568851-85bc-4a10-8d6a-261d130626fa', "
                "type_id=EGG, x=68, y=38, z=76, pitch=180, yaw=263.494, "
                "data=1, velocity_x=21, velocity_y=55, velocity_z=41)"
                % packet.id if context.protocol_later_eq(49) else
                "0x%02X SpawnObjectPacket(entity_id=49846, type_id=EGG, "
                "x=68, y=38, z=76, pitch=180, yaw=263.494, data=1, "
                "velocity_x=21, velocity_y=55, velocity_z=41)" % packet.id
            )

            packet2 = clientbound.play.SpawnObjectPacket(
                        context=context, position_and_look=pos_look,
                        velocity=velocity, type=type_name,
                        entity_id=entity_id, data=1)
            if context.protocol_later_eq(49):
                packet2.object_uuid = object_uuid
            self.assertEqual(packet.__dict__, packet2.__dict__)

            packet2.position = pos_look.position
            self.assertEqual(packet.position, packet2.position)

            packet2.data = 0
            if context.protocol_earlier(49):
                del packet2.velocity
            self._test_read_write_packet(packet, context,
                                         yaw=360/256, pitch=360/256)
            self._test_read_write_packet(packet2, context,
                                         yaw=360/256, pitch=360/256)

    def test_sound_effect_packet(self):
        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            packet = clientbound.play.SoundEffectPacket(
                sound_id=545, effect_position=Vector(0.125, 300.0, 50.5),
                volume=0.75)
            if context.protocol_later_eq(201):
                packet.pitch = struct.unpack('f', struct.pack('f', 1.5))[0]
            else:
                packet.pitch = int(1.5 / 63.5) * 63.5
            if context.protocol_later_eq(95):
                packet.sound_category = \
                    clientbound.play.SoundEffectPacket.SoundCategory.NEUTRAL

            self._test_read_write_packet(packet, context)

    def test_face_player_packet(self):
        for protocol_version in TEST_VERSIONS:
            context = ConnectionContext(protocol_version=protocol_version)

            packet = clientbound.play.FacePlayerPacket(context)
            packet.target = 1.0, -2.0, 3.5
            packet.entity_id = None
            if context.protocol_later_eq(353):
                packet.origin = OriginPoint.EYES
            self.assertEqual(
                str(packet),
                "0x%02X FacePlayerPacket(origin=EYES, x=1.0, y=-2.0, z=3.5, "
                "entity_id=None)" % packet.id
                if context.protocol_later_eq(353) else
                "0x%02X FacePlayerPacket(entity_id=None, x=1.0, y=-2.0, z=3.5)"
                % packet.id
            )
            self._test_read_write_packet(packet, context)

            packet.entity_id = 123
            if context.protocol_later_eq(353):
                packet.entity_origin = OriginPoint.FEET
            else:
                del packet.target
            self.assertEqual(
                str(packet),
                "0x%02X FacePlayerPacket(origin=EYES, x=1.0, y=-2.0, z=3.5, "
                "entity_id=123, entity_origin=FEET)" % packet.id
                if context.protocol_later_eq(353) else
                "0x%02X FacePlayerPacket(entity_id=123)" % packet.id
            )
            self._test_read_write_packet(packet, context)

    def _test_read_write_packet(self, packet_in, context=None, **kwargs):
        """
        If kwargs are specified, the key will be tested against the
        respective delta value. Useful for testing FixedPointNumbers
        where there is precision lost in the resulting value.
        """
        if context is None:
            for protocol_version in TEST_VERSIONS:
                logging.debug('protocol_version = %r' % protocol_version)
                context = ConnectionContext(protocol_version=protocol_version)
                self._test_read_write_packet(packet_in, context)
        else:
            packet_in.context = context
            packet_buffer = PacketBuffer()
            packet_in.write(packet_buffer)
            packet_buffer.reset_cursor()
            VarInt.read(packet_buffer)
            packet_id = VarInt.read(packet_buffer)
            self.assertEqual(packet_id, packet_in.id)

            packet_out = type(packet_in)(context=context)
            packet_out.read(packet_buffer)
            self.assertIs(type(packet_in), type(packet_out))

            for packet_attr, precision in kwargs.items():
                packet_attribute_in = packet_in.__dict__.pop(packet_attr)
                packet_attribute_out = packet_out.__dict__.pop(packet_attr)
                self.assertAlmostEqual(packet_attribute_in,
                                       packet_attribute_out,
                                       delta=precision)

            self.assertEqual(packet_in.__dict__, packet_out.__dict__)
