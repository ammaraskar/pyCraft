from minecraft.networking.packets.serverbound.play import ChatPacket


def send_message(connection, message):
    message_packet = ChatPacket()
    message_packet.message = message
    connection.write_packet(message_packet, force=True)
