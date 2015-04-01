import platform
from distutils.version import StrictVersion

if StrictVersion(platform.python_version()) < StrictVersion("3.3.0"):
    import mock  # noqa
else:
    from unittest import mock  # noqa
