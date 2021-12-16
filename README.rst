pyCraft
=======
.. image:: https://app.travis-ci.com/ammaraskar/pyCraft.svg?branch=master 
    :target: https://app.travis-ci.com/github/ammaraskar/pyCraft 
.. image:: https://readthedocs.org/projects/pycraft/badge/?version=latest
    :target: https://pycraft.readthedocs.org/en/latest
.. image:: https://coveralls.io/repos/ammaraskar/pyCraft/badge.svg?branch=master 
    :target: https://coveralls.io/r/ammaraskar/pyCraft?branch=master


Minecraft Python Client Library!

This projects aims to be a modern, Python3-compatible, well-documented library for
communication with a MineCraft server.

Detailed information for developers can be found here:
`<http://pycraft.readthedocs.org/en/latest/>`_.

``start.py`` is a basic example of a headless client using the library
Use ``start.py --help`` for the options.

Supported Minecraft versions
----------------------------
pyCraft is compatible with the following Minecraft releases:

* 1.8, 1.8.1, 1.8.2, 1.8.3, 1.8.4, 1.8.5, 1.8.6, 1.8.7, 1.8.8, 1.8.9
* 1.9, 1.9.1, 1.9.2, 1.9.3, 1.9.4
* 1.10, 1.10.1, 1.10.2
* 1.11, 1.11.1, 1.11.2
* 1.12, 1.12.1, 1.12.2
* 1.13, 1.13.1, 1.13.2
* 1.14, 1.14.1, 1.14.2, 1.14.3, 1.14.4
* 1.15, 1.15.1, 1.15.2
* 1.16, 1.16.1, 1.16.2, 1.16.3, 1.16.4, 1.16.5
* 1.17, 1.17.1
* 1.18, 1.18.1

In addition, some development snapshots and pre-release versions are supported:
`<minecraft/__init__.py>`_ contains a full list of supported Minecraft versions
and corresponding protocol version numbers.

Supported functionality
-----------------------
Although pyCraft is compatible any supported server, only a subset of all
packets are currently decoded or encoded by the library: those necessary
to remain connected to the server, those used for chat, and some others.

Developers wishing to use other functionality with pyCraft can contribute by
implementing packet classes for the desired packets, adding them under
`<minecraft/networking/packets>`_, and sending a pull request.

Supported Python versions
-------------------------
pyCraft is compatible with (at least) the following Python implementations:

* Python 3.5
* Python 3.6
* Python 3.7
* Python 3.8
* Python 3.9
* PyPy

Requirements
------------
- `cryptography <https://github.com/pyca/cryptography#cryptography>`_
- `requests <http://docs.python-requests.org/en/latest/>`_
- `PyNBT <https://github.com/TkTech/PyNBT>`_

The requirements are also stored in ``setup.py``

See the installation instructions for the cryptography library here: `<https://cryptography.io/en/latest/installation/>`_
but essentially ``pip install -r requirements.txt`` should cover everything.

Contact
-------
This project currently has 2 main developers, *Ammar Askar* and *Jeppe Klitgaard*.

GitHub
^^^^^^
The preferred method of communication is via this GitHub page.

Mail
^^^^
We can be contacted by mail:

* Ammar Askar `ammar@ammaraskar.com <mailto:ammar@ammaraskar.com>`_
* Jeppe Klitgaard `jeppe@dapj.dk <mailto:jeppe@dapj.dk>`_

IRC
^^^
We can often be found on the ``minecraftdev`` IRC on
`irc.esper.net <https://www.esper.net/>`_

We go by the names of ``ammar2`` and ``dkkline``.
