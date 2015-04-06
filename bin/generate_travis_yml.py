import os
os.chdir("..")

from tox._config import parseconfig

print("language: python")
print("python: 2.7")
print("env:")
for env in parseconfig(None, 'tox').envlist:
    print("  - TOX_ENV=%s" % env)
print("install:")
print("  - pip install tox")
print("  - pip install python-coveralls")
print("script:")
print("  - tox -e $TOX_ENV")
print("after_success:")
print('  - if [ "$TOX_ENV" = "coveralls" ]; then coveralls; fi')
print("notifications:")
print("  email: false")
