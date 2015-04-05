import subprocess
import sys

EXPECTED_OUTPUT = "lists of files in version control and sdist match"


def check_manifest():
    """
    Returns a tuple containing ``(output, status)``.

    Status is:
        ``True`` if ``output`` was as expected (no errors),
        ``False`` otherwise.
    """
    output = subprocess.check_output(["check-manifest"]).decode()
    if EXPECTED_OUTPUT == output.strip():
        status = True
    else:
        status = False

    return (output, status)

if __name__ == '__main__':
    output, verified = check_manifest()

    if not verified:
        print("Check-manifest didn't match.")
        print("OUTPUT: {}".format(output))
        print("EXPECTED_OUTPUT: {}".format(EXPECTED_OUTPUT))
        sys.exit(1)

    else:
        print("Manifest verified.")
        sys.exit(0)
