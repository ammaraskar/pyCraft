#!/usr/bin/env python
# flake8: noqa

import sys
import os
import os.path
from tox.config import parseconfig

# This file is in pyCraft/bin/; it needs to execute in pyCraft/.
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

print("language: python")
print("python: 3.5")
print("env:")
for env in parseconfig(None, 'tox').envlist:
    print("  - TOX_ENV=%s" % env)
print("install:")
print("  - pip install tox")
print("  - pip install python-coveralls")
print("script:")
print("  - tox -e $TOX_ENV")
print("after_script:")
print('  - if [ "$TOX_ENV" = "py35" ]; then tox -e coveralls; fi')
print("notifications:")
print("  email: false")
