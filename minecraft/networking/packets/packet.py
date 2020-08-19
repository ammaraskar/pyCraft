from zlib import compress

from .packet_buffer import PacketBuffer
from minecraft.networking.types import (
    VarInt, Enum, overridable_property,
)


class Packet(object):
    packet_name = "base"

    # To define the packet ID, either:
    #  1. Define the attribute `id', of type int, in a subclass; or
    #  2. Override `get_id' in a subclass and return the correct packet ID
    #     for the given ConnectionContext. This is necessary if the packet ID
    #     has changed across protocol versions, for example; or
    #  3. Define the attribute `id' in an instance of a class without either
    #     of the above.
    @classmethod
    def get_id(cls, _context):
        return getattr(cls, 'id')

    @overridable_property
    def id(self):
        return None if self.context is None else self.get_id(self.context)

    # To define the network data layout of a packet, either:
    #  1. Define the attribute `definition', a list of fields, each of which
    #     is a dict mapping attribute names to data types; or
    #  2. Override `get_definition' in a subclass and return the correct
    #     definition for the given ConnectionContext. This may be necessary
    #     if the layout has changed across protocol versions, for example; or
    #  3. Override the methods `read' and/or `write_fields' in a subclass.
    #     This may be necessary if the packet layout cannot be described as a
    #     simple list of fields.
    @classmethod
    def get_definition(cls, _context):
        return getattr(cls, 'definition')

    @overridable_property
    def definition(self):
        return None if self.context is None else \
               self.get_definition(self.context)

    # In general, a packet instance must have its 'context' attribute set to an
    # instance of 'ConnectionContext', for example to decide on version-
    # dependent behaviour. This can either be given as an argument to this
    # constructor (e.g. 'p = P(context=c)') or set later
    # (e.g. 'p.context = c').
    #
    # While a packet has no 'context' set, all attributes should *writable*
    # without errors, but some attributes may not be *readable*.
    #
    # When sending or receiving packets via 'Connection', it is generally not
    # necessary to set the 'context', as this will be done automatically by
    # 'Connection'.
    def __init__(self, context=None, **kwargs):
        self.context = context
        self.set_values(**kwargs)

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def read(self, file_object):
        for field in self.definition:  # pylint: disable=not-an-iterable
            for var_name, data_type in field.items():
                value = data_type.read_with_context(file_object, self.context)
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
        self.write_fields(packet_buffer)
        self._write_buffer(socket, packet_buffer, compression_threshold)

    def write_fields(self, packet_buffer):
        # Write the fields comprising the body of the packet (excluding the
        # length, packet ID, compression and encryption) into a PacketBuffer.
        for field in self.definition:  # pylint: disable=not-an-iterable
            for var_name, data_type in field.items():
                data = getattr(self, var_name)
                data_type.send_with_context(data, packet_buffer, self.context)

    def __repr__(self):
        str = type(self).__name__
        if self.id is not None:
            str = '0x%02X %s' % (self.id, str)
        fields = self.fields
        if fields is not None:
            inner_str = ', '.join('%s=%s' % (a, self.field_string(a))
                                  for a in fields if hasattr(self, a))
            str = '%s(%s)' % (str, inner_str)
        return str

    @property
    def fields(self):
        """ An iterable of the names of the packet's fields, or None. """
        if self.definition is None:
            return None
        # pylint: disable=not-an-iterable
        return (field for defn in self.definition for field in defn)

    def field_string(self, field):
        """ The string representation of the value of a the given named field
            of this packet. Override to customise field value representation.
        """
        value = getattr(self, field, None)

        enum_class = self.field_enum(field, self.context)
        if enum_class is not None:
            name = enum_class.name_from_value(value)
            if name is not None:
                return name

        return repr(value)

    @classmethod
    def field_enum(cls, field, context=None):
        """ The subclass of 'minecraft.networking.types.Enum' associated with
            this field, or None if there is no such class.
        """
        enum_name = ''.join(s.capitalize() for s in field.split('_'))
        if hasattr(cls, enum_name):
            enum_class = getattr(cls, enum_name)
            if isinstance(enum_class, type) and issubclass(enum_class, Enum):
                return enum_class
