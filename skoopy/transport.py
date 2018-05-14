"""
Transport interface for skoopy

Abstracts interface to bluetooth library.
In theory this should allow for multiple bluetooth libraries
in the future.
"""

import bluepy
import uuid
from bluepy.btle import Scanner, Peripheral, Characteristic

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
        if rawDevice.connectable:
            self.connect(rawDevice.addr, rawDevice.addrType)
            info += "Services:\n"
            rawServices = self.getRawServices()
            for rawService in rawServices:
                info += "{0:s}".format(self.rawServiceInfoStr(rawService))
            self.disconnect()
        
        return info

    def rawServiceInfoStr(self, rawService):
        info = "    UUID: {0:s}\n".format(str(rawService.uuid))
        info += "    Characteristics:\n"
        rawCharacteristics = self.getRawCharacteristicsForService(rawService) 
        for rawCharacteristic in rawCharacteristics:
            info += "{0:s}".format(self.rawCharacteristicInfoStr(rawCharacteristic))
        return info

    def rawCharacteristicInfoStr(self, rawCharacteristic):
        info = "    -   UUID: {0:s}\n".format(str(rawCharacteristic.uuid))
        info += "    -   Handle: {0:d} (0x{0:x})\n".format(rawCharacteristic.getHandle())
        info += "    -   Properties: {0:s}\n".format(rawCharacteristic.propertiesToString())
        return info
        
    def connect(self, addr, addrType=bluepy.btle.ADDR_TYPE_RANDOM):
        self.disconnect()
        self.peripheral = Peripheral(addr, addrType)
        
    def disconnect(self):
        if self.peripheral != None:
            self.peripheral.disconnect()
            self.peripheral = None

    def getRawServices(self):
        if self.peripheral == None:
            print("Not connected.\n")
            return {}
        rawServices = self.peripheral.getServices()
        print("Found {0:d} services\n".format(len(rawServices)))
        return rawServices

    def getRawCharacteristicsForService(self, service):
        return service.getCharacteristics()

    def getRawCharacteristicsByUUID(self, uuid):
        results = []
        if self.peripheral != None:
            results = self.peripheral.getCharacteristics(uuid=uuid)
        return results
