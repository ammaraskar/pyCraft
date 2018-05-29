"""
Contains the `Exceptions` used by this library.
"""


class YggdrasilError(Exception):
    """
    Base `Exception` for the Yggdrasil authentication service.

    :param str message: A human-readable string representation of the error.
    :param int status_code: Initial value of :attr:`status_code`.
    :param str yggdrasil_error: Initial value of :attr:`yggdrasil_error`.
    :param str yggdrasil_message: Initial value of :attr:`yggdrasil_message`.
    :param str yggdrasil_cause: Initial value of :attr:`yggdrasil_cause`.
    """

    def __init__(
        self,
        message=None,
        status_code=None,
        yggdrasil_error=None,
        yggdrasil_message=None,
        yggdrasil_cause=None,
    ):
        super(YggdrasilError, self).__init__(message)
        self.status_code = status_code
        self.yggdrasil_error = yggdrasil_error
        self.yggdrasil_message = yggdrasil_message
        self.yggdrasil_cause = yggdrasil_cause

    status_code = None
    """`int` or `None`. The associated HTTP status code. May be set."""

    yggdrasil_error = None
    """`str` or `None`. The `"error"` field of the Yggdrasil response: a short
       description such as `"Method Not Allowed"` or
       `"ForbiddenOperationException"`. May be set.
    """

    yggdrasil_message = None
    """`str` or `None`. The `"errorMessage"` field of the Yggdrasil response:
       a longer description such as `"Invalid credentials. Invalid username or
       password."`. May be set.
    """

    yggdrasil_cause = None
    """`str` or `None`. The `"cause"` field of the Yggdrasil response: a string
       containing additional information about the error. May be set.
    """


class ConnectionFailure(Exception):
    """Raised by 'minecraft.networking.Connection' when a connection attempt
       fails.
    """


class VersionMismatch(ConnectionFailure):
    """Raised by 'minecraft.networking.Connection' when connection is not
       possible due to a difference between the server's and client's
       supported protocol versions.
    """


class LoginDisconnect(ConnectionFailure):
    """Raised by 'minecraft.networking.Connection' when a connection attempt
       is terminated by the server sending a Disconnect packet, during login,
       with an unknown message format.
    """


class InvalidState(ConnectionFailure):
    """Raised by 'minecraft.networking.Connection' when a connection attempt
       fails due to to the internal state of the Connection being unsuitable,
       for example if there is an existing ongoing connection.
    """


class IgnorePacket(Exception):
    """This exception may be raised from within a packet handler, such as
       `PacketReactor.react' or a packet listener added with
       `Connection.register_packet_listener', to stop any subsequent handlers
       from being called on that particular packet.
    """
