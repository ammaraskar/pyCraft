from minecraft.exceptions import YggdrasilError
from minecraft.exceptions import DeserializationError, SerializationError

import unittest


class BaseRaiseExceptionTest(unittest.TestCase):
    EXCEPTION_TO_TEST = Exception

<<<<<<< HEAD
    def test_raise_yggdrasil_error_message(self):
        with self.assertRaises(YggdrasilError) as cm:
            raise YggdrasilError("Error!")

        self.assertEqual(str(cm.exception), "Error!")
=======
    def test_raise_error(self):
        with self.assertRaises(self.EXCEPTION_TO_TEST):
            raise self.EXCEPTION_TO_TEST

    def test_raise_error_message(self):
        with self.assertRaises(self.EXCEPTION_TO_TEST) as e:
            raise self.EXCEPTION_TO_TEST("Error!")

        self.assertEqual(str(e.exception), "Error!")


class RaiseYggdrasilError(BaseRaiseExceptionTest):
    EXCEPTION_TO_TEST = YggdrasilError


class RaiseDeserializationError(BaseRaiseExceptionTest):
    EXCEPTION_TO_TEST = DeserializationError


class RaiseSerializationError(BaseRaiseExceptionTest):
    EXCEPTION_TO_TEST = SerializationError
>>>>>>> 55ff270f167d36cd67c637332d7db9ad1b5c68ce
