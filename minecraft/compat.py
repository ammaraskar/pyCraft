"""
This module stores code used for making pyCraft compatible with
both Python2 and Python3 while using the same codebase.
"""

import six

# ### LONG ###
if six.PY3:
    long = int
else:
    long = long
