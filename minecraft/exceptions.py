"""
Contains the `Exceptions` used by this library.
"""


class YggdrasilError(Exception):
    """
    Base ``Exception`` for the Yggdrasil authentication service.
    """


class DeserializationError(Exception):
    """
    ``Exception`` raised when something went wrong during the deserialization
    process.
    """


class SerializationError(Exception):
    """
    ``Exception`` raised when something went wrong during the serialization
    process.
    """
