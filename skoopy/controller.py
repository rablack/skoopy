#!/usr/env python

from skoopy.transport import TransportBluepy
from skoopy.registry import SkoobotRegistry
from pathlib import Path
from bluepy.btle import BTLEException
import time
import argparse

CMD_RIGHT = 0x10
CMD_LEFT = 0x11
CMD_FORWARD = 0x12
CMD_BACKWARD = 0x13
CMD_STOP = 0x14
CMD_SLEEP = 0x15

#    cmd_step_mode = 0x16
#    cmd_buzzer = 0x17
CMD_GET_AMBIENT = 0x21
CMD_GET_DISTANCE = 0x22
#    cmd_record = 0x30
#    cmd_increase_gain = 0x31
#    cmd_decrease_gain = 0x32
CMD_ROVER_MODE = 0x40

class SkoobotController:
    """
    Control API for Skoobots
    """

    def __init__(self):
        self.transport = TransportBluepy()
        self.registry = SkoobotRegistry()

        # Table of characteristic name to uuid mappings.
        # The characteristic names used are the ones in the firmware.
        self.uuids = {
            "cmd" : "00001525-1212-efde-1523-785feabcd123",
            "data" : "00001524-1212-efde-1523-785feabcd123",
            "byte2" : "00001526-1212-efde-1523-785feabcd123",
            "byte128" : "00001527-1212-efde-1523-785feabcd123",
            "byte4" : "00001528-1212-efde-1523-785feabcd123",
        }
        self.connectedSkoobot = None

    def connect(self, name=None, addr=None):
        """
        Connect to the given Skoobot.
        If no Skoobot is given, connects to the default.
        Returns the address of the connected Skoobot if successful;
        None otherwise.
        """
        addrList = []

        if addr != None:
            if isinstance(addr, str):
                addrList.append(addr)
            else:
                raise TypeError("addr should be a string")
        else:
            if name == None:
                name = self.registry.getDefaultName()
            elif not isinstance(name, str):
                raise TypeError("name should be a string")
            if name != None:
                skoobots = self.registry.getSkoobotsByName(name)
                addrList = [ bot[0] for bot in skoobots ]
            else:
                raise RuntimeError("No default skoobot defined")
        
            if len(addrList) == 0:
                raise ValueError("No Skoobot with name {0:s} found".format(name))

        if self.connectedSkoobot != None:
            self.disconnect()

        for botAddr in addrList:
            try:
                self.transport.connect(botAddr)
                self.connectedSkoobot = botAddr
                break
            except BTLEException:
                pass

        return self.connectedSkoobot

    def disconnect(self):
        self.transport.disconnect()
        self.connectedSkoobot = None

    def sendCommand(self, data, waitForResponse=False):
        if self.connectedSkoobot == None:
            raise RuntimeError("BLE not connected")
        data = int(data);
        cmdBytes = data.to_bytes(1, byteorder="little") 
        characteristics = self.transport.getRawCharacteristicsByUUID(self.uuids["cmd"])
        if len(characteristics) == 0:
            raise RuntimeError("cmd characteristic not supported by firmware")
        cmd = characteristics[0]
        cmd.write(cmdBytes, waitForResponse)

    def readBytes(self, charName="data"):
        """
        Read an array of bytes from the named characteristic

        returns a bytearray of the data
        """
        if self.connectedSkoobot == None:
            raise RuntimeError("BLE not connected")
        characteristics = self.transport.getRawCharacteristicsByUUID(self.uuids[charName])
        if len(characteristics) == 0:
            raise RuntimeError("{0:s} characteristic not supported by firmware".format(charName))
        charac = characteristics[0]
        dataBytes = charac.read()
        return dataBytes

    def readData(self, charName="data"):
        dataBytes = self.readBytes(charName)
        value = int.from_bytes(dataBytes, byteorder="little")
        return value

    def cmdRight(self):
       self.sendCommand(CMD_RIGHT, True)

    def cmdLeft(self):
       self.sendCommand(CMD_LEFT, True)

    def cmdForward(self):
       self.sendCommand(CMD_FORWARD, True)

    def cmdBackward(self):
       self.sendCommand(CMD_BACKWARD, True)

    def cmdStop(self):
       self.sendCommand(CMD_STOP, True)

    def cmdSleep(self):
       self.sendCommand(CMD_SLEEP, True)

    def cmdRoverMode(self):
       self.sendCommand(CMD_ROVER_MODE, True)

    def requestDistance(self):
       self.sendCommand(CMD_GET_DISTANCE, True)
       return self.readData()

    def requestAmbientLight(self):
       self.sendCommand(CMD_GET_AMBIENT, True)
       return self.readData("byte2")

class CommandParser:
    def __init__(self, controller):
        # Command table - dictionary in the form:
        #   <command> : (<args inc command>, <command object>, <command method>)
        self.commandTable = {
            "left" : (1, "controller", "Left"),
            "right" : (1, "controller", "Right"),
            "forward" : (1, "controller", "Forward"),
            "backward" : (1, "controller", "Backward"),
            "stop" : (1, "controller", "Stop"),
            "sleep" : (1, "controller", "Sleep"),
            "rover" : (1, "controller", "RoverMode"),
            "wait" : (2, "self", "Wait"),
            "test" : (1, "self", "Test"),
            "get" : (2, "self", "Get"),
            "list" : (1, "self", "List"),
            "read" : (2, "self", "Read"),
        }
        # Skoobot property table - dictionary in the form:
        #   <property> : <request method>
        self.propertyTable = {
            "distance" : "Distance",
            "ambient" : "AmbientLight",
        }
        self.controller = controller

    def parseCommandList(self, words):
        objDict = {
            "controller" : self.controller,
            "self" : self
        }
        while len(words) >= 1:
            if not isinstance(words[0], str):
                raise TypeError("words should be a list of strings")
            commandTuple = self.commandTable.get(words[0])
            if commandTuple == None:
                raise RuntimeError("Unrecognised command: {0:s}".format(words[0]))

            wordCount = commandTuple[0]

            targetObject = objDict.get(commandTuple[1])
            if targetObject == None:
                raise RuntimeError("Unrecognised command type: {0:s}".format(commandTuple[1]))
            targetMethod = getattr(targetObject, "cmd" + commandTuple[2])

            if wordCount == 1:
                targetMethod()
            else:
                args = words[1:wordCount]
                targetMethod(args)

            words = words[wordCount:]
    
    def cmdWait(self, args):
        duration = float(args[0])
        time.sleep(duration)

    def cmdTest(self):
        print("Testing...")

        print("Right")
        self.parseCommandList(["right", "wait", "1"])

        print("Left")
        self.parseCommandList(["left", "wait", "1"])

        print("Forward")
        self.parseCommandList(["forward", "wait", "1"])

        print("Backward")
        self.parseCommandList(["backward", "wait", "0.5"])

        print("Stop")
        self.parseCommandList(["stop", "wait", "1"])

        print("Sleep")
        self.parseCommandList(["sleep"])

        print("Finished testing")

    def cmdGet(self, args):
        request = self.propertyTable.get(args[0])
        if request == None:
            raise KeyError("Skoobot data property {0:s} not found.".format(args[0]))
        targetMethod = getattr(self.controller, "request" + request)
        data = targetMethod()
        print("{0:s} = {1:d}".format(args[0], data))

    def cmdList(self):
        """
        List the known characteristics
        """
        "List of known characteristics:"
        for key, value in self.controller.uuids.items():
            print("\t{0:s}\t: {1:s}".format(key, value))
        
    def cmdRead(self, args):
        """
        Read the named characteristic
        """
        if args[0] in self.controller.uuids:
            value = self.controller.readBytes(args[0])
            self.printBytes(value)
        else:
            raise RuntimeError("Unknown characteristic {0:s}".format(args[0]))

    def printBytes(self, bytes):
        """
        Print the contents of a bytearray
        """
        length = len(bytes)
        if length == 0:
            print("<empty>")
        else:
            output =[] 
            width = 16
            for i in range(0, length, 2):
                if i % width == 0 and i != 0:
                    print(" ".join(output))
                    output = []
                if i + 1 < length:
                    output.append("0x{1:02x}{0:02x}".format(bytes[i], bytes[i + 1]))
                else:
                    output.append("0x{0:02x}".format(bytes[i]))
            print(" ".join(output))

def control():
    argParser = argparse.ArgumentParser(description="Control a Skoobot")
    argParser.add_argument("--baddr", "-b", help="Skoobot bluetooth address")
    argParser.add_argument("--name", "-n", help="Skoobot name")
    # argParser.add_argument("--changedefault", "-c", action="store_true", help="Change the default Skoobot")
    # argParser.add_argument("--register", "-r", action="store_true", help="Register the Skoobot")
    argParser.add_argument("commands", nargs=argparse.REMAINDER, help="Commands to send to the Skoobot")
    args = argParser.parse_args()

    controller = SkoobotController()

    name = getattr(args, "name", None)
    baddr = getattr(args, "baddr", None)
    changeDefault = getattr(args, "changedefault", False)
    doRegister = getattr(args, "register", False)
    commandList = getattr(args, "commands", None)

    if commandList != 0:
        addr = controller.connect(name, baddr)
        if addr == None:
            print("Unable to connect to skoobot")
            exit(1)
    
        parser = CommandParser(controller)
        parser.parseCommandList(commandList)

        controller.disconnect()
    else:
        print("No commands")

if __name__ == "__main__":
    control()
