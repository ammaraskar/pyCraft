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


class VersionMismatch(Exception):
    pass
