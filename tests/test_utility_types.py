import unittest

from minecraft.networking.types import (
    Enum, BitFieldEnum, Vector, Position, PositionAndLook
)


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


class VectorTest(unittest.TestCase):
    def test_operators(self):
        self.assertEqual(Vector(1, -2, 0) + Vector(0, 1, 2), Vector(1, -1, 2))
        self.assertEqual(Vector(1, -2, 0) - Vector(0, 1, 2), Vector(1, -3, -2))
        self.assertEqual(-Vector(1, -2, 0), Vector(-1, 2, 0))
        self.assertEqual(Vector(1, -2, 0) * 2, Vector(2, -4, 0))
        self.assertEqual(2 * Vector(1, -2, 0), Vector(2, -4, 0))
        self.assertEqual(Vector(1, -2, 0) / 2, Vector(1/2, -2/2, 0/2))
        self.assertEqual(Vector(1, -2, 0) // 2, Vector(0, -1, 0))

    def test_repr(self):
        self.assertEqual(str(Vector(1, 2, 3)), 'Vector(1, 2, 3)')
        self.assertEqual(str(Position(1, 2, 3)), 'Position(1, 2, 3)')


class PositionAndLookTest(unittest.TestCase):
    """ This also tests the MutableRecord base type. """
    def test_properties(self):
        pos_look_1 = PositionAndLook(position=(1, 2, 3), look=(4, 5))
        pos_look_2 = PositionAndLook(x=1, y=2, z=3, yaw=4, pitch=5)
        string_repr = 'PositionAndLook(x=1, y=2, z=3, yaw=4, pitch=5)'

        self.assertEqual(pos_look_1, pos_look_2)
        self.assertEqual(pos_look_1.position, pos_look_1.position)
        self.assertEqual(pos_look_1.look, pos_look_2.look)
        self.assertEqual(hash(pos_look_1), hash(pos_look_2))
        self.assertEqual(str(pos_look_1), string_repr)

        self.assertFalse(pos_look_1 != pos_look_2)
        pos_look_1.position += Vector(1, 1, 1)
        self.assertTrue(pos_look_1 != pos_look_2)
