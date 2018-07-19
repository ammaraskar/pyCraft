from .packet import Packet
from minecraft.networking.types import String, TrailingByteArray


class AbstractPluginMessagePacket(Packet):
    """NOTE: Plugin channels were significantly changed, including changing the
       names of channels, between Minecraft 1.12 and 1.13 - see <http://wiki.vg
       /index.php?title=Pre-release_protocol&oldid=14132#Plugin_Channels>.
    """
    definition = [
        {'channel': String},
        {'data': TrailingByteArray}]
