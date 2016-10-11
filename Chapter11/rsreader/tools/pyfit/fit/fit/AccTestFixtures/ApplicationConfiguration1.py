# Test Application Configuration Module
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Utilities import em

def defineConfig(options):
    return Configuration(options)

class Configuration(object):
    def __init__(self, options):
        self.labelOption = "camel"
        for option in options.appConfigurationParms:
            firstDot = option.find(".")
            if firstDot > -1:
                key = option[:firstDot]
                value = option[firstDot+1:]
                if key == "LabelMapping":
                    self.labelOption = value

    def mapLabel(self, unused='label'):
        return "force", self.labelOption

    def mapFixture(self, label):
        normalizedLabel = " ".join(label.split())
        if normalizedLabel == "check configuration":
            return "fit.AccTestFixtures.CheckConfiguration"
        elif normalizedLabel == "map label display":
            return "fit.AccTestFixtures.LabelMappingFixture"
        elif normalizedLabel == "add with custom int adapter":
            return "fit.AccTestFixtures.AppTypeAdapters.AddFixture"
        elif normalizedLabel == "check that adapters can be used":
            return "fit.AccTestFixtures.AppTypeAdapters.CheckAdapterClass"
        return None

    def mapTypeAdapter(self, adapterName):
        if adapterName == "@customInt":
            adapterPath = "fit.AccTestFixtures.AppTypeAdapters.CustomIntAdapter"
        else:
            return None

        try:
            adapter = self._import(adapterPath)
            return adapter
        except Exception:
            raise
            return None

    def _import(self, adapterPath):
        parts = adapterPath.split(".")
        head = ".".join(parts[:-1])
        tail = parts[-1]
        parts = parts[1:-1]
        mod = __import__(head)
        for part in parts:
            mod = getattr(mod, part)
        return getattr(mod, tail)

    def mapErrorMessage(self, args, unused='isExc', dummy='doTrace'):
        if args[0] == "NoTypeInfo":
            return ("Missing Metadata for '%s'. It oughta be here: '%s', and it ain't"
                    % (args[1:]))
        return None

    def AllowDefaultTypeAdapter(self):
        return True
