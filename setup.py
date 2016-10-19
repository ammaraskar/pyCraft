from distutils.core import setup
from minecraft import __version__


def read(filename):
    """
    Puts a file into a string.
    """
    with open(filename, "r") as f:
        return f.read()

MAIN_AUTHORS = ["Ammar Askar <ammar@ammaraskar.com>",
                "Jeppe Klitgaard <jeppe@dapj.dk>"]

URL = "https://github.com/ammaraskar/pyCraft"

setup(name="minecraft",
      version=__version__,
      description="Python MineCraft library",
      long_description=read("README.rst"),
      url=URL,
      download_url=URL + "/tarball/" + __version__,
      author=", ".join(MAIN_AUTHORS),
      packages=["minecraft", "minecraft.networking"],
      keywords=["MineCraft", "networking", "pyCraft", "minecraftdev", "mc"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache Software License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Topic :: Games/Entertainment",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Utilities"
                   ]
      )
