from distutils.core import setup
from minecraft import __version__

MAIN_AUTHORS = ["Ammar Askar <ammar@ammaraskar.com>",
                "Jeppe Klitgaard <jeppe@dapj.dk>"]

setup(name="minecraft",
      version=__version__,
      description="Python MineCraft library",
      author=", ".join(MAIN_AUTHORS),
      packages=["minecraft"]
      )
