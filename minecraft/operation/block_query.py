from minecraft.networking.connection import Connection
from minecraft.networking.packets.serverbound.play import QueryBlockNBTPacket
from minecraft.networking.types import Position


def query_block(connection: Connection, location: list[3], transaction_id):
    block_packet = QueryBlockNBTPacket()
    block_packet.transaction_id = transaction_id
    block_packet.location = Position(x=int(location[0]), y=int(location[1]), z=int(location[2]))
    connection.write_packet(block_packet, force=True)
