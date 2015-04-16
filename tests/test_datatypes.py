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

    # VALID_VALUES should have the following format:
    # [(DESERIALIZED_VALUE, SERIALIZED_VALUE), ...]
    #
    # So that DESERIALIZED_VALUE is SERIALIZED_VALUE when serialized
    # and vice versa.

    VALID_VALUES = []

    # INVALID_SERIALIZATION_VALUES should be a list of tuples
    # containing the value and the expected exception.
    INVALID_SERIALIZATION_VALUES = []

    # INVALID_DESERIALIZATION_VALUES should be a list of tuples
    # containing the value and the expected exception.
    INVALID_DESERIALIZATION_VALUES = []

    def test_init(self):
        d = self.DATATYPE_CLS()  # noqa

    def test_init_with_arg(self):
        # We shouldn't accept any parameters.
        with self.assertRaises(TypeError):
            d = self.DATATYPE_CLS("This is a positional argument...")  # noqa

    def test_valid_data_serialization_values(self):
        for deserialized_val, serialized_val in self.VALID_VALUES:
            self.assertEqual(self.DATATYPE_CLS.serialize(deserialized_val),
                             serialized_val)

    def test_valid_data_deserialization_values(self):
        for deserialized_val, serialized_val in self.VALID_VALUES:
            self.assertEqual(self.DATATYPE_CLS.deserialize(serialized_val),
                             deserialized_val)

    def test_invalid_data_serialization_values(self):
        for value, exception in self.INVALID_SERIALIZATION_VALUES:
            with self.assertRaises(exception):
                self.DATATYPE_CLS.serialize(value)

    def test_invalid_data_deserialization_values(self):
        for value, exception in self.INVALID_DESERIALIZATION_VALUES:
            with self.assertRaises(exception):
                self.DATATYPE_CLS.deserialize(value)


class BaseNumberDatatypeTester(BaseDatatypeTester):
    BASE_NUMBER_INVALID_SERIALIZATION_VALUES = [
        ("", TypeError),
        ("Test", TypeError),
        (b"\x00", TypeError),
        (b"\x80", TypeError),
        (True, TypeError),
        (False, TypeError)
    ]

    def base_number_invalid_data_serialization_values(self):
        values_to_test = BASE_INVALID_SERIALIZATION_VALUES
        values_to_test.extend([
            (self.DATATYPE_CLS.MIN_NUMBER_VALUE - 1, ValueError),
            (self.DATATYPE_CLS.MAX_NUMBER_VALUE + 1, ValueError)
        ])

        for value, exception in values_to_test:
            with self.assertRaises(exception):
                self.DATATYPE_CLS.serialize(value)


class BaseStringDatatypeTester(BaseDatatypeTester):
    pass


BASE_INVALID_DESERIALIZATION_VALUES = [
    (-1, TypeError),
    (0, TypeError),
    (1, TypeError),
    ("", ValueError),
    (True, TypeError),
    (False, TypeError)
]


class DatatypeTest(BaseDatatypeTester):
    DATATYPE_CLS = Datatype


class NumberDatatypeTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = NumberDatatype


class StringDatatypeTest(BaseStringDatatypeTester):
    DATATYPE_CLS = StringDatatype


class BooleanTest(BaseDatatypeTester):
    DATATYPE_CLS = Boolean

    VALID_VALUES = [
        (True, b"\x01"),
        (False, b"\x00")
    ]

    INVALID_SERIALIZATION_VALUES = [
        ("\x00", TypeError),
        ("\x01", TypeError),
        ("\x02", TypeError),
        (-1, TypeError),
        (0, TypeError),
        (1, TypeError),
        ("", TypeError),
        ("Test", TypeError)
    ]

    # Use list(BASE_INVALID_DESERIALIZATION_VALUES) instead of
    # just = BASE_INVALID_DESERIALIZATION_VALUES, cause we want a COPY
    # of the list, NOT a reference (that we'll later extend!)
    INVALID_DESERIALIZATION_VALUES = list(BASE_INVALID_DESERIALIZATION_VALUES)
    INVALID_DESERIALIZATION_VALUES.extend([
        (b"\x00\x01", ValueError)
    ])


class ByteTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = Byte

    VALID_VALUES = [
        (-128, b"\x80"),
        (-22, b"\xea"),
        (0, b"\x00"),
        (22, b"\x16"),
        (127, b"\x7f")
    ]

    INVALID_DESERIALIZATION_VALUES = list(BASE_INVALID_DESERIALIZATION_VALUES)
    INVALID_DESERIALIZATION_VALUES.extend([
        (b"\x01\x20", ValueError),
    ])


class UnsignedByteTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = UnsignedByte

    VALID_VALUES = [
        (0, b"\x00"),
        (127, b"\x7f"),
        (255, b"\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = ByteTest.INVALID_DESERIALIZATION_VALUES


class ShortTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = Short

    VALID_VALUES = [
        (-32768, b"\x80\x00"),
        (-10000, b"\xd8\xf0"),
        (0, b"\x00\x00"),
        (5000, b"\x13\x88"),
        (32767, b"\x7f\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = list(BASE_INVALID_DESERIALIZATION_VALUES)
    INVALID_DESERIALIZATION_VALUES.extend([
        (b"\xff", ValueError),
        (b"\xff\x01\x6e", ValueError)
    ])


class UnsignedShortTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = UnsignedShort

    VALID_VALUES = [
        (0, b"\x00\x00"),
        (10000, b"'\x10"),
        (32767, b"\x7f\xff"),
        (65535, b"\xff\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = ShortTest.INVALID_DESERIALIZATION_VALUES


class IntegerTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = Integer

    VALID_VALUES = [
        (-2147483648, b"\x80\x00\x00\x00"),
        (-1000000, b"\xff\xf0\xbd\xc0"),
        (0, b"\x00\x00\x00\x00"),
        (10000000, b"\x00\x98\x96\x80"),
        (2147483647, b"\x7f\xff\xff\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = list(BASE_INVALID_DESERIALIZATION_VALUES)
    INVALID_DESERIALIZATION_VALUES.extend([
        (b"\xff", ValueError),
        (b"\x00\x01", ValueError),
        (b"\x76\x80\x80\x10\xff", ValueError)
    ])


class UnsignedIntegerTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = UnsignedInteger

    VALID_VALUES = [
        (0, b"\x00\x00\x00\x00"),
        (10000000, b"\x00\x98\x96\x80"),
        (2147483647, b"\x7f\xff\xff\xff"),
        (4294967295, b"\xff\xff\xff\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = IntegerTest.INVALID_DESERIALIZATION_VALUES


class LongTest(IntegerTest):
    DATATYPE_CLS = Long


class UnsignedLongTest(UnsignedInteger):
    DATATYPE_CLS = UnsignedLong


class LongLongTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = LongLong

    VALID_VALUES = [
        (-9223372036854775808, b"\x80\x00\x00\x00\x00\x00\x00\x00"),
        (-1000000, b"\xff\xff\xff\xff\xff\xf0\xbd\xc0"),
        (0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        (10000000, b"\x00\x00\x00\x00\x00\x98\x96\x80"),
        (9223372036854775807, b"\x7f\xff\xff\xff\xff\xff\xff\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = list(BASE_INVALID_DESERIALIZATION_VALUES)
    INVALID_DESERIALIZATION_VALUES.extend([
        (b"\xff", ValueError),
        (b"\x00\x01", ValueError),
        (b"\x76\x80\x80\x10\xff", ValueError),
        (b"\x55\x44\x33\x22\x11\x66\x77\x88\x99", ValueError)
    ])


class UnsignedLongLongTest(BaseNumberDatatypeTester):
    DATATYPE_CLS = UnsignedLongLong

    VALID_VALUES = [
        (0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        (10000000, b"\x00\x00\x00\x00\x00\x98\x96\x80"),
        (9223372036854775807, b"\x7f\xff\xff\xff\xff\xff\xff\xff"),
        (18446744073709551615, b"\xff\xff\xff\xff\xff\xff\xff\xff")
    ]

    INVALID_DESERIALIZATION_VALUES = \
        LongLongTest.INVALID_DESERIALIZATION_VALUES


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
