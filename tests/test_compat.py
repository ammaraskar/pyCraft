from minecraft import compat  # noqa unused-import

import unittest


class TestCompatInput(unittest.TestCase):
    def test_import_input(self):
        from minecraft.compat import input  # noqa unused-import
