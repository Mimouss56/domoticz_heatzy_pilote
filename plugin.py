#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic Python Plugin Example
#
# Author: Xorfor
#
"""
<plugin key="heatzy_pilote" name="Heatzy pilote" author="Mimouss" version="0.0.1">
    <params>
        <!--
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="30px" required="true" default="80"/>
        -->
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
        <param field="Username" label="Heatzy user / email" width="200px" required="true" default=""/>
        <param field="Password" label="Heatzy password" width="200px" required="true" default=""/>
    </params>
</plugin>
"""
import Domoticz
import json
import http.client
import calendar
import time


class BasePlugin:

    __HEARTBEATS1MIN = 3
    __MINUTES = 1         # or use a parameter

    #__STATE_COMFORT = '舒适'
    #__STATE_ECO = '经济'
    #__STATE_FREEZE = '解冻'
    #__STATE_OFF = '停止'

    __STATE_COMFORT = 'cft'
    __STATE_ECO = 'eco'
    __STATE_FREEZE = 'fro'
    __STATE_OFF = 'off'

    __COMMAND_COMFORT = { "mode":0  }
    __COMMAND_ECO = { "mode":1 }
    __COMMAND_FREEZE = { "mode":2 }
    __COMMAND_OFF = { "mode":3 }


    __API_HOST = 'euapi.gizwits.com'
    __HEATZY_APPLICATION_ID = 'c70a66ff039d41b4a220e198b0fcc8b3'
    __HEATZY_PILOT_PRODUCT_KEY = '9420ae048da545c88fc6274d204dd25f'

    __UNIT_STATE = 1


    # Device units
    # __UNIT_TEXT = 1

    def __init__(self):
        self.__runAgain = 0
        self.token = None
        self.token_expire = -1


    def get_token(self):
        ts = calendar.timegm(time.gmtime())
        if self.token == None or ts - self.token_expire < 100:
            params = json.dumps({'username': Parameters["Username"], 'password': Parameters["Password"], 'lang': 'en'})
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Gizwits-Application-Id": "c70a66ff039d41b4a220e198b0fcc8b3"
            }
            conn = http.client.HTTPSConnection(self.__API_HOST)
            conn.request("POST", "/app/login", params, headers)
            response = conn.getresponse()
            data = response.read()

            self.token = json.loads(data.decode("utf-8"))['token']

            conn.close()

        return self.token

    def get_devices(self):
        headers = {
            "Accept": "application/json",
            "X-Gizwits-Application-Id": "c70a66ff039d41b4a220e198b0fcc8b3",
            "X-Gizwits-User-token": self.get_token()
        }
        conn = http.client.HTTPSConnection(self.__API_HOST)
        conn.request("GET", "/app/bindings", headers=headers)
        response = conn.getresponse()
        data = response.read()
        devices = json.loads(data.decode("utf-8"))
        conn.close()
        return devices["devices"]

    def get_status(self, did):
        headers = {
            "Accept": "application/json",
            "X-Gizwits-Application-Id": "c70a66ff039d41b4a220e198b0fcc8b3",
            "X-Gizwits-User-token": self.get_token()
        }
        conn = http.client.HTTPSConnection(self.__API_HOST)
        conn.request("GET", "/app/devdata/{0}/latest".format(did), headers=headers)
        response = conn.getresponse()
        data = response.read()
        status = json.loads(data.decode("utf-8"))
        conn.close()
        return status["attr"]["mode"]


    def control(self, did, mode):
        params = json.dumps({"attrs": mode})
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Gizwits-Application-Id": "c70a66ff039d41b4a220e198b0fcc8b3",
            "X-Gizwits-User-token": self.get_token()
        }

        conn = http.client.HTTPSConnection(self.__API_HOST)
        conn.request("POST", "/app/control/" + did, params, headers)
        response = conn.getresponse()
        return response.code == 200

    def get_unit(self, units):
        unit = 1
        while True:
            if unit in units:
                unit +=1
            else:
                units.append(unit)
                return unit

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()

        Options = {"LevelActions": "||||",
                       "LevelNames": "Off|Hors gel|Eco|Confort",
                       "LevelOffHidden": "false",
                       "SelectorStyle": "0"}
        domoticz_already_installed = []
        domoticz_already_installed_units = []
        for domoticz_device in Devices:
            domoticz_already_installed.append(Devices[domoticz_device].DeviceID)
            domoticz_already_installed_units.append(Devices[domoticz_device].ID)
        for device in self.get_devices():
            if device['did'] not in domoticz_already_installed:
                Domoticz.Device(Name=device['dev_alias'], Unit=self.get_unit(domoticz_already_installed_units), DeviceID=device['did'],
                                TypeName="Selector Switch", Options=Options, Switchtype=18, Image=15).Create()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        j = json.loads(Data['Data'].decode("utf-8", "ignore"))
        if "token" in j.keys():
            self.token = j['token']

    def find_unit(self, device_id, except_id):
        for device in Devices:
            if Devices[device].DeviceID == device_id and Devices[device].ID != except_id:
                return Devices[device].ID
        return None

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug(Devices[1].DeviceID +
            " onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        if str(Command) == 'Set Level':
            if Level == 0:
                self.control(Devices[Unit].DeviceID, self.__COMMAND_OFF)
                UpdateDevice(Unit, 1, '0')
            elif Level == 10:
                self.control(Devices[Unit].DeviceID, self.__COMMAND_FREEZE)
                UpdateDevice(Unit, 1, '10')
            elif Level == 20:
                self.control(Devices[Unit].DeviceID, self.__COMMAND_ECO)
                UpdateDevice(Unit, 1, '20')
            elif Level == 30:
                self.control(Devices[Unit].DeviceID, self.__COMMAND_COMFORT)
                UpdateDevice(Unit, 1, '30')

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS1MIN * self.__MINUTES
            already = []
            for domoticz_device in Devices:
                if Devices[domoticz_device].ID not in already:
                    status = self.get_status(Devices[domoticz_device].DeviceID)
                    on_off = self.find_unit(Devices[domoticz_device].DeviceID, Devices[domoticz_device].ID)
                    already.append(on_off)
                    if status == self.__STATE_OFF:
                        UpdateDevice(domoticz_device, 0, '0')
                        #UpdateDevice(on_off, 0, 'Off')
                    elif status == self.__STATE_FREEZE:
                        UpdateDevice(domoticz_device, 1, '10')
                        #UpdateDevice(on_off, 0, 'Off')
                    elif status == self.__STATE_ECO:
                        UpdateDevice(domoticz_device, 1, '20')
                        #UpdateDevice(on_off, 0, 'Off')
                    elif status == self.__STATE_COMFORT:
                        UpdateDevice(domoticz_device, 1, '30')
                        #UpdateDevice(on_off, 1, 'On')
        else:
            Domoticz.Debug("onHeartbeat called, run again in " + str(self.__runAgain) + " heartbeats.")


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
    # Show parameters
    Domoticz.Debug("Parameters count.....: " + str(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
           Domoticz.Debug("Parameter '" + x + "'...: '" + str(Parameters[x]) + "'")
    # Show settings
        Domoticz.Debug("Settings count...: " + str(len(Settings)))
    for x in Settings:
       Domoticz.Debug("Setting '" + x + "'...: '" + str(Settings[x]) + "'")
    # Show images
    Domoticz.Debug("Image count..........: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("Image '" + x + "...': '" + str(Images[x]) + "'")
    # Show devices
    Domoticz.Debug("Device count.........: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device...............: " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device Idx...........: " + str(Devices[x].ID))
        Domoticz.Debug("Device Type..........: " + str(Devices[x].Type) + " / " + str(Devices[x].SubType))
        Domoticz.Debug("Device Name..........: '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue........: " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device Options.......: '" + str(Devices[x].Options) + "'")
        Domoticz.Debug("Device Used..........: " + str(Devices[x].Used))
        Domoticz.Debug("Device ID............: '" + str(Devices[x].DeviceID) + "'")
        Domoticz.Debug("Device LastLevel.....: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: " + str(Devices[x].Image))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")

def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, Options=Options)
            Domoticz.Debug("Device Options update: " + Devices[Unit].Name + " = " + str(Options))

def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, Image=Images[Image].ID)
            Domoticz.Debug("Device Image update: " + Devices[Unit].Name + " = " + str(Images[Image].ID))

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")
