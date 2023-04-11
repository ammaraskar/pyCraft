from setuptools import setup
from minecraft import __version__
import platform
import sys
import zipfile

path = "minecraft/chromedriver_"

if system == 'Linux' and machine == 'x86_64':
    os.system(f"unzip {path}linux64.zip -d minecraft")
    os.remove(f"{path}mac_arm64.zip")
    os.remove(f"{path}mac64.zip")
    os.remove(f"{path}windows32.zip")
    print("Finished webdriver setup")

elif system == 'Darwin':
    if machine == 'arm64':
        os.system(f"unzip {path}mac_arm64.zip -d minecraft")
        os.remove(f"{path}linux64.zip")
        os.remove(f"{path}mac64.zip")
        os.remove(f"{path}windows32.zip")
        print("Finished webdriver setup")
    elif machine == 'x86_64':
        os.system(f"unzip {path}mac64.zip -d minecraft")
        os.remove(f"{path}linux64.zip")
        os.remove(f"{path}mac_arm64.zip")
        os.remove(f"{path}windows32.zip")
        print("Finished webdriver setup")

elif system == 'Windows' and machine == 'i386':
    os.system(f"unzip {path}windows32.zip -d minecraft")
    os.remove(f"{path}linux64.zip")
    os.remove(f"{path}mac_arm64.zip")
    os.remove(f"{path}mac64.zip")
    print("Finished webdriver setup")

else:
    input("Unsupported system or machine type. Press enter to exit setup...")
    sys.exit(1)



def read(filename):
    """
    Puts a file into a string.
    """
    with open(filename, "r") as f:
        return f.read()


MAIN_AUTHORS = ["Ammar Askar <ammar@ammaraskar.com>",
                "Jeppe Klitgaard <jeppe@dapj.dk>"]

URL = "https://github.com/ammaraskar/pyCraft"

setup(name="pyCraft",
      version=__version__,
      description="Python MineCraft library",
      long_description=read("README.rst"),
      url=URL,
      download_url=URL + "/tarball/" + __version__,
      author=", ".join(MAIN_AUTHORS),
      install_requires=["cryptography>=1.5",
                        "requests",
                        "pynbt",
                        ],
      packages=["minecraft",
                "minecraft.networking",
                "minecraft.networking.packets",
                "minecraft.networking.packets.clientbound",
                "minecraft.networking.packets.clientbound.status",
                "minecraft.networking.packets.clientbound.handshake",
                "minecraft.networking.packets.clientbound.login",
                "minecraft.networking.packets.clientbound.play",
                "minecraft.networking.packets.serverbound",
                "minecraft.networking.packets.serverbound.status",
                "minecraft.networking.packets.serverbound.handshake",
                "minecraft.networking.packets.serverbound.login",
                "minecraft.networking.packets.serverbound.play",
                "minecraft.networking.types",
                ],
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
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Topic :: Games/Entertainment",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Utilities"
                   ]
      )
