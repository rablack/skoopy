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

        self.skooName = "testSkoo"
        self.skooAddr = "00:44:00:bb:55:ff"
        registryDict = {
            "default" : self.skooName,
            "skoobots" : {
                self.skooAddr : self.skooName
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
            self.assertEqual(1, len(registry.registry))
            self.assertEqual(True, registry.valid)
            self.assertEqual(self.skooName, registry.getDefaultName())
    
if __name__ == "__main__":
    unittest.main()
