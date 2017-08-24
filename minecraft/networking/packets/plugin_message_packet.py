from .packet import Packet
from minecraft.networking.types import String, TrailingByteArray


class AbstractPluginMessagePacket(Packet):
    definition = [
        {'channel': String},
        {'data': TrailingByteArray}]
