from .packet import Packet
from .packet_buffer import PacketBuffer
from .keep_alive_packet import KeepAlivePacket

# For backward compatibility, re-export any old names from before the change:

# Handshake State
# ==============
from .clientbound.handshake import get_packets as state_handshake_clientbound
from .serverbound.handshake import HandShakePacket
from .serverbound.handshake import get_packets as state_handshake_serverbound

# Status State
# ==============
from .clientbound.status import ResponsePacket
from .clientbound.status import PingResponsePacket as PingPacketResponse
from .clientbound.status import get_packets as state_status_clientbound
from .serverbound.status import RequestPacket
from .serverbound.status import PingPacket
from .serverbound.status import get_packets as state_status_serverbound

# Login State
# ==============
from .clientbound.login import DisconnectPacket
from .clientbound.login import EncryptionRequestPacket
from .clientbound.login import LoginSuccessPacket
from .clientbound.login import SetCompressionPacket
from .clientbound.login import get_packets as state_login_clientbound
from .serverbound.login import LoginStartPacket
from .serverbound.login import EncryptionResponsePacket
from .serverbound.login import get_packets as state_login_serverbound

# Playing State
# ==============
from .clientbound.play import KeepAlivePacket as KeepAlivePacketClientbound
from .serverbound.play import KeepAlivePacket as KeepAlivePacketServerbound
from .clientbound.play import JoinGamePacket
from .clientbound.play import ChatMessagePacket
from .clientbound.play import PlayerPositionAndLookPacket
from .clientbound.play import DisconnectPacket as DisconnectPacketPlayState
from .clientbound.play import (
    SetCompressionPacket as SetCompressionPacketPlayState
)
from .clientbound.play import PlayerListItemPacket
from .clientbound.play import MapPacket
from .clientbound.play import get_packets as state_playing_clientbound
from .serverbound.play import ChatPacket
from .serverbound.play import PositionAndLookPacket
from .serverbound.play import TeleportConfirmPacket
from .serverbound.play import AnimationPacket as AnimationPacketServerbound
from .serverbound.play import get_packets as state_playing_serverbound

__all_legacy_packets__ = [
           state_handshake_clientbound, HandShakePacket,
           state_handshake_serverbound, ResponsePacket,
           PingPacketResponse, state_status_clientbound,
           RequestPacket, PingPacket, state_status_serverbound,
           DisconnectPacket, EncryptionRequestPacket, LoginSuccessPacket,
           SetCompressionPacket, state_login_clientbound,
           LoginStartPacket, EncryptionResponsePacket,
           state_login_serverbound, KeepAlivePacketClientbound,
           KeepAlivePacketServerbound, JoinGamePacket, ChatMessagePacket,
           PlayerPositionAndLookPacket, DisconnectPacketPlayState,
           SetCompressionPacketPlayState, PlayerListItemPacket,
           MapPacket, state_playing_clientbound, ChatPacket,
           PositionAndLookPacket, TeleportConfirmPacket,
           AnimationPacketServerbound, state_playing_serverbound,
           Packet, PacketBuffer, KeepAlivePacket
                         ]


class PacketListener(object):
    def __init__(self, callback, *args):
        self.callback = callback
        self.packets_to_listen = []
        for arg in args:
            if issubclass(arg, Packet):
                self.packets_to_listen.append(arg)

    def call_packet(self, packet):
        for packet_type in self.packets_to_listen:
            if isinstance(packet, packet_type):
                self.callback(packet)
