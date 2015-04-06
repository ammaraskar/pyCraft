"""
This module stores code used for making pyCraft compatible with
both Python2 and Python3 while using the same codebase.
"""

# Raw input -> input shenangians
# example
# > from minecraft.compat import input
# > input("asd")
try:
    input = raw_input
except NameError:
    pass
