import string
import copy
import base64


class PacketDumper:
    options = None
    writeFile = None

    def onEnable(self, parser, pluginloader):
        parser.add_option("-d", "--dump-packets",
                          action="store_true", dest="dumpPackets", default=False,
                          help="run with this argument to dump packets")

        parser.add_option("-o", "--out-file", dest="filename", default="dump.txt",
                          help="file to dump packets to")

    def onDisable(self):
        if self.writeFile is not None:
            self.writeFile.close()

    def optionsParsed(self, parsedOptions):
        self.options = parsedOptions
        if self.options.dumpPackets:
            self.writeFile = open(self.options.filename, 'w')

    def packetReceive(self, packetID, receivedPacket):
        packet = copy.deepcopy(receivedPacket)
        if self.writeFile is not None:
            if packetID == "\x33" or packetID == "\x38":
                packet['Data'] = base64.b64encode(packet['RawData'])
                del packet['RawData']
            if packetID == "\x03":
                packet['Message'] = filter(lambda x: x in string.printable, packet['Message'])
            self.writeFile.write(hex(ord(packetID)) + " : " + str(packet) + '\n')
