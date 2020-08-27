Example Implementations
=======================

.. currentmodule:: examples.Player
.. _Players: https://github.com/ammaraskar/pyCraft/blob/master/examples/Player.py
.. _Start: https://github.com/ammaraskar/pyCraft/blob/master/examples/start.py

Both of these examples can be used to show how to go about initiating a simple
connection to a server using `pyCraft`.

`Note: These implementations expect to be running in the root directory of this project.
That being one directory higher then they are on the GitHub repo.`

Basic Headless Client
~~~~~~~~~~~~~~~~~~~~~~

Use `python start.py --help` for the available options.

.. automodule:: examples.start
    :members:

See the Start_ file for the implementation


Simple Player Class
~~~~~~~~~~~~~~~~~~~~

This implements all the required functionality to connect and maintain a connection
to a given server. This also handles the parsing of chat and then prints it to the screen.

.. automodule:: examples.Player
   :members:

See the Players_ file for the implementation