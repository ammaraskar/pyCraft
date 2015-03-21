pyCraft
====

Minecraft Python Client!

http://pycraft.readthedocs.org/en/latest/

When running start.py, make sure you duck.

#Requirements
- pyCrypto 2.5 (Also in requirements.txt)

##PyCrypto on Windows Systems (32 bit)
If you use Python 2.7 with win32 you're in luck, theres an installer right [here](http://www.secker.nl/wp-content/uploads/2012/03/pycrypto-2.5.win32-py2.7.exe) for pyCrypto 2.5
otherwise you're gonna need to compile it, followed by some fancy instructions on how to install pyCrypto over [here](http://www.secker.nl/2012/03/08/building-pycrypto-2-5-using-mingw-and-python-2-7-on-windows-xp/)

----------

On linux you'll need the `build-essential` and `python-dev` packages after which running `pip install -r requirements.txt`, should pull everything in.

Eventually we'll put some run instructions here but `start.py --help` should cover everything for now

#Writing Plugins for pyCraft
pyCraft has some basic plugin support, as a developer making plugins is a simple process. In the plugins folder, simply create a .py file with your plugin's name as the file name.
In your plugin.py file define a single class with the exact same spellings as your plugin file name. Now within your plugin class you'll be notified using certain methods when
things happen in the minecraft world. See the [PacketDumper plugin](https://github.com/ammaraskar/pyCraft/blob/master/plugins/PacketDumper.py) as an example. Currently these methods are
used:

```onEnable(self, parser, pluginloader)``` This fires when your plugin is loaded and passes the option parser as an argument allowing you to add custom command line options

```onDisable(self)``` This fires when pyCraft is exited cleanly, use it for cleaning up

```optionsParsed(self, parsedOptions)``` This fires when command line options have been parsed allowing you to get information from any parameters you may have added in onEnable

```packetReceive(self, packetID, receivedPacket)``` This fires when pyCraft's networking core receives a packet
