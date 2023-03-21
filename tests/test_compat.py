from minecraft import compat  # noqa unused-import

import unittest  # noqa unused-import


class TestCompatLong(unittest.TestCase):
    def test_import_long(self):
        from minecraft.compat import long  # noqa unused-import

    def test_long(self):
        compat.long(45)
