import string
import copy

class PacketDumper:
    options = None
    writeFile = None

    def onEnable(self, parser):
        parser.add_option("-d", "--dump-packets",
            action="store_true", dest="dumpPackets", default=False,
            help="run with this argument to dump packets")

        parser.add_option("-o", "--out-file", dest="filename", default="dump.txt",
            help="file to dump packets to")

    def onDisable(self):
        if (self.writeFile != None):
            self.writeFile.close()

    def optionsParsed(self, parsedOptions):
        self.options = parsedOptions
        if (self.options.dumpPackets):
            self.writeFile = open(self.options.filename, 'w')

    def packetReceive(self, packetID, receivedPacket):
        packet = copy.deepcopy(receivedPacket)
        if (self.writeFile != None):
            if (packetID == "\x33" or packetID == "\x38"):
                packet = {'ChunkPlaceHolder': 0}
            if (packetID == "\x03"):
                packet['Message'] = filter(lambda x: x in string.printable, packet['Message'])
            self.writeFile.write(hex(ord(packetID)) + " : " + str(packet) + '\n')
    
    