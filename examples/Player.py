import re
import time
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import serverbound, clientbound

from .Parsers import DefaultParser


class Player:
    """
    A class built to handle all required actions to maintain:
     - Gaining auth tokens, and connecting to online minecraft servers.
     - Clientbound chat
     - Serverbound chat

    Warnings
    --------
    This class explicitly expects a username & password, then expects to
    be able to connect to a server in online mode.
    If you wish to add different functionality please view the example
    headless client, `start.py`, for how to implement it.
    """

    def __init__(self, username, password, *, admins=None):
        """
        Init handles the following:
         - Client Authentication
         - Setting the current connection state
         - Setting the recognized 'admins' for this instance

        Parameters
        ----------
        username : String
            Used for authentication
        password : String
            Used for authentication
        admins : list, optional
            The minecraft accounts to auto accept tpa's requests from

        Raises
        ------
        YggdrasilError
            Username or Password was incorrect

        """
        self.kickout = False
        self.admins = [] if admins is None else admins

        self.auth_token = authentication.AuthenticationToken()
        self.auth_token.authenticate(username, password)

    def Parser(self, data):
        """
        Converts the chat packet received from the server
        into human readable strings

        Parameters
        ----------
        data : JSON
            The chat data json receive from the server

        Returns
        -------
        message : String
            The text received from the server in human readable form

        """
        message = DefaultParser(
            data)  # This is where you would call other parsers

        if not message:
            return False

        if "teleport" in message.lower():
            self.HandleTpa(message)

        return message

    def HandleTpa(self, message):
        """
        Using the given message, figure out whether or not to accept the tpa

        Parameters
        ----------
        message : String
            The current chat, where 'tpa' was found in message.lower()

        """
        try:
            found = re.search(
                "(.+?) has requested that you teleport to them.", message
            ).group(1)
            if found in self.admins:
                self.SendChat("/tpyes")
                return
        except AttributeError:
            pass

        try:
            found = re.search(
                "(.+?) has requested to teleport to you.",
                message).group(1)
            if found in self.admins:
                self.SendChat("/tpyes")
                return
        except AttributeError:
            pass

    def SendChat(self, msg):
        """
        Send a given message to the server

        Parameters
        ----------
        msg : String
            The message to send to the server

        """
        msg = str(msg)
        if len(msg) > 0:
            packet = serverbound.play.ChatPacket()
            packet.message = msg
            self.connection.write_packet(packet)

    def ReceiveChat(self, chat_packet):
        """
        The listener for ClientboundChatPackets

        Parameters
        ----------
        chat_packet : ClientboundChatPacket
            The incoming chat packet
        chat_packet.json : JSON
            The chat packet to pass of to our Parser for handling

        """
        message = self.Parser(chat_packet.json_data)
        if not message:
            # This means our Parser failed lol
            print("Parser failed")
            return

        print(message)

    def SetServer(self, ip, port=25565, handler=None):
        """
        Sets the server, ready for connection

        Parameters
        ----------
        ip : str
            The server to connect to
        port : int, optional
            The port to connect on
        handler : Function pointer, optional
            Points to the function used to handle Clientbound chat packets

        """
        handler = handler or self.ReceiveChat

        self.ip = ip
        self.port = port
        self.connection = Connection(
            ip, port, auth_token=self.auth_token, handle_exception=print
        )

        self.connection.register_packet_listener(
            handler, clientbound.play.ChatMessagePacket
        )

        self.connection.exception_handler(print)

    def Connect(self):
        """
        Actually connect to the server for this player and maintain said connection

        Notes
        -----
        This is a blocking function and will not return until `Disconnect()` is called on said instance.

        """
        self.connection.connect()

        print(f"Connected to server with: {self.auth_token.username}")

        while True:
            time.sleep(1)
            if self.kickout:
                break

    def Disconnect(self):
        """
        In order to disconnect the client, and break the blocking loop
        this method must be called

        """
        self.kickout = True
        self.connection.disconnect()


async def Main():
    try:
        player = Player("Account Email/Username", "Account Password")
    except YggdrasilError as e:
        # Authentication Error
        print("Incorrect Login", e)
        return

    player.SetServer("Server to connect to.")

    # We do this to ensure it is non blocking as Connect() is a
    # forever loop used to maintain a connection to a server
    executor = ThreadPoolExecutor()
    executor.submit(player.Connect)

    # Forever do things unless the user wants us to logout
    while True:
        message = input("What should I do/say?\n")

        # Disconnect the client from the server before finishing everything up
        if message.lower() in ["logout", "disconnected", "exit"]:
            player.Disconnect()
            print("Disconnected")
            return

        # Send the message to the server via the player
        player.SendChat(message)


# Simply run our program
if __name__ == "__main__":
    asyncio.run(Main())
