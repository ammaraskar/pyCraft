"""
A modern, Python3-compatible, well-documented library for communicating
with a MineCraft server.
"""

__version__ = "0.2.0"

SUPPORTED_MINECRAFT_VERSIONS = {
    '1.8':      47,
    '1.8.1':    47,
    '1.8.2':    47,
    '1.8.3':    47,
    '1.8.4':    47,
    '1.8.5':    47,
    '1.8.6':    47,
    '1.8.7':    47,
    '1.8.8':    47,
    '1.9':      107,
    '1.9.1':    108,
    '1.9.2':    109,
    '1.9.3':    110,
    '1.9.4':    110,
    '1.10':     210,
    '16w32a':   301,
}

SUPPORTED_PROTOCOL_VERSIONS = sorted(SUPPORTED_MINECRAFT_VERSIONS.values())
