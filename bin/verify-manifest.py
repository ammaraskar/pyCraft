"""
Exits with exit code 0 if manifest was verified.
"""

from sh import check_manifest
from sh import ErrorReturnCode_1
import sys

EXPECTED_OUTPUT = "lists of files in version control and sdist match"


def verify_manifest():
    """
    Returns a ``str`` containing output from ``check-manifest``.
    """
    try:
        output = check_manifest().decode()
    except ErrorReturnCode_1 as e:
        output = e.stderr.decode() + e.stdout.decode()

    return output

if __name__ == '__main__':
    output = verify_manifest()

    print(output)

    if output == EXPECTED_OUTPUT:
        sys.exit(0)

    else:
        sys.exit(1)
