Connecting to Servers
======================

.. module:: network.connection

Your primary dealings when connecting to a server will deal with the Connection class

.. autoclass:: network.connection.Connection
	:members:

Writing Packets
~~~~~~~~~~~~~~~~~~~~

The packet class uses a lot of magic to work, here is how to use them.
Look up the particular packet you need to deal with, for my example let's go with the ``KeepAlivePacket``

.. autoclass:: network.packets.KeepAlivePacket
	:undoc-members: 
	:inherited-members:
	:exclude-members: read, write

Pay close attention to the definition attribute, we're gonna be using that to assign values within the packet::

	packet = KeepAlivePacket()
	packet.keep_alive_id = random.randint(0, 5000)
	connection.write_packet(packet)

and just like that, the packet will be written out to the server

Listening for Certain Packets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's look at how to listen for certain packets, the relevant method being

.. automethod:: network.connection.Connection.register_packet_listener

An example of this can be found in the ``start.py`` headless client, it is recreated here::

    connection = Connection(address, port, login_response)
    connection.connect()

    def print_chat(chat_packet):
        print "Position: " + str(chat_packet.position)
        print "Data: " + chat_packet.json_data

    from network.packets import ChatMessagePacket
    connection.register_packet_listener(print_chat, ChatMessagePacket)

The field names ``position`` and ``json_data`` are inferred by again looking at the definition attribute as before

.. autoclass:: network.packets.ChatMessagePacket
	:undoc-members: 
	:inherited-members:
	:exclude-members: read, write