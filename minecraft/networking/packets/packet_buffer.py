from io import BytesIO


class PacketBuffer(object):
    def __init__(self):
        self.bytes = BytesIO()

    def send(self, value):
        """
        Writes the given bytes to the buffer, designed to emulate socket.send
        :param value: The bytes to write
        """
        self.bytes.write(value)

    def read(self, length=None):
        return self.bytes.read(length)

    def recv(self, length=None):
        return self.read(length)

    def reset(self):
        self.bytes = BytesIO()

    def reset_cursor(self):
        self.bytes.seek(0)

    def get_writable(self):
        return self.bytes.getvalue()
