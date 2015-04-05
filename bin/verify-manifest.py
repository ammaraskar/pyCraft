"""
Exits with exit code 0 if manifest was verified.
"""
import sys
import subprocess
import errno
import os

EXPECTED_OUTPUT = "lists of files in version control and sdist match"
os.chdir("..")  # Leave bin/

def verify_manifest():
    """
    Returns a ``str`` containing output from ``check-manifest``.
    """
    try:
        output = subprocess.check_output("check-manifest",
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output

    return output.decode().strip()

if __name__ == '__main__':
    output = verify_manifest()
    print(output)

    if output == EXPECTED_OUTPUT:
        sys.exit(0)

    else:
        sys.exit(1)
