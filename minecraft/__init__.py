"""
A modern, Python3-compatible, well-documented library for communicating
with a MineCraft server.
"""

__version__ = "0.3.0"

SUPPORTED_MINECRAFT_VERSIONS = {
    '1.8':       47,
    '1.8.1':     47,
    '1.8.2':     47,
    '1.8.3':     47,
    '1.8.4':     47,
    '1.8.5':     47,
    '1.8.6':     47,
    '1.8.7':     47,
    '1.8.8':     47,
    '1.9':       107,
    '1.9.1':     108,
    '1.9.2':     109,
    '1.9.3':     110,
    '1.9.4':     110,
    '1.10':      210,
    '1.10.1':    210,
    '1.10.2':    210,
    '16w32a':    301,
    '16w32b':    302,
    '16w33a':    303,
    '16w35a':    304,
    '16w36a':    305,
    '16w38a':    306,
    '16w39a':    307,
    '16w39b':    308,
    '16w39c':    309,
    '16w40a':    310,
    '16w41a':    311,
    '16w42a':    312,
    '16w43a':    313,
    '16w44a':    313,
    '1.11-pre1': 314,
    '1.11':      315,
    '16w50a':    316,
}

SUPPORTED_PROTOCOL_VERSIONS = sorted(SUPPORTED_MINECRAFT_VERSIONS.values())
