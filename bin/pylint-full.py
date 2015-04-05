DOCSTR = """
Runs a full pylint inspection.

If evaluation score is under the min-eval variable,
this program will exit with exit code 1.
"""

__doc__ = DOCSTR

from sh import pylint
from sh import ErrorReturnCode
import sys
import re
import argparse

parser = argparse.ArgumentParser(DOCSTR)

parser.add_argument("--min-eval", dest="min_eval", type=float, default=10.00,
                    help="The minimum allowed global evaluation score."
                         "If the score is lower than this number,"
                         "the program will exit with exit code 1.")

args = parser.parse_args()

PYLINT_ARGS = ("minecraft", "--disable=E")

try:
    output = pylint(*PYLINT_ARGS)
except ErrorReturnCode as e:
    output = e.stdout
output = output.decode()

global_eval_pattern = re.compile(r"Global evaluation\n-----------------\n"
                                 r"Your code has been rated at (\d*\.\d+)/10")

match = global_eval_pattern.search(output)
evaluation = float(match.group(1))

print(output)  # We want to appear as if we're pylint

if evaluation < args.min_eval:
    print("ERROR: Evaluation score must be over {}".format(str(args.min_eval)))
    sys.exit(1)
else:
    sys.exit(0)
