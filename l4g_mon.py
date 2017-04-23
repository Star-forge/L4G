#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
from datetime import datetime, date, time

port = "COM2"
baud = 9600
COMMAND = ""
SERIAL_PORT = None
LIGHT_PERIODS = [[6, 0, "1"], [7, 0, "2"], [20, 0, "1"], [22, 0, "2"], [0, 0, "2"]]
FLAG = ""
LIGHT_POWER_LEVEL_MIN = 65
LIGHT_POWER_LEVEL_MAX = 103
LIGHT_POWER = 0
# Average LIGHT_POWER - of last 5 datas
LIGHT_POWER_AVG = 0
LIGHT_POWER_AVG_LIST = []


def getAVG_LIGHT_POWER():
    global LIGHT_POWER_AVG, LIGHT_POWER_AVG_LIST, LIGHT_POWER
    while (len(LIGHT_POWER_AVG_LIST) < 6):
        LIGHT_POWER_AVG_LIST.append(LIGHT_POWER)
    LIGHT_POWER_AVG_LIST.pop(0)

    lp_avg = 0
    for lp in LIGHT_POWER_AVG_LIST:
        lp_avg += lp
    LIGHT_POWER_AVG = int(lp_avg / 5)
    # print("LIGHT_POWER_AVG =",LIGHT_POWER_AVG)


def checkFlag():
    global FLAG, COMMAND, LIGHT_POWER, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX
    ff = open("FLAG.TXT", 'r')
    FLAG = ff.read()
    ff.close()
    ret_code = 1

    ff = open("LIGHT_POWER_LEVEL.TXT", 'r')
    Light_power_levels = ff.read()
    Light_power_level_min, Light_power_level_max = Light_power_levels.split("-")
    LIGHT_POWER_LEVEL_MIN = int(Light_power_level_min)
    LIGHT_POWER_LEVEL_MAX = int(Light_power_level_max)
    ff.close()

    if ((LIGHT_POWER_LEVEL_MAX > LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MIN) & (FLAG != "ON")):
        ff = open("FLAG.TXT", 'w')
        ff.write("ON")
        FLAG = "ON"
        ff.close()
    elif (((LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MAX + 2) | (LIGHT_POWER_AVG < LIGHT_POWER_LEVEL_MIN - 2)) & (
        FLAG != "OFF")):
        ff = open("FLAG.TXT", 'w')
        ff.write("OFF")
        FLAG = "OFF"
        ff.close()
    # ret_code = -1
    # elif(LIGHT_POWER <= (LIGHT_POWER_LEVEL)):
    #     FLAG = "OFF"
    #     ret_code = -1

    # print(LIGHT_POWER, LIGHT_POWER_LEVEL, FLAG)

    if ((FLAG == "ON") & (COMMAND != "1")):
        COMMAND = "1"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif ((FLAG == "OFF") & (COMMAND != "2")):
        COMMAND = "2"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif ((FLAG == "ON") | (FLAG == "OFF")):
        return ret_code
    else:
        return 0


def checkTime():
    global COMMAND, SERIAL_PORT, LIGHT_PERIODS, LIGHT_POWER, LIGHT_POWER_LEVEL
    com = COMMAND
    for _hour, _minute, _command in LIGHT_PERIODS:
        if ((int(datetime.today().hour) >= int(_hour)) & (int(datetime.today().minute) >= int(_minute)) & (
            _command != com)):
            com = _command
    if (com != COMMAND):
        COMMAND = com;
        SERIAL_PORT.write(COMMAND.encode('ascii'))


if __name__ == "__main__":
    _str = ""
    COMMAND = "2"
    SERIAL_PORT = serial.Serial(port, baud, timeout=1)
    # open the serial port
    if SERIAL_PORT.isOpen():
        filename = 'svet' + str(date.today()) + ".log"

        print(SERIAL_PORT.name + ' is open...')
        SERIAL_PORT.write(COMMAND.encode('ascii'))
    while True:
        try:
            line = SERIAL_PORT.readline()
            today = datetime.now()
            _str = str(line.decode("utf-8")).strip()
            if ((len(_str) > 0) & (_str.startswith("data"))):
                lp, resp = _str.split()
                LIGHT_POWER = int(lp[4:])
                getAVG_LIGHT_POWER()
                _str = str(today) + "," + str(LIGHT_POWER) + "," + str(resp)
                print(today, " lp =", LIGHT_POWER, " resp =", resp)
                if datetime.hour == datetime.minute == datetime.second == 0:
                    filename = 'svet' + str(date.today()) + ".log"
                f = open(filename, 'a')
                if (f):
                    f.write("\n" + _str)
                    f.flush()
                    f.close()
                else:
                    print("File Error")
            elif (len(_str) > 0):
                print(today, _str)

            if (checkFlag() == 0):
                checkTime()
                # elif(checkFlag() == -1):
                #     checkTime()


        except OSError:
            print('cannot open')



