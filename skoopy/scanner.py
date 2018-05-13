#!/usr/env python3

from transport import TransportBluepy

def scan():
    transport = TransportBluepy()

    rawDevices = transport.findRawDevices()
    for device in rawDevices:
        print(transport.rawDeviceInfoStr(device))

if __name__ == "__main__":
    scan()
