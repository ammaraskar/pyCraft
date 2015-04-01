from distutils.version import StrictVersion as SV
import unittest

import minecraft


class VersionTest(unittest.TestCase):
    def test_module_version_is_a_valid_pep_386_strict_version(self):
        SV(minecraft.__version__)

    def test_minecraft_version_is_a_valid_pep_386_strict_version(self):
        SV(minecraft.MINECRAFT_VERSION)

    def test_protocol_version_is_an_int(self):
        self.assertTrue(type(minecraft.PROTOCOL_VERSION) is int)
