from minecraft.exceptions import YggdrasilError
from minecraft.exceptions import DeserializationError, SerializationError

import unittest


class RaiseYggdrasilError(unittest.TestCase):
    def test_raise_yggdrasil_error(self):
        with self.assertRaises(YggdrasilError):
            raise YggdrasilError

    def test_raise_yggdrasil_error_message(self):
        with self.assertRaises(YggdrasilError) as e:
            raise YggdrasilError("Error!")

        self.assertEqual(str(e.exception), "Error!")


class RaiseDeserializationError(unittest.TestCase):
    def test_raise_deserialization_error(self):
        with self.assertRaises(DeserializationError):
            raise DeserializationError

    def test_raise_deserialization_error_message(self):
        with self.assertRaises(DeserializationError) as e:
            raise DeserializationError("Error!")

        self.assertEqual(str(e.exception), "Error!")


class RaiseSerializationError(unittest.TestCase):
    def test_raise_serialization_error(self):
        with self.assertRaises(SerializationError):
            raise SerializationError

    def test_raise_serialization_error_message(self):
        with self.assertRaises(SerializationError) as e:
            raise SerializationError("Error!")

        self.assertEqual(str(e.exception), "Error!")
