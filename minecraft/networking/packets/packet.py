from .packet_buffer import PacketBuffer
from zlib import compress
from minecraft.networking.types import (
    VarInt
)


class Packet(object):
    packet_name = "base"
    id = None
    definition = None

    # To define the packet ID, either:
    #  1. Define the attribute `id', of type int, in a subclass; or
    #  2. Override `get_id' in a subclass and return the correct packet ID
    #     for the given ConnectionContext. This is necessary if the packet ID
    #     has changed across protocol versions, for example.
    @classmethod
    def get_id(cls, context):
        return cls.id

    # To define the network data layout of a packet, either:
    #  1. Define the attribute `definition', a list of fields, each of which
    #     is a dict mapping attribute names to data types; or
    #  2. Override `get_definition' in a subclass and return the correct
    #     definition for the given ConnectionContext. This may be necessary
    #     if the layout has changed across protocol versions, for example; or
    #  3. Override the methods `read' and/or `write' in a subclass. This may be
    #     necessary if the packet layout cannot be described as a list of
    #     fields.
    @classmethod
    def get_definition(cls, context):
        return cls.definition

    def __init__(self, context=None, **kwargs):
        self.context = context
        self.set_values(**kwargs)

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, _context):
        self._context = _context
        self._context_changed()

    def _context_changed(self):
        if self._context is not None:
            self.id = self.get_id(self._context)
            self.definition = self.get_definition(self._context)
        else:
            self.id = None
            self.definition = None

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def read(self, file_object):
        for field in self.definition:
            for var_name, data_type in field.items():
                value = data_type.read(file_object)
                setattr(self, var_name, value)

    # Writes a packet buffer to the socket with the appropriate headers
    # and compressing the data if necessary
    def _write_buffer(self, socket, packet_buffer, compression_threshold):
        # compression_threshold of None means compression is disabled
        if compression_threshold is not None:
            if len(packet_buffer.get_writable()) > compression_threshold != -1:
                # compress the current payload
                packet_data = packet_buffer.get_writable()
                compressed_data = compress(packet_data)
                packet_buffer.reset()
                # write out the length of the uncompressed payload
                VarInt.send(len(packet_data), packet_buffer)
                # write the compressed payload itself
                packet_buffer.send(compressed_data)
            else:
                # write out a 0 to indicate uncompressed data
                packet_data = packet_buffer.get_writable()
                packet_buffer.reset()
                VarInt.send(0, packet_buffer)
                packet_buffer.send(packet_data)

        VarInt.send(len(packet_buffer.get_writable()), socket)  # Packet Size
        socket.send(packet_buffer.get_writable())  # Packet Payload

    def write(self, socket, compression_threshold=None):
        # buffer the data since we need to know the length of each packet's
        # payload
        packet_buffer = PacketBuffer()
        # write packet's id right off the bat in the header
        VarInt.send(self.id, packet_buffer)
        # write every individual field
        for field in self.definition:
            for var_name, data_type in field.items():
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        self._write_buffer(socket, packet_buffer, compression_threshold)

    def __str__(self):
        str = type(self).__name__
        if self.id is not None:
            str = '0x%02X %s' % (self.id, str)
        if self.definition is not None:
            fields = {a: getattr(self, a) for d in self.definition for a in d}
            str = '%s %s' % (str, fields)
        return str
