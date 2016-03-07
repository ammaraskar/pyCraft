"""
This module stores code used for making pyCraft compatible with
both Python2 and Python3 while using the same codebase.
"""

# Raw input -> input shenangians
# example
# > from minecraft.compat import input
# > input("asd")

# Hi, I'm pylint, and sometimes I act silly, at which point my programmer
# overlords need to correct me.

# pylint: disable=undefined-variable,redefined-builtin,invalid-name
try:
    input = raw_input
except NameError:
    input = input

try:
    unicode = unicode
except NameError:
    unicode = str
# pylint: enable=undefined-variable,redefined-builtin,invalid-name
