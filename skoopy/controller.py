#!/usr/env python3

from skoopy.transport import TransportBluepy
from pathlib import Path
import time

skoobot_file_path = Path(Path.home(), ".skoobots")

transport = TransportBluepy()

cmdUUID = "00001525-1212-efde-1523-785feabcd123"
dataUUID = "00001524-1212-efde-1523-785feabcd123"

bleAddrList = []
try:
    with skoobot_file_path.open("r") as skoobot_file:
        for line in skoobot_file:
            bleAddrList.append(line.strip())
except FileNotFoundError:
    print("Skoobot address file not found: {0:s}".format(str(skoobot_file_path)))
    exit(1)

bleAddr = bleAddrList[0]

#class SkooController:
#    def __init__(self):
        

cmd_right = 0x10
cmd_left = 0x11
cmd_forward = 0x12
cmd_backward = 0x13
cmd_stop = 0x14
cmd_sleep = 0x15
cmd_step_mode = 0x16
cmd_buzzer = 0x17
cmd_get_ambient = 0x21
cmd_get_distance = 0x22
cmd_record = 0x30
cmd_increase_gain = 0x31
cmd_decrease_gain = 0x32
cmd_rover_mode = 0x40

print("Attempting to contact Skoobot at '{0:s}'".format(bleAddr))

transport.connect(bleAddr)
cmdList = transport.getRawCharacteristicsByUUID(cmdUUID)
if len(cmdList) == 0:
    print("No command characteristic found\n")
    exit(1)

cmd = cmdList[0]

cmdData = bytearray(1)

print("Right")
cmdData[0] = cmd_right
cmd.write(cmdData, False)
time.sleep(1)

print("Left")
cmdData[0] = cmd_left
cmd.write(cmdData, False)
time.sleep(1)

print("Sleep")
cmdData[0] = cmd_sleep
cmd.write(cmdData, False)
time.sleep(1)

transport.disconnect()
print("Done")
