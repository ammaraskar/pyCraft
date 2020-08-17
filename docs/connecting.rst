Connecting to Servers
======================

.. module:: minecraft.networking.connection

Your primary dealings when connecting to a server will be with the Connection class

.. autoclass:: Connection
	:members:

Writing Packets
~~~~~~~~~~~~~~~~~~~~

The packet class uses a lot of magic to work, here is how to use them.
Look up the particular packet you need to deal with, for this example
let's go with the ``serverbound.play.KeepAlivePacket``

.. autoclass:: minecraft.networking.packets.serverbound.play.KeepAlivePacket
	:undoc-members: 
	:inherited-members:
	:exclude-members: read, write, context, get_definition, get_id, id, packet_name, set_values

Pay close attention to the definition attribute, and how our class variable corresponds to
the name given from the definition::

	from minecraft.networking.packets import serverbound
	packet = serverbound.play.KeepAlivePacket()
	packet.keep_alive_id = random.randint(0, 5000)
	connection.write_packet(packet)

and just like that, the packet will be written out to the server.

It is possible to implement your own custom packets by subclassing
:class:`minecraft.networking.packets.Packet`. Read the docstrings and in
packets.py and follow the examples in its subpackages for more details on
how to do advanced tasks like having a packet that is compatible across
multiple protocol versions.

Listening for Certain Packets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's look at how to listen for certain packets, the relevant decorator being

A decorator can be used to register a packet listener:

.. autodecorator:: Connection.listener

Example usage::
    
    connection = Connection(options.address, options.port, auth_token=auth_token)
    connection.connect()
    
    from minecraft.networking.packets.clientbound.play import ChatMessagePacket
    
    @connection.listener(ChatMessagePacket)
    def print_chat(chat_packet):
        print "Position: " + str(chat_packet.position)
        print "Data: " + chat_packet.json_data


Altenatively, packet listeners can also be registered seperate from the function definition.

.. automethod:: Connection.register_packet_listener

An example of this can be found in the ``start.py`` headless client, it is recreated here::

    connection = Connection(options.address, options.port, auth_token=auth_token)
    connection.connect()

    def print_chat(chat_packet):
        print "Position: " + str(chat_packet.position)
        print "Data: " + chat_packet.json_data

    from minecraft.networking.packets.clientbound.play import ChatMessagePacket
    connection.register_packet_listener(print_chat, ChatMessagePacket)

The field names ``position`` and ``json_data`` are inferred by again looking at the definition attribute as before


.. autoclass:: minecraft.networking.packets.clientbound.play.ChatMessagePacket
	:undoc-members: 
	:inherited-members:
	:exclude-members: read, write, context, get_definition, get_id, id, packet_name, set_values
