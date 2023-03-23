from minecraft.networking.packets.serverbound.play import PlayerBlockPlacementPacket
from minecraft.networking.types import Position


def place_block(connection, x: int, y: int, z: int):
    packet = PlayerBlockPlacementPacket()
    packet.location = Position(x=x, y=y, z=z)
    packet.face = packet.Face.TOP   # See networking.types.BlockFace.
    packet.hand = packet.Hand.MAIN  # See networking.types.RelativeHand.
    packet.inside_block = False
    packet.x = 0.5
    packet.y = 0.5
    packet.z = 0.5
    connection.write_packet(packet)
