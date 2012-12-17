import os
import imp

class PluginLoader():
    
    path = ""
    plugins = []
    listeners = []
    
    def __init__(self, path):
        self.path = path
        

    def loadPlugins(self, parser):
        for root, dirs, files in os.walk(self.path):
            for source in (s for s in files if s.endswith(".py")):
                name = os.path.splitext(os.path.basename(source))[0]
                full_name = os.path.splitext(source)[0].replace(os.path.sep, '.')
                m = imp.load_module(full_name, *imp.find_module(name, [root]))

                pluginClass = None
                try:
                    pluginClass = getattr(m, name)()
                    self.plugins.append(pluginClass)
                    try:
                        pluginClass.onEnable(parser)
                    except AttributeError:
                        pass
                    try:
                        self.listeners.append(pluginClass.packetReceive)
                    except AttributeError:
                        pass
                except AttributeError:
                    print "Plugin " + name + " is malformed"
                    
    def disablePlugins(self):
        for plugin in self.plugins:
            try:
                plugin.onDisable()
            except AttributeError:
                pass
                    
    def notifyOptions(self, options):
        for plugin in self.plugins:
            try:
                plugin.optionsParsed(options)
            except AttributeError:
                pass
                    
    def getPlugins(self):
        return self.plugins
    
    def getPacketListeners(self):
        return self.listeners
