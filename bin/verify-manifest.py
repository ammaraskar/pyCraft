import os, subprocess
import errno, sys

EXPECTED_OUTPUT = "lists of files in version control and sdist match"


def check_manifest():
	os.chdir('..')
	output = subprocess.check_output(["check-manifest"]).decode()
	print(output)
	if EXPECTED_OUTPUT == output.strip():
		return 1
	else:
		sys.exit(2)

if __name__ == '__main__':
	check_manifest()