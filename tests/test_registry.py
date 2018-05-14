"""
Test cases for  the skoopy.registry module
"""

import unittest
import sys
import io
import os
import tempfile
import json

# If this test is being executed standalone, add '..' to the path
# to start searching for packages from the top level of the app.
if __name__ == "__main__":
    sys.path.insert(0, '..')

from skoopy.registry import SkoobotRegistry

class TestSkootbotRegistry(unittest.TestCase):
    """
    Test case for the SkoobotRegistry class
    """

    def setUp(self):
        registryFd, self.tempPath = tempfile.mkstemp(suffix=".json", prefix="skoobot_test", text=True)

        self.skooName = "TestSkoobot"
        self.skooAddr = "00:44:00:bb:55:ff"
        self.skooDupName = "DuplicateSkoobot"
        self.skooDupAddr1 = "00:00:00:00:00:01"
        self.skooDupAddr2 = "00:00:00:00:00:02"
        registryDict = {
            "default" : self.skooName,
            "skoobots" : {
                self.skooAddr : self.skooName,
                self.skooDupAddr1 : self.skooDupName,
                self.skooDupAddr2 : self.skooDupName
            }
        }
        with open(self.tempPath, "w") as registryFile:
            json.dump(registryDict, registryFile, indent=4)

        os.close(registryFd)

    def tearDown(self):
        os.remove(self.tempPath)
        
    def testConstruct(self):
        """
        Test construction with a non-existent file
        and the JSON file created during setup
        """
        with self.subTest("Empty registry"):
            emptyRegistry = SkoobotRegistry("~/nonexistent.json")
            self.assertEqual(dict(), emptyRegistry.registry)
            self.assertEqual(True, emptyRegistry.valid)
            self.assertEqual(None, emptyRegistry.getDefaultName())
    
            # Make sure that ~ in the filename was expanded
            self.assertNotIn("~", emptyRegistry.registryPath)
    
        with self.subTest("setUp() registry"):
            registry = SkoobotRegistry(self.tempPath)
            self.assertEqual(3, len(registry.registry))
            self.assertEqual(True, registry.valid)
            self.assertEqual(self.skooName, registry.getDefaultName())

    def testGetSkoobotsByName(self):
        """
        Test the getSkoobotsByName() method

        The method should return a list of (addr, name) tuples
        for all skoobots matching name
        """
        setUpRegistry = SkoobotRegistry(self.tempPath)
        names = (self.skooName, self.skooDupName, "nobody", None)
        for name in names:
            with self.subTest(name=name):
                skoobots = setUpRegistry.getSkoobotsByName(name)
                if name == self.skooDupName:
                    self.assertEqual(2, len(skoobots))
                    for skoobot in skoobots:
                        self.assertEqual(self.skooDupName, skoobot[1])
                    # Make a list of just the addresses
                    skooDupAddrs = [skoo[0] for skoo in skoobots]
                    self.assertIn(self.skooDupAddr1, skooDupAddrs)
                    self.assertIn(self.skooDupAddr2, skooDupAddrs)
                elif name == self.skooName:
                    self.assertEqual(1, len(skoobots))
                    # There is only 1 skoobot, so test it
                    skoobot = skoobots[0]
                    self.assertEqual(self.skooName, skoobot[1])
                    self.assertEqual(self.skooAddr, skoobot[0])
                else:
                    self.assertEqual(0, len(skoobots))

    def testGetSkoobotByAddress(self):
        """
        Test the getSkoobotsByAddress() method

        The method should return a list of (addr, name) tupes
        for the skoobot matching addr, if any. Addresses are unique
        so there cannot be more than one. We verify uniqueness in
        the adding tests.
        """
        registry = SkoobotRegistry(self.tempPath)
        addrs = (self.skooAddr, self.skooDupAddr1, self.skooDupAddr2, "nomatch", None)
        matchExpected = (self.skooAddr, self.skooDupAddr1, self.skooDupAddr2)
        for addr in addrs:
            expectedLen = 1 if addr in matchExpected else 0
            with self.subTest(addr=addr, expectedLen=expectedLen):
                skoobots = registry.getSkoobotsByAddress(addr)
                self.assertEqual(expectedLen, len(skoobots))
                if expectedLen == 1:
                    # There is exactly 1 skoobot in the list, so use it.
                    skoobot = skoobots[0]
                    if addr == self.skooAddr:
                        self.assertEqual(addr, skoobot[0])
                        self.assertEqual(self.skooName, skoobot[1])
                    else:
                        self.assertEqual(addr, skoobot[0])
                        self.assertEqual(self.skooDupName, skoobot[1])

    def testAddSkoobot(self):
        """
        Test addition of skoobots using the addSkoobot() method

        The method adds a skoobot to the registry using an address
        and an optional name.
        """
        registry = SkoobotRegistry(self.tempPath)
        namedAddr = "ff:ff:ff:ff:ff:ff"
        namedName = "newSkoobot"
        unnamedAddr = "ff:ff:ff:ff:ff:fe"

        with self.subTest("Add named Skoobot"):
            registry.addSkoobot(namedAddr, namedName)
            self.assertEqual(4, len(registry.registry))
            self.assertEqual(1, len(registry.getSkoobotsByAddress(namedAddr)))
            self.assertEqual(1, len(registry.getSkoobotsByName(namedName)))
            
        with self.subTest("Add unnamed Skoobot"):
            registry.addSkoobot(unnamedAddr)
            self.assertEqual(5, len(registry.registry))
            skoobots = registry.getSkoobotsByAddress(unnamedAddr)
            self.assertEqual(1, len(skoobots))
            self.assertIn(skoobots[0][1], registry.skoobotNames)

        with self.subTest("Add duplicate Skoobot"):
            # It is not defined whether this throws an exception
            # or which value ends up in the registry,
            # but it is defined that it does not result in a
            # duplicate address.
            try:
                registry.addSkoobot(namedAddr, namedName)
            except:
                pass
            self.assertEqual(5, len(registry.registry))

    def testSetDefault(self):
        """
        Test for method setDefault()

        Method sets the default name. It takes one parameter, which is either
        the address or the name.
        """
        registry = SkoobotRegistry(self.tempPath)

        registry.setDefault(self.skooDupName)
        self.assertEqual(self.skooDupName, registry.getDefaultName())
        
        registry.setDefault(self.skooAddr)
        self.assertEqual(self.skooName, registry.getDefaultName())

        registry.setDefault(self.skooDupAddr1)
        self.assertEqual(self.skooDupName, registry.getDefaultName())

    def testGetDefaultName(self):
        """
        Test for method getDefaultName()

        Method gets the default name.
        """
        registry = SkoobotRegistry(self.tempPath)
        self.assertEqual(self.skooName, registry.getDefaultName())

if __name__ == "__main__":
    unittest.main()
