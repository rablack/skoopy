"""
Transport interface for skoopy

Abstracts interface to bluetooth library.
In theory this should allow for multiple bluetooth libraries
in the future.
"""

import bluepy
from bluepy.btle import Scanner

class TransportBluepy():
    def __init__(self):
        self.devices = []
        self.peripheral = None

    def findRawDevices(self, timeout=1.0):
        rawDevices = []
        scanner = Scanner()
        rawDevices = scanner.scan(timeout)

        return rawDevices

    def rawDeviceInfoStr(self, rawDevice):
        """
        Convert the raw device into an info string.

        The format of the string is transport-specific.
        """
        info = "Address: {0:s}\n".format(rawDevice.addr)
        info += "Address type: {0:s}\n".format("public" if rawDevice.addrType == bluepy.btle.ADDR_TYPE_PUBLIC else "random")
        info += "Connections?: {0:s}\n".format("yes" if rawDevice.connectable else "no")
        info += "Scan Data:\n"
        scanData = rawDevice.getScanData()
        for scanRow in scanData:
            info += "    {0:d}\t| {1:s}\t| {2:s}\n".format(scanRow[0], scanRow[1], scanRow[2])
        
        return info

