#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Intelligent lighting system for plant growth
#
# Get temperature from COM-port
# Analysis settings
# Write commands to COM-port

import os

import serial
from datetime import datetime, date, time
from time import sleep

port = "COM4"
baud = 9600
COMMAND = ""
SERIAL_PORT = None
LIGHT_PERIODS = []
FLAG = ""
LIGHT_POWER_LEVEL = 70
LIGHT_POWER = 0
SERIAL_PORT_RECONNECT_TIMEOUT = 5

def checkFlag():
    global FLAG, COMMAND, LIGHT_POWER, LIGHT_POWER_LEVEL
    ff = open("FLAG.TXT", 'r')
    FLAG = ff.read()
    ff.close()
    ret_code = 1

    if(LIGHT_POWER > (LIGHT_POWER_LEVEL+2)):
        FLAG = "ON"
        ret_code = -1
    elif(LIGHT_POWER <= (LIGHT_POWER_LEVEL)):
        FLAG = "OFF"
        ret_code = -1

    # print(LIGHT_POWER, LIGHT_POWER_LEVEL, FLAG)

    if((FLAG == "ON") & (COMMAND != "1")):
        COMMAND = "1"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif((FLAG == "OFF") & (COMMAND != "2")):
        COMMAND = "2"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif((FLAG == "ON") | (FLAG == "OFF")):
        return ret_code
    else:
        return 0

def checkTime():
    global COMMAND, SERIAL_PORT, LIGHT_PERIODS, LIGHT_POWER, LIGHT_POWER_LEVEL
    com = COMMAND
    for _hour, _minute, _command in LIGHT_PERIODS:
        if ((int(datetime.today().hour) >= int(_hour)) & (int(datetime.today().minute) >= int(_minute)) & ( _command != com)):
            com = _command
    if(com != COMMAND ):
        COMMAND = com;
        SERIAL_PORT.write(COMMAND.encode('ascii'))


def isSerialReady():
    global SERIAL_PORT
    try:
        SERIAL_PORT = serial.Serial(port, baud, timeout=1)
        if SERIAL_PORT.isOpen():
            return True
    except Exception as ex:
        print("Exeption at isSerialReady:", ex)
        return False

def getLineFromSerial():
    line = SERIAL_PORT.readline()
    line = str(line.decode("utf-8")).strip()
    if (len(line) > 0):
        return line
    else: return None

def getDataFromLine(line):
    raw_sensor_now = ""
    last_response = ""
    if (line.startswith("Recieved data")): raw_sensor_now = int(line[-3:])
    elif (line.startswith("Sent response")): last_response = int(line[-2:])
    elif (line.startswith("***")): pass
    else: print("unknown data from line"+line)
    return raw_sensor_now, last_response

def readParameters():
    global FLAG, LIGHT_POWER_LEVEL, LIGHT_PERIODS
    ret = True
    try:
        # Open a config file for reading
        file = open("FLAG.TXT", 'r')
    except IOError as e:
        # If error
        print(u'Read error: ', e)
        ret = False
        pass
    else:
        # If OK
        with file:
            FLAG = file.read()
            file.close()
            ret = ret & True
    try:
        # Open a config file for reading
        file = open("TIMES.TXT", 'r')
    except IOError as e:
        # If error
        print(u'Read error: ', e)
        ret = False
        pass
    else:
        # If OK
        with file:
            LIGHT_PERIODS = []
            line = file.readline()
            file.close()
            if(line):
                startHour, startMinute, stopHour, stopMinute, command = line.split()
                LIGHT_PERIODS.append([startHour, startMinute, stopHour, stopMinute, command])
                if (len(LIGHT_PERIODS) == 0):
                    ret = False
            ret = ret & True
    try:
        # Open a config file for reading
        file = open("LIGHT_POWER_LEVEL.TXT", 'r')
    except IOError as e:
        # If error
        print(u'Read error: ', e)
        pass
    else:
        # If OK
        with file:
            LIGHT_POWER_LEVEL = int(file.read())
            file.close()
            return ret
    return ret


def doControl(raw_sensor_now, last_response):
    global COMMAND
    COMMAND = "2"

    SERIAL_PORT.write(COMMAND.encode('ascii'))


def writeLog(log_file, raw_sensor_now, last_response):
    try:
        today = datetime.now()
        print(today, " | Sensor RAW: ", raw_sensor_now, ", response: ", last_response)
        if((datetime.hour == 0) & (datetime.minute == 0) & (datetime.second == 0)):
            log_file = 'LC-' + str(date.today()) + "-.log"
        f = open(log_file, 'a')
        if (f):
            if os.path.getsize(log_file) == 0: f.write("Date,Raw_sensor,response")
            txt_to_log = "\n"+str(today)+","+str(raw_sensor_now)+","+str(last_response)
            f.write(txt_to_log)
            f.flush()
            f.close()
    except IOError as e:
        # If error
        print(u'I/O error: ', e)

if __name__ == "__main__":
    # Проверка готовности порта
    # Check port for i/o operations
    while not isSerialReady():
        print("Serial port", port,"is not ready. Reconnect in", SERIAL_PORT_RECONNECT_TIMEOUT, "seconds")
        sleep(SERIAL_PORT_RECONNECT_TIMEOUT)
        pass

    # Основной цикл
    # Main loop
    log_file = 'LC-' + str(date.today()) + "-.log"
    while True:
        try:
            # read string data (line) from COM port
            line = getLineFromSerial()
            # get data
            if(line != None):
                print(line)
                raw_sensor_now, last_response = getDataFromLine(line)
                # read params max 3 times
                try_count = 1
                while(not readParameters()):
                    if try_count == 3: break
                    else:
                        print("Reading parameters - failed. Try No=", try_count)
                        try_count+=1
                # control lamps
                doControl(raw_sensor_now, last_response)
                writeLog(log_file, raw_sensor_now, last_response)
        except Exception as ex:
            print(ex)
            pass





