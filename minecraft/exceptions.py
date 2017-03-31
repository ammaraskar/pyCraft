"""
Contains the `Exceptions` used by this library.
"""


class YggdrasilError(Exception):
    """
    Base `Exception` for the Yggdrasil authentication service.
    """
    def __init__(
        self,
        message=None,
        status_code=None,
        yggdrasil_error=None,
        yggdrasil_message=None,
        yggdrasil_cause=None,
        *args
    ):
        if message is not None:
            args = (message,) + args
        super(YggdrasilError, self).__init__(*args)

        self.status_code = status_code
        self.yggdrasil_error = yggdrasil_error
        self.yggdrasil_message = yggdrasil_message
        self.yggdrasil_cause = yggdrasil_cause


class VersionMismatch(Exception):
    pass
