Connecting to Servers
======================

.. currentmodule:: network.connection

Your primary dealings when connecting to a server will deal with the Connection class

.. automodule:: network.connection
	:members:

Dealing wih packets
~~~~~~~~~~~~~~~~~~~~

The packet class uses a lot of magic to work, here is how to use them.
Look up the particular packet you need to deal with, for my example let's go with the ``KeepAlivePacket``

.. autoclass:: network.packets.KeepAlivePacket
	:undoc-members:
	:inherited-members:

Pay close attention to the definition attribute, we're gonna be using that to assign values within the packet::

	packet = KeepAlivePacket()
	packet.keep_alive_id = random.randint(0, 5000)
	connection.write_packet(packet)

and just like that, the packet will be written out to the server