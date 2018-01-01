# MAC address presence Python Plugin
#
# Author: Xorfor
#
# MAC addresses in de format xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx

"""
<plugin key="xrf_macpresence" name="MAC address presence" author="Xorfor" version="2.0.0" externallink="https://github.com/Xorfor/Domoticz/tree/master/plugins/macpresence">
    <params>
        <param field="Address" label="MAC addresses" width="1000px" required="true"/>
        <param field="Mode1" label="Minutes between check" width="100px" required="true" default="1"/>
        <param field="Mode2" label="Minutes for timeout" width="100px" required="true" default="10"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import platform
import os


class BasePlugin:

    __MINUTE = 6
    __UNIT = 1

    def __init__(self):
        self.__platform = platform.system()
        self.__addresses = {}
        self.__timeouts = {}
        self.__heartbeat = 1
        self.__timeout = 1
        self.__runAgain = 0
        self.__config_ok = False
        self.__COMMAND = ""
        self.__OPTIONS = ""
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        # Debug
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)
        # Validate parameters
        Domoticz.Debug("Platform: "+self.__platform)
        if self.__platform == "Linux":
            self.__COMMAND = "arp-scan"
            self.__OPTIONS = "-lq"
            ret = os.popen("dpkg -l | grep " + self.__COMMAND).read()
            pos = ret.find(self.__COMMAND)
            if pos >= 0:
                self.__config_ok = True
                self.__COMMAND = "sudo " + self.__COMMAND
            else:
                Domoticz.Error(self.__COMMAND + " not found")
                return
        elif self.__platform == "Windows":
            # Not implemented yet
            pass
        Domoticz.Debug("Command: " + self.__COMMAND + " " + self.__OPTIONS)

        # Check parameter for heartbeat. Default is 1. Check every 1 minute for the presence of the defined mac addresses
        self.__heartbeat = int(Parameters["Mode1"])
        if self.__heartbeat < 1:
            self.__heartbeat = 1

        # Check parameter for timeout. Default is 10, minimum is 5. After absence of the mac address for 10 minutes, then switch off
        self.__timeout = int(Parameters["Mode2"])
        if self.__timeout < 1:
            self.__timeout = 5

        # Initialize all defined devices
        macList = Parameters["Address"].split(",")
        numDevices = 0
        for macItem in macList:
            numDevices += 1
            self.__addresses[numDevices] = macItem.lower().strip().replace("-", ":")
            self.__timeouts[numDevices] = self.__timeout
        Domoticz.Debug("Number of mac items: "+str(numDevices))
        if self.__UNIT not in Devices:
            Domoticz.Device(Unit=self.__UNIT, Name="MAC Presence", TypeName="Switch", Image=18, Used=1).Create()
        DumpConfigToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if not self.__config_ok:
            return
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            found = False
            # Scan for mac addresses in the network
            ret = os.popen(self.__COMMAND + " " + self.__OPTIONS).read().lower()
            for i in range(len(self.__addresses)):
                num = i + 1
                Domoticz.Debug("num    : " + str(num))
                Domoticz.Debug("address: '" + self.__addresses[num] + "'")
                pos = ret.find(self.__addresses[num])
                Domoticz.Debug("pos: "+str(pos))
                if pos >= 0:
                    Domoticz.Debug("address: " + self.__addresses[num] + " found. Timeout: " + str(self.__timeout))
                    found = True
                    self.__timeouts[num] = self.__timeout
                else:
                    # Device not found
                    self.__timeouts[num] -= 1
                    if self.__timeouts[num] > 0:
                        # Device not timed out yet
                        Domoticz.Debug("address: " + self.__addresses[num] + " not timed out yet: "+str(self.__timeouts[num]))
                        found = True
            if found:
                Domoticz.Debug("An address found or not timed out yet")
                UpdateDevice(self.__UNIT, 1, "On")
            else:
                Domoticz.Debug("No addresses found")
                UpdateDevice(self.__UNIT, 0, "Off")

            self.__runAgain = self.__MINUTE*self.__heartbeat

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    for x in Settings:
        Domoticz.Debug("Setting:           " + str(x) + " - " + str(Settings[x]))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
