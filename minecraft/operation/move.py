from minecraft.networking.connection import Connection
from minecraft.networking.packets.serverbound.play import PositionAndLookPacket


def calculate_distance(start, end):
    ans = 0
    for i in range(3):
        ans += (start[i] - float(end[i])) * (start[i] - float(end[i]))
    return ans, [float(end[i]) - start[i] for i in range(3)]


def player_move(connection: Connection, destination, rotation):
    pos_packet = PositionAndLookPacket()
    pos_packet.x = float(destination[0])
    pos_packet.feet_y = float(destination[1])
    pos_packet.z = float(destination[2])
    pos_packet.yaw = rotation[0]
    pos_packet.pitch = rotation[1]
    pos_packet.on_ground = True
    connection.write_packet(pos_packet, force=True)
