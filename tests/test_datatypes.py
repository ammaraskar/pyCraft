from minecraft.networking.datatypes import *
from minecraft.exceptions import DeserializationError

import unittest


# # Note, we use the actual classes as keys.
# # Format: DATATYPE_OBJ = (LIST_OF_VALID_VALUES, LIST_OF_INVALID_VALUES)
# TEST_DATA = {
#     Boolean: [True, False],
#     Byte: [-127, -25, 0, 125],
#     UnsignedByte: [0, 125],
#     Byte: [-22, 22],
#     Short: [-340, 22, 350],
#     UnsignedShort: [0, 400],
#     Integer: [-1000, 1000],
#     VarInt: [1, 250, 50000, 10000000],
#     Long: [50000000],
#     Float: [21.000301],
#     Double: [36.004002],
#     ShortPrefixedByteArray: [bytes(245)],
#     VarIntPrefixedByteArray: [bytes(1234)],
#     StringType: ["hello world"]
# }


class BaseDatatypeTester(unittest.TestCase):
    DATATYPE_CLS = Datatype  # We use Datatype as a an example here.

    # TEST_DATA_VALID_VALUES should have the following format:
    # [(DESERIALIZED_VALUE, SERIALIZED_VALUE), ...]
    #
    # So that DESERIALIZED_VALUE is SERIALIZED_VALUE when serialized
    # and vice versa.

    TEST_DATA_VALID_VALUES = []

    # TEST_DATA_INVALID_SERIALIZATION_VALUES should be a list of tuples
    # containing the value and the expected exception.
    TEST_DATA_INVALID_SERIALIZATION_VALUES = []

    # TEST_DATA_INVALID_DESERIALIZATION_VALUES should be a list of tuples
    # containing the value and the expected exception.
    TEST_DATA_INVALID_DESERIALIZATION_VALUES = []

    def test_init(self):
        d = self.DATATYPE_CLS()  # noqa

    def test_init_with_arg(self):
        # We shouldn't accept any parameters.
        with self.assertRaises(TypeError):
            d = self.DATATYPE_CLS("This is a positional argument...")  # noqa

    def test_valid_data_serialization_values(self):
        for deserialized_val, serialized_val in self.TEST_DATA_VALID_VALUES:
            self.assertEqual(self.DATATYPE_CLS.serialize(deserialized_val),
                             serialized_val)

    def test_valid_data_deserialization_values(self):
        for deserialized_val, serialized_val in self.TEST_DATA_VALID_VALUES:
            self.assertEqual(self.DATATYPE_CLS.deserialize(serialized_val),
                             deserialized_val)

    def test_invalid_data_serialization_values(self):
        for value, exception in self.TEST_DATA_INVALID_SERIALIZATION_VALUES:
            with self.assertRaises(exception):
                self.DATATYPE_CLS.serialize(value)

    def test_invalid_data_deserialization_values(self):
        for value, exception in self.TEST_DATA_INVALID_DESERIALIZATION_VALUES:
            with self.assertRaises(exception):
                self.DATATYPE_CLS.deserialize(value)


class DatatypeTest(BaseDatatypeTester):
    DATATYPE_CLS = Datatype


class BooleanTest(BaseDatatypeTester):
    DATATYPE_CLS = Boolean

    TEST_DATA_VALID_VALUES = [
        (True, b"\x01"),
        (False, b"\x00")
    ]

    TEST_DATA_INVALID_SERIALIZATION_VALUES = [
        ("\x00", TypeError),
        ("\x01", TypeError),
        ("\x02", TypeError),
        (-1, TypeError),
        (0, TypeError),
        (1, TypeError),
        ("", TypeError),
        ("Test", TypeError)
    ]

    TEST_DATA_INVALID_DESERIALIZATION_VALUES = [
        (-1, TypeError),
        (0, TypeError),
        (1, TypeError),
        ("", TypeError),
        ("Test", TypeError),
        (True, TypeError),
        (False, TypeError)
    ]


class ByteTest(BaseDatatypeTester):
    DATATYPE_CLS = Byte

    TEST_DATA_VALID_VALUES = [
        (-128, b"\x80"),
        (-22, b"\xea"),
        (0, b"\x00"),
        (22, b"\x16"),
        (127, b"\x7f")
    ]

    TEST_DATA_INVALID_SERIALIZATION_VALUES = [
        (-500, ValueError),
        (128, ValueError),
        (1024, ValueError),

    ]

# def _bin(binstr):
#     """
#     Accepts a pretty looking string of binary numbers and
#     returns the binary number.

#     Parameters:
#         binstr - a string with this format: `'1010 0010 0100'`.

#     Returns:
#         Int
#     """
#     binstr = binstr.replace(" ", "")  # Remove all spaces.
#     num = int("0b" + binstr, 2)

#     return num


# class VarIntTests(unittest.TestCase):
#     def test1(self):
#         self.assertEqual(VarInt.deserialize(_bin("0000 0001")), 1)
#         self.assertEqual(VarInt.deserialize(_bin("1010 1100 0000 0010")), 300)
