import pkgutil
import plugins
import imp
import importlib
import sys
import plugin

class pluginLoader:
    def __init__(self):
        self.availablePlugins = {}
        self.__loadPlugins(plugins.__path__[0])

    def __loadPlugins(self, path):
        # Iterate over each plugin
        for loader, name, ispkg in pkgutil.iter_modules([path]):
            file, pathname, desc = imp.find_module(name, [path])
            # Source the plugin
            pluginModule = imp.load_source(name, pathname)
            pluginClass = getattr(pluginModule, name)
            # Store the instance
            self.availablePlugins[name] = pluginClass

    def getPluginInstance(self, site):
       if site in  self.availablePlugins:
           return self.availablePlugins[site]

