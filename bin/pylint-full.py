DOCSTR = """
Runs a full pylint inspection.

If evaluation score is under the min-eval variable,
this program will exit with exit code 1.
"""

__doc__ = DOCSTR

import subprocess
import os
import sys
import re
import argparse

os.chdir("..")  # leave bin/

parser = argparse.ArgumentParser(DOCSTR)

parser.add_argument("--min-eval", dest="min_eval", type=float, default=10.00,
                    help="The minimum allowed global evaluation score."
                         "If the score is lower than this number,"
                         "the program will exit with exit code 1.")

args = parser.parse_args()

PYLINT = ("pylint", "minecraft", "--disable=E")
EVAL_PATTERN = (r"Global evaluation\n-----------------\n"
                r"Your code has been rated at (\d*\.\d+)/10")


def get_evaluation_score_and_output():
    """
    Returns a tuple containing ``(output, eval_score)`` where:
        ``output`` is a ``str`` with the pylint output.
        ``eval_score`` is a ``float`` with the pylint evaluation score
    """
    try:
        output = subprocess.check_output(PYLINT)
    except subprocess.CalledProcessError as e:
        output = e.output
    output = output.decode()

    global_eval_pattern = re.compile(EVAL_PATTERN)

    match = global_eval_pattern.search(output)

    evaluation = float(match.group(1))

    return (output, evaluation)

output, evaluation = get_evaluation_score_and_output()
print(output)  # We want to appear as if we're pylint

if evaluation < args.min_eval:
    print("ERROR: Evaluation score must be over {}".format(str(args.min_eval)))
    sys.exit(1)
else:
    sys.exit(0)
