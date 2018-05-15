"""
Skoobot registry management
"""

import os.path
import json
import random
import platform

class SkoobotRegistry:
    """
    A register of Skoobots, backed by a JSON file
    """
    def __init__(self, registryPath=None, debug=False):
        """
        Construct a Skoobot registry and load it from its file.
        If the file does not yet exist, an empty registry will be created.
        A file will not be created until the save() method is called.
        """
        self.debug = debug
        if self.debug:
            print("SkoobotRegistry: debug on")
        if registryPath == None:
            if platform.system() == "Windows":
                registryPath = "~/skoobot.json"
            else:
                # We need to use the logname instead of the user name
                # in case this is run from sudo
                logname = os.getlogin()
                registryPath = "~{0:s}/.skoobots.json".format(logname)
        self.registryPath = os.path.expanduser(registryPath)
        self.valid = True
        if os.path.isfile(self.registryPath):
            self.load()
        else:
            if self.debug:
                print("No readable file")
            self.registry = {}
            self.default = None

        self.skoobotNames = set((
            "alice",
            "bob",
            "carol",
            "david",
            "eve",
            "frank",
            "grace",
            "heidi",
            "ivor",
            "judy",
            "ken",
            "lucy",
            "mallory",
            "niaj",
            "oscar",
            "peggy",
            "quentin",
            "rachael",
            "sybil",
            "ted",
            "ursula",
            "victor",
            "walter",
            "xander",
            "yvonne",
            "zach"))


    def getSkoobotsByName(self, name):
        """
        Find Skoobots by name. Normally this will return a list
        with 0 or 1 elements, unless two Skoobots have been
        given the same name.
        """
        skoobotList = []
        for addr, skooName in self.registry.items():
            if skooName == name:
                skoobotList.append((addr, skooName))
        return skoobotList

    def getSkoobotsByAddress(self, address):
        """
        Find Skoobots by address. Since the BLE address is unqiue,
        this should always return a list with 0 or 1 elements
        """
        skoobotList = []
        name = self.registry.get(address)
        if name != None:
            skoobotList.append((address, name))
        return skoobotList

    def addSkoobot(self, addr, name=None, replace=True):
        """
        Add a Skoobot to the registry.
        If a name is not provided, a unique name will be generated.
        If an entry exists, a name is provided and replace=False then
        a TypeError exception will be generated.
        NB: If the name is specified, there is no requirement for the
        name to be unique.  However, it is strongly recommended.
        """
        # Validate inputs
        if not isinstance(addr, str):
            raise TypeError("Invalid addr : must be a string.")
        if name != None and not isinstance(name, str):
            raise TypeError("Invalid name : must be a string.")
        if name != None and replace == False:
            if self.registry.get(addr, name) != name:
                raise RuntimeError("Duplicate skoobot with conflicting name")

        if name == None:
            # Use the existing name if it exists
            name = self.registry.get(addr)
            if name == None:
                name = self.generateName()

        self.registry[addr] = name

    def setDefault(self, nameAddr):
        """
        Set the default Skoobot. This may be by address or name.
        NB: The registry stores the name. However, here is no requirement
        for the name to be unique.
        """
        if nameAddr != None and not isinstance(nameAddr, str):
            raise TypeError("nameAddr is not a String or None")
        if nameAddr in self.registry:
            nameAddr = self.registry[nameAddr]
        if nameAddr != None and not nameAddr in self.registry.values():
            raise ValueError("Default value does not match a Skoobot in the registry")
        self.default = nameAddr

    def getDefaultName(self):
        """
        Return the default Skoobot name.
        NB: It is not an error for there to be multiple Skoobots
        with this name.
        """
        return self.default

    def load(self):
        """
        Load the registry from self.registryPath
        If the registry file is missing, create an empty registry
        If the registry file is not valid, mark the registry as not valid
        and raise an Exception
        """
        if self.debug:
            print("Loading")
        try:
            with open(self.registryPath, "r") as registryFile:
                registryDict = json.load(registryFile)
            self.registry = registryDict.get("skoobots", {})
            self.default = None
            newDefault = registryDict.get("default", None)
            if newDefault in self.registry.values():
                self.default = newDefault
            self.valid = True
        except:
            if self.debug:
               print("load(): exception")
            self.registry = {}
            self.default = None
            self.valid = False
            raise

    def save(self):
        """
        Save the registry to self.registryPath
        If the registry is invalid, do nothing
        """
        if self.valid:
            registryDict = { "default" : self.default, "skoobots" : self.registry }
            with open(self.registryPath, "w") as registryFile:
                json.dump(registryDict, registryFile, sort_keys=True, indent=4)

    def generateName(self):
        """
        Generate a Skoobot name that does not exist in the registry
        """
        namesUsed = set(self.registry.values())
        namesAvailable = self.skoobotNames - namesUsed
        if len(namesAvailable) == 0:
            raise KeyError("Run out of skoobot names")
        return random.sample(namesAvailable, 1)[0]
        
