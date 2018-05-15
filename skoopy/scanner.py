#!/usr/env python3

from skoopy.transport import TransportBluepy
from skoopy.registry import SkoobotRegistry
import os, shutil

def scan():
    transport = TransportBluepy()
    registry = SkoobotRegistry()

    rawDevices = transport.findRawDevices()
    for device in rawDevices:
        # print(transport.rawDeviceInfoStr(device))
        addr = device.addr
        registry.addSkoobot(addr)
        name = registry.getSkoobotsByAddress(addr)[0][1]
        if registry.getDefaultName() == None:
            registry.setDefault(name)
        defaultText = " (default)" if registry.getDefaultName() == name else ""
        msg = "Added Skoobot {0:s} to registry with name {1:s}{2:s}"
        print(msg.format(addr, name, defaultText))
    print("Saving to list of Skoobots to registry {0:s}".format(registry.registryPath))
    registry.save()
    shutil.chown(registry.registryPath, os.getlogin())

if __name__ == "__main__":
    scan()
